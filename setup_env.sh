
#!/bin/bash

set -e

# ============================================================
# RobotSlam Workspace Setup
# ============================================================

WORKSPACE="$HOME/RobotSlam"
BASHRC="$HOME/.bashrc"

echo "=================================================="
echo "          RobotSlam Setup & Build"
echo "=================================================="

# ============================================================
# 1. Install System Dependencies
# ============================================================

echo ""
echo "[1/5] Installing system dependencies..."

sudo apt update

sudo apt install -y \
    xterm \
    python3-rosdep \
    python3-colcon-common-extensions \
    mesa-utils

echo "[INFO] System dependencies installed."

# ============================================================
# 2. Install ROS 2 Dependencies
# ============================================================

echo ""
echo "[2/5] Installing ROS 2 dependencies..."

source /opt/ros/jazzy/setup.bash

if ! command -v rosdep &> /dev/null; then
    echo "[ERROR] rosdep is not available."
    exit 1
fi

# Initialize rosdep if necessary
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi

rosdep update

cd "$WORKSPACE"

rosdep install \
    --from-paths src \
    --ignore-src \
    --rosdistro jazzy \
    -r -y

echo "[INFO] ROS 2 dependencies installed."

# ============================================================
# 3. Build RobotSlam Workspace
# ============================================================

echo ""
echo "[3/5] Building RobotSlam..."

colcon build --symlink-install

echo "[INFO] RobotSlam build completed."

# ============================================================
# 4. Configure ROS 2 Environment
# ============================================================

echo ""
echo "[4/5] Configuring ROS 2 environment..."

add_bashrc_line() {
    local line="$1"

    if ! grep -Fqx "$line" "$BASHRC"; then
        printf '%s\n' "$line" >> "$BASHRC"
    fi
}

# ROS 2 Jazzy
add_bashrc_line ""
add_bashrc_line "# Load ROS 2 Jazzy"
add_bashrc_line 'source /opt/ros/jazzy/setup.bash'

# RobotSlam workspace
add_bashrc_line ""
add_bashrc_line "# Load RobotSlam workspace"
add_bashrc_line 'if [ -f "$HOME/RobotSlam/install/setup.bash" ]; then source "$HOME/RobotSlam/install/setup.bash"; fi'

# NVIDIA GPU acceleration for WSLg
add_bashrc_line ""
add_bashrc_line "# NVIDIA GPU acceleration for WSLg"
add_bashrc_line 'export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA'
add_bashrc_line 'export GALLIUM_DRIVER=d3d12'
add_bashrc_line 'unset LIBGL_ALWAYS_SOFTWARE'

echo "[INFO] Environment configuration completed."

# ============================================================
# 5. Finalize Environment
# ============================================================

echo ""
echo "[5/5] Verifying environment..."

echo ""
echo "=================================================="
echo "       RobotSlam Setup Completed!"
echo "=================================================="

echo "[OK] XTerm installed"
echo "[OK] Mesa utilities installed"
echo "[OK] ROS 2 dependencies installed"
echo "[OK] RobotSlam workspace built"
echo "[OK] ROS 2 Jazzy configured"
echo "[OK] RobotSlam workspace configured"
echo "[OK] NVIDIA WSLg environment configured"

echo ""
echo "Please reload your terminal or run:"
echo "  source ~/.bashrc"
echo ""
echo "Check GPU acceleration:"
echo "  glxinfo -B"
echo ""
echo "Run Gazebo:"
echo "  ros2 launch bumperbot_bringup simulated_robot.launch.py"
echo ""
echo "=================================================="
