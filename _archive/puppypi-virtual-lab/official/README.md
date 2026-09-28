# Official PuppyPi installation

Upstream: https://github.com/Hiwonder/PuppyPi, branch `ros2`.
Pinned checkout: `dfff97c42331f97497050a5558e650bde41bf54d`.
Location: `../upstream/PuppyPi`. Original files are kept unchanged.

## Scope

Install/build the official `puppypi_description` ROS2 package and its dependencies, then run the official URDF/STL model in RViz using ROS2 joint states. The official ROS2 simulation course uses this workflow:
https://docs.hiwonder.com/projects/PuppyPi/en/latest/docs/22.ROS2_Simulation_Course.html

This is distinct from the earlier custom JavaScript simulator at the project root.

## Upstream blockers found

- `src/driver/puppy_control/puppy_control/puppy.py` imports `puppy_kinematics`, `servo_controller`, `action_group_control`, and `pwm_servo_control` from the vendor robot image. These modules are not present in this Git checkout. It also constructs a hardware `Board()` at import time.
- `puppy.gazebo.xacro` references `libgazebo_ros_control.so`, a ROS1 Gazebo plugin. Do not describe the ROS2 checkout as an immediately runnable Gazebo gait stack.
- Official launch scripts require `need_compile=True` to resolve installed packages instead of `/home/ubuntu/ros2_ws`.
- Use `use_sim_time:=false` for RViz/joint-state testing without a physics simulator publishing `/clock`.

Full vendor gait execution needs the missing vendor SDK/image and verification of CPU architecture support. No replacement gait is presented as vendor code.

## Environment and commands

Dedicated Ubuntu 22.04 WSL1 distribution: `PuppyPi-ROS2`, stored under `G:\Projects\PuppyPi\.runtime\wsl-ubuntu`. WSL2 installation reported virtualization unavailable on this machine. Existing Debian was not modified.

Ubuntu image SHA256: `1483cc5c1dce13064f774834cbffdff226559fd522a67a381a8ea77d63fb4109`, checked against Canonical's SHA256SUMS over HTTPS.

```powershell
wsl -d PuppyPi-ROS2 -u root -- bash /mnt/g/Projects/PuppyPi/official/install-ros.sh
wsl -d PuppyPi-ROS2 -u root -- bash /mnt/g/Projects/PuppyPi/official/build-drivers.sh
.\official\start.ps1
```

The RViz session is exposed only on localhost at `http://127.0.0.1:6085/vnc.html?autoconnect=true&resize=scale`. It is a real Linux RViz window, delivered through noVNC. RViz shows kinematics and joint changes, not physical contact dynamics. Use the joint-state publisher sliders to test individual joints.

The original Git files remain unchanged. Build outputs are in `/root/puppypi_ws`; generated files and logs are in this `official` folder. The public checkout does not include all vendor runtime files needed to launch the full robot control stack.
