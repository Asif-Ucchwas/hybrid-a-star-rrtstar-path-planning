# Hybrid A*-RRT* Path Planner — Docker Container
# Author: Md Asifuzzaman
# Base image: ROS2 Jazzy on Ubuntu 24.04

FROM ros:jazzy-ros-base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --break-system-packages \
    numpy \
    matplotlib \
    scipy

# Create workspace
WORKDIR /ros2_ws

# Copy project files into container
COPY . /ros2_ws/hybrid-planner/

# Set working directory to project
WORKDIR /ros2_ws/hybrid-planner

# Source ROS2 on container start
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

# Default command when container starts
CMD ["/bin/bash"]
