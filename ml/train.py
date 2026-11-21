"""Stage 3: train a small U-Net to predict where the exact shortest path runs.

Input  (3 channels): obstacles, start cell, goal cell.
Output (1 channel) : for every cell, the chance that the shortest path passes through it.

    python -m ml.train --epochs 1 --name smoke        # quick test (a few minutes)
    python -m ml.train --epochs 40 --name unet_v1     # the real run

Everything lands in ``runs/<name>/``: ``last.pt`` (saved every epoch, so a stopped
run continues from where it was when you run the same command again), ``best.pt``
(lowest validation loss), ``log.csv``, TensorBoard logs and ``predictions.png``.

Validation is the last 5% of the dataset (by seed); those maps are never trained on.
Each epoch also reports how useful the prediction is as a corridor for a planner:
  coverage  = share of true path cells inside the predicted corridor
  connected = share of maps where the corridor links start and goal through free cells
  corridor  = corridor size as a share of the free cells (smaller = more focused)
"""

import argparse
import csv
import glob
import math
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage


# ---------------------------------------------------------------- data

def load_dataset(dirname):
    files = sorted(glob.glob(os.path.join(dirname, "shard_*.npz")))
    if not files:
        raise SystemExit(f"no shard_*.npz files in {dirname}")
    grid, mask, start, goal, seed = [], [], [], [], []
    for f in files:
        with np.load(f) as d:
            grid.append(d["grid"])
            mask.append(d["mask"])
            start.append(d["start"])
            goal.append(d["goal"])
            seed.append(d["seed"])
    order = np.argsort(np.concatenate(seed))
    cat = lambda xs: np.concatenate(xs)[order]  # noqa: E731
    return cat(grid), cat(mask), cat(start).astype(np.int64), cat(goal).astype(np.int64)


def make_input(grid, start, goal):
    """(B, H, W) obstacle grid + (B, 2) start/goal as (x, y) -> (B, 3, H, W) float tensor."""
    b = grid.shape[0]
    x = torch.zeros((b, 3, grid.shape[1], grid.shape[2]), device=grid.device)
    x[:, 0] = grid.float()
    i = torch.arange(b, device=grid.device)
    x[i, 1, start[:, 1], start[:, 0]] = 1.0
    x[i, 2, goal[:, 1], goal[:, 0]] = 1.0
    return x


def augment(x, y):
    """Same random rotation (0/90/180/270) and mirror for inputs and labels; paths stay valid."""
    k = int(torch.randint(0, 4, (1,)))
    x, y = torch.rot90(x, k, (2, 3)), torch.rot90(y, k, (2, 3))
    if torch.rand(1) < 0.5:
        x, y = torch.flip(x, (3,)), torch.flip(y, (3,))
    return x, y


# ---------------------------------------------------------------- model

class Block(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
            nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True))

    def forward(self, x):
        return self.net(x)


class UNet(nn.Module):
    """Plain U-Net with 3 down/up steps. Works on any map size (pads to a multiple of 8,
    with the padding marked as obstacle), so a model trained on 50x50 also runs on 100x100."""

    def __init__(self, cin=3, base=32):
        super().__init__()
        c = [base, base * 2, base * 4, base * 8]
        self.d0, self.d1, self.d2, self.mid = Block(cin, c[0]), Block(c[0], c[1]), Block(c[1], c[2]), Block(c[2], c[3])
        self.u2, self.b2 = nn.ConvTranspose2d(c[3], c[2], 2, 2), Block(c[3], c[2])
        self.u1, self.b1 = nn.ConvTranspose2d(c[2], c[1], 2, 2), Block(c[2], c[1])
        self.u0, self.b0 = nn.ConvTranspose2d(c[1], c[0], 2, 2), Block(c[1], c[0])
        self.out = nn.Conv2d(c[0], 1, 1)

    def forward(self, x):
        h, w = x.shape[2:]
        ph, pw = (-h) % 8, (-w) % 8
        x = torch.cat([F.pad(x[:, :1], (0, pw, 0, ph), value=1.0),
                       F.pad(x[:, 1:], (0, pw, 0, ph), value=0.0)], 1)
        e0 = self.d0(x)
        e1 = self.d1(F.max_pool2d(e0, 2))
        e2 = self.d2(F.max_pool2d(e1, 2))
        m = self.mid(F.max_pool2d(e2, 2))
        z = self.b2(torch.cat([self.u2(m), e2], 1))
        z = self.b1(torch.cat([self.u1(z), e1], 1))
        z = self.b0(torch.cat([self.u0(z), e0], 1))
        return self.out(z)[:, :, :h, :w]


def loss_fn(logits, y):
    """Binary cross-entropy + soft Dice (Dice keeps the thin path from being ignored)."""
    bce = F.binary_cross_entropy_with_logits(logits, y)
    p = torch.sigmoid(logits)
    inter = (p * y).sum((1, 2, 3))
    dice = 1 - (2 * inter + 1) / (p.sum((1, 2, 3)) + y.sum((1, 2, 3)) + 1)
    return bce + dice.mean()


# ---------------------------------------------------------------- evaluation

EIGHT = np.ones((3, 3), dtype=bool)


def corridor_stats(prob, grid, mask, start, goal, thr=0.5):
    """Planner-facing metrics for a batch of numpy arrays (see module docstring)."""
    cov, con, size = [], [], []
    for p, g, m, s, t in zip(prob, grid, mask, start, goal):
        free = g == 0
        corr = ndimage.binary_dilation(p > thr, EIGHT) & free
        corr[s[1], s[0]] = corr[t[1], t[0]] = True
        cov.append((corr & (m == 1)).sum() / max(1, m.sum()))
        lab, _ = ndimage.label(corr, EIGHT)
        con.append(lab[s[1], s[0]] == lab[t[1], t[0]])
        size.append(corr.sum() / max(1, free.sum()))
    return float(np.mean(cov)), float(np.mean(con)), float(np.mean(size))


@torch.no_grad()
def evaluate(model, data, idx, device, batch, n_corridor=2000):
    grid, mask, start, goal = data
    model.eval()
    losses, inter, union = [], 0.0, 0.0
    probs = []
    for lo in range(0, len(idx), batch):
        j = idx[lo:lo + batch]
        x = make_input(grid[j], start[j], goal[j])
        y = mask[j].float().unsqueeze(1)
        with torch.autocast(device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
            logits = model(x)
        logits = logits.float()
        losses.append(loss_fn(logits, y).item() * len(j))
        pred = (logits > 0).float()
        inter += (pred * y).sum().item()
        union += ((pred + y) > 0).float().sum().item()
        if lo < n_corridor:
            probs.append(torch.sigmoid(logits)[:, 0].cpu().numpy())
    k = min(n_corridor, len(idx))
    sub = idx[:k].cpu()
    cov, con, size = corridor_stats(np.concatenate(probs)[:k], grid[sub].cpu().numpy(),
                                    mask[sub].cpu().numpy(), start[sub].cpu().numpy(),
                                    goal[sub].cpu().numpy())
    return {"val_loss": sum(losses) / len(idx), "iou": inter / max(1.0, union),
            "coverage": cov, "connected": con, "corridor": size}


def save_predictions(model, data, idx, device, path, n=8):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grid, mask, start, goal = data
    j = idx[:n]
    n = len(j)
    model.eval()
    with torch.no_grad():
        prob = torch.sigmoid(model(make_input(grid[j], start[j], goal[j])).float())[:, 0].cpu().numpy()
    g, m, s, t = (a[j].cpu().numpy() for a in (grid, mask, start, goal))
    fig, axes = plt.subplots(2, n, figsize=(2.6 * n, 5.6), squeeze=False)
    for c in range(n):
        for r, (img, title) in enumerate([(m[c], "exact path"), (prob[c], "network")]):
            ax = axes[r, c]
            ax.imshow(np.where(g[c] == 1, -0.4, img), cmap="magma", vmin=-0.4, vmax=1, origin="lower",
                      interpolation="nearest")
            ax.plot(*s[c], "o", color="lime", ms=5)
            ax.plot(*t[c], "o", color="cyan", ms=5)
            ax.set_xticks([])
            ax.set_yticks([])
            if c == 0:
                ax.set_ylabel(title)
    fig.suptitle("Validation maps (never trained on): top = label, bottom = prediction (black = obstacle)")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# ---------------------------------------------------------------- training

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default="data/ml_corridor")
    ap.add_argument("--name", default="unet_v1")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--base", type=int, default=32, help="U-Net width (channels in the first block)")
    ap.add_argument("--val-frac", type=float, default=0.05)
    ap.add_argument("--limit", type=int, default=0, help="use only this many samples (for quick tests)")
    args = ap.parse_args(argv)

    torch.manual_seed(0)
    np.random.seed(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out = os.path.join("runs", args.name)
    os.makedirs(out, exist_ok=True)

    t0 = time.time()
    grid, mask, start, goal = load_dataset(args.data)
    if args.limit:
        grid, mask, start, goal = grid[:args.limit], mask[:args.limit], start[:args.limit], goal[:args.limit]
    n = len(grid)
    n_val = max(1, int(n * args.val_frac))
    data = tuple(torch.from_numpy(a).to(device) for a in (grid, mask, start, goal))
    train_idx = torch.arange(0, n - n_val, device=device)
    val_idx = torch.arange(n - n_val, n, device=device)
    print(f"Device: {torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'} | "
          f"{n - n_val} train / {n_val} validation maps | loaded in {time.time() - t0:.0f} s", flush=True)

    model = UNet(base=args.base).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    steps_per_epoch = math.ceil(len(train_idx) / args.batch)
    total_steps = args.epochs * steps_per_epoch
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=total_steps,
                                                pct_start=max(0.1, 3 / total_steps))
    first_epoch, best = 0, float("inf")
    last_path, best_path = os.path.join(out, "last.pt"), os.path.join(out, "best.pt")
    if os.path.exists(last_path):
        ck = torch.load(last_path, map_location=device)
        if ck.get("epochs") != args.epochs or ck.get("base") != args.base:
            raise SystemExit(f"{last_path} was started with --epochs {ck.get('epochs')} --base {ck.get('base')}. "
                             "Resume with the same settings, or use a new --name.")
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["opt"])
        sched.load_state_dict(ck["sched"])
        first_epoch, best = ck["epoch"] + 1, ck["best"]
        print(f"Resuming from epoch {first_epoch} (best val loss so far {best:.4f})", flush=True)
    print(f"Model: U-Net, {n_params / 1e6:.2f} M parameters | {args.epochs} epochs x {steps_per_epoch} steps",
          flush=True)

    from torch.utils.tensorboard import SummaryWriter
    tb = SummaryWriter(os.path.join(out, "tb"))
    log_path = os.path.join(out, "log.csv")
    new_log = not os.path.exists(log_path) or first_epoch == 0
    log_f = open(log_path, "w" if new_log else "a", newline="")
    fields = ["epoch", "train_loss", "val_loss", "iou", "coverage", "connected", "corridor", "lr", "epoch_s"]
    log = csv.DictWriter(log_f, fieldnames=fields)
    if new_log:
        log.writeheader()

    grid_t, mask_t, start_t, goal_t = data
    for epoch in range(first_epoch, args.epochs):
        model.train()
        te = time.time()
        perm = train_idx[torch.randperm(len(train_idx), device=device)]
        total, count = 0.0, 0
        for lo in range(0, len(perm), args.batch):
            j = perm[lo:lo + args.batch]
            x = make_input(grid_t[j], start_t[j], goal_t[j])
            y = mask_t[j].float().unsqueeze(1)
            x, y = augment(x, y)
            with torch.autocast(device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
                logits = model(x)
            loss = loss_fn(logits.float(), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(j)
            count += len(j)

        stats = evaluate(model, data, val_idx, device, args.batch)
        row = {"epoch": epoch + 1, "train_loss": total / count, **stats,
               "lr": sched.get_last_lr()[0], "epoch_s": time.time() - te}
        log.writerow({k: (f"{v:.5g}" if isinstance(v, float) else v) for k, v in row.items()})
        log_f.flush()
        for k, v in row.items():
            if k != "epoch":
                tb.add_scalar(k, v, epoch + 1)
        if stats["val_loss"] < best:
            best = stats["val_loss"]
            torch.save({"model": model.state_dict(), "base": args.base, "epoch": epoch, "stats": stats}, best_path)
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                    "epoch": epoch, "best": best, "base": args.base, "epochs": args.epochs}, last_path)
        print(f"epoch {epoch + 1:3d}/{args.epochs} | train {row['train_loss']:.4f} | val {stats['val_loss']:.4f} | "
              f"IoU {stats['iou']:.3f} | coverage {stats['coverage']:.3f} | connected {stats['connected']:.3f} | "
              f"corridor {stats['corridor']:.3f} | {row['epoch_s']:.0f} s", flush=True)

    save_predictions(model, data, val_idx, device, os.path.join(out, "predictions.png"))
    tb.close()
    log_f.close()
    print(f"\nDONE in {(time.time() - t0) / 60:.1f} min -> {out}/ (best.pt, last.pt, log.csv, predictions.png)")


if __name__ == "__main__":
    main()
