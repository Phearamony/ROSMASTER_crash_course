# ROSMASTER Crash Course: How to Run

Everything you need to install ROS 2 on Windows and run the Week 1 simulation: a ROSMASTER A1 in Gazebo that avoids obstacles with its LiDAR.

## What you need

Windows 11, or Windows 10 build 19044 or newer (press Win+R, type `winver`). Everything runs on Ubuntu 22.04 inside WSL2.

| Item | Version |
| --- | --- |
| Ubuntu | 22.04 (WSL2 on Windows) |
| ROS 2 | Humble Hawksbill |
| Simulator | Gazebo Classic 11 |
| Course code | [github.com/Phearamony/ROSMASTER_crash_course](https://github.com/Phearamony/ROSMASTER_crash_course) |

Installing takes a few GB and 20 to 40 minutes. Do it at home before class.

## Install on Windows (once)

**1. Install Ubuntu (WSL2).** Right click PowerShell, choose Run as administrator:

```powershell
wsl --install -d Ubuntu-22.04
```

Restart the PC, open Ubuntu 22.04 from the Start menu, and make a username and password (the password is invisible while you type). Check with `lsb_release -a`. Already have WSL? Run `wsl --update` first. Everything below goes in the Ubuntu terminal.

**2. Prepare Ubuntu.**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y locales software-properties-common curl git
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo add-apt-repository -y universe
```

**3. Add the ROS 2 source** (from the [official Humble install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)):

```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

**4. Install ROS 2 and Gazebo.**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-humble-desktop ros-dev-tools
sudo apt install -y ros-humble-gazebo-ros-pkgs ros-humble-xacro ros-humble-teleop-twist-keyboard
```

**5. Load ROS 2 in every terminal, then test.**

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
ros2 run demo_nodes_cpp talker      # terminal 1
ros2 run demo_nodes_py listener     # terminal 2
```

The listener should print `I heard: [Hello World: 1]`. Stop both with Ctrl+C.

**6. Test Gazebo.** Run `gazebo`. An empty world opens on your Windows desktop. If it is black or crashes:

```bash
echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
source ~/.bashrc
```

## Run the Week 1 simulation

1. Get the code (once):

    ```bash
    mkdir -p ~/rosmaster_ws/src && cd ~/rosmaster_ws/src
    git clone https://github.com/Phearamony/ROSMASTER_crash_course.git
    ```

2. Build it:

    ```bash
    cd ~/rosmaster_ws && colcon build --symlink-install
    ```

3. Terminal 1, open Gazebo with the A1:

    ```bash
    source ~/rosmaster_ws/install/setup.bash
    ros2 launch rosmaster_sim sim.launch.py
    ```

    First start can take 30 seconds. The robot sits in the corner, publishing `/scan` and waiting for `/cmd_vel`.

4. Terminal 2, start the brain:

    ```bash
    source ~/rosmaster_ws/install/setup.bash
    ros2 run rosmaster_avoidance lidar_avoidance
    ```

    The robot drives and the terminal prints lines like `FORWARD front=2.31 left=1.05 right=0.88`.

Every new terminal needs the `source` line. To skip it: `echo "source ~/rosmaster_ws/install/setup.bash" >> ~/.bashrc`.

## Checks and experiments

Check it is working (terminal 3, source first):

```bash
ros2 node list               # see /lidar_avoidance
ros2 topic list              # see /scan and /cmd_vel
ros2 topic hz /scan          # about 10 messages per second
ros2 topic echo /cmd_vel     # speed commands the node sends
rqt_graph                    # draw the node graph
```

Week 1 experiments:

- [ ] Drive it yourself: stop the node (Ctrl+C), run `ros2 run teleop_twist_keyboard teleop_twist_keyboard`, drive with `i` `j` `l` `,` and stop with `k`.
- [ ] Look at the data: drive next to a box, run `ros2 topic echo /scan --once`, find the small numbers.
- [ ] Change behavior: `ros2 run rosmaster_avoidance lidar_avoidance --ros-args -p safe_distance:=0.4`, then `1.0`. Compare.
- [ ] Make it harder: drop new boxes or cylinders from the Gazebo toolbar. Does it still escape?

| Parameter | Default | Meaning |
| --- | --- | --- |
| forward_speed | 0.25 | Driving speed (m/s) |
| turn_speed | 1.0 | How hard to turn |
| safe_distance | 0.7 | Start turning when closer than this (m) |
| stop_distance | 0.3 | Back up when closer than this (m) |

## Real A1 commands (Weeks 3 and 4)

From Yahboom's [ROSMASTER A1 course](https://github.com/YahboomTechnology/ROSMASTER-A1). On a Raspberry Pi 5 or Jetson Nano, enter the robot's Docker container first.

| What | Command |
| --- | --- |
| Chassis driver | `ros2 run yahboomcar_bringup Ackman_driver_A1` |
| Keyboard driving | `ros2 run yahboomcar_ctrl yahboom_keyboard` |
| LiDAR (C1) | `ros2 launch sllidar_ros2 sllidar_c1_launch.py` |
| LiDAR (YDLidar) | `ros2 launch ydlidar_ros2_driver ydlidar_launch.py` |
| Obstacle avoidance | `ros2 run yahboomcar_laser laser_Avoidance_A1` |
| LiDAR following | `ros2 run yahboomcar_laser laser_Tracker_A1` |
| SLAM mapping (gmapping) | `ros2 launch yahboomcar_nav map_gmapping_launch.py` |
| Save the map | `ros2 launch yahboomcar_nav save_map_launch.py` |
| USB camera | `ros2 launch usb_cam camera.launch.py` |
| YOLO object recognition (Week 3 homework) | `cd /root/ultralytics/ultralytics/yahboom_demo && python3 01.detection_camera_usb.py` |
| Tune parameters live | `ros2 run rqt_reconfigure rqt_reconfigure` |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Package 'rosmaster_sim' not found` | Run `source ~/rosmaster_ws/install/setup.bash` in that terminal. |
| Gazebo black or crashes on WSL | `export LIBGL_ALWAYS_SOFTWARE=1`, then launch again. Update the Windows graphics driver. |
| Gazebo will not start, address in use | `killall gzserver gzclient`, then launch again. |
| Robot does not move | Is the avoidance node running? In `rqt_graph`, `/cmd_vel` must connect `/lidar_avoidance` to Gazebo. |
| Another student's robot moves yours | Each student picks a number: `export ROS_DOMAIN_ID=<1-100>` in every terminal. |
| `colcon: command not found` | `sudo apt install ros-dev-tools` |

Slides (PDF and PPTX) are in the [slides folder](slides/).
