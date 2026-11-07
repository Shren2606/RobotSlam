#!/bin/bash

BASHRC="$HOME/.bashrc"

# Check if ROS 2 Jazzy source already exists
if ! grep -Fq "source /opt/ros/jazzy/setup.bash" "$BASHRC"; then

    echo "" >> "$BASHRC"
    echo "# Load ROS 2 Jazzy" >> "$BASHRC"
    echo "source /opt/ros/jazzy/setup.bash
    " >> "$BASHRC"
    

fi

# Check if RobotSlam workspace source already exists
if ! grep -Fq "source ~/RobotSlam/install/setup.bash" "$BASHRC"; then

    echo "# Load RobotSlam workspace" >> "$BASHRC"
    echo "source ~/RobotSlam/install/setup.bash
    " >> "$BASHRC"

fi

echo "ROS 2 environment setup completed!:
# Load ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Load RobotSlam workspace
source ~/RobotSlam/install/setup.bash"