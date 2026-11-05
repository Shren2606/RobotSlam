sudo apt update
sudo apt install python3-rosdep
sudo apt install gedit
source /opt/ros/jazzy/setup.bash
source ~/RobotSlam/install/setup.bash

cd ~/RobotSlam
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
colcon build

ros2 launch <package_name> <launch_file>
