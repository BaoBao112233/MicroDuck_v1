#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/humble/setup.bash
export DEBIAN_FRONTEND=noninteractive
apt-get install -y build-essential cmake ros-humble-rosidl-default-generators python3-numpy python3-matplotlib python3-serial python3-yaml
cd /root/puppypi_ws
for package in puppy_control puppy_control_msgs ros_robot_controller ros_robot_controller_msgs sdk; do
  ln -sfn "/mnt/g/Projects/PuppyPi/upstream/PuppyPi/src/driver/$package" "src/$package"
done
colcon build --packages-select puppy_control puppy_control_msgs ros_robot_controller ros_robot_controller_msgs sdk --cmake-args -DBUILD_TESTING=OFF
