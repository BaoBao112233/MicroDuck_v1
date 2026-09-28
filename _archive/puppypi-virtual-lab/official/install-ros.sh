#!/usr/bin/env bash
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg locales software-properties-common
locale-gen en_US en_US.UTF-8
add-apt-repository -y universe
if [ -f /mnt/g/Projects/PuppyPi/official/ros-archive-keyring.gpg ]; then
  cp /mnt/g/Projects/PuppyPi/official/ros-archive-keyring.gpg /usr/share/keyrings/ros-archive-keyring.gpg
else
  curl --fail --location https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
fi
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main' > /etc/apt/sources.list.d/ros2.list
apt-get update
apt-get install -y ros-humble-ros-base ros-humble-rviz2 ros-humble-xacro ros-humble-joint-state-publisher-gui ros-humble-robot-state-publisher ros-humble-nav2-common python3-colcon-common-extensions xvfb x11vnc novnc websockify openbox
source /opt/ros/humble/setup.bash
mkdir -p /root/puppypi_ws/src
ln -sfn /mnt/g/Projects/PuppyPi/upstream/PuppyPi/src/simulations/puppypi_description /root/puppypi_ws/src/puppypi_description
cd /root/puppypi_ws
colcon build --packages-select puppypi_description
source install/setup.bash
ros2 pkg prefix puppypi_description
xacro install/puppypi_description/share/puppypi_description/urdf/puppy.xacro > /mnt/g/Projects/PuppyPi/official/puppy.generated.urdf
