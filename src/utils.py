"""Compatibility shim: the implementation now lives in ``planner_core``.

Kept so existing scripts (``python src/demo.py``, ``scripts/run_simulation.py``)
keep working. Do not add code here.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planner_core.utils import *  # noqa: F401,F403,E402
