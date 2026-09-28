#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/humble/setup.bash
source /root/puppypi_ws/install/setup.bash
export need_compile=True
export DISPLAY=:99
export LIBGL_ALWAYS_SOFTWARE=1
export QT_X11_NO_MITSHM=1
export ROS_LOCALHOST_ONLY=1
mkdir -p /mnt/g/Projects/PuppyPi/official/logs
LOG=/mnt/g/Projects/PuppyPi/official/logs
Xvfb :99 -screen 0 1440x900x24 -ac +extension GLX +render -noreset > "$LOG/xvfb.log" 2>&1 &
XVFB=$!
sleep 2
openbox > "$LOG/openbox.log" 2>&1 &
WM=$!
x11vnc -display :99 -localhost -rfbport 5905 -nopw -forever -shared > "$LOG/vnc.log" 2>&1 &
VNC=$!
websockify --web /usr/share/novnc 127.0.0.1:6085 localhost:5905 > "$LOG/websockify.log" 2>&1 &
WEB=$!
trap 'kill "$WEB" "$VNC" "$WM" "$XVFB" 2>/dev/null || true' EXIT
ros2 launch puppypi_description display.launch.py use_sim_time:=false 2>&1 | tee "$LOG/ros-launch.log"
