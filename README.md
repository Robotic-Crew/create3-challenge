# Robotic Crew Challenge: Create 3 in simulation

Welcome! This repo contains a ready-to-run simulation of an **iRobot Create 3** with a **2D lidar** and an **RGB camera**. It runs on **ROS 2 Humble + Ignition Gazebo Fortress** inside Docker.

Your job is to add two things:

1. **Keyboard teleoperation**: drive the robot from the keyboard.
2. **RViz visualization**: see the robot, the lidar and the camera in RViz.

---

## Requirements

- Linux with X11 (Ubuntu 22.04/24.04 recommended). Wayland works through XWayland.
- Docker Engine 24+ with the `docker compose` plugin.
- Intel/AMD GPU with Mesa drivers, which works out of the box. For NVIDIA, see [Troubleshooting](#troubleshooting).
- About 6 GB of free disk space.

## Running the simulation

```bash
cp .env.example .env
xhost +local:docker            # let containers open windows on your X11 display
docker compose up --build sim
```

The first build takes several minutes. When it finishes, Gazebo opens with the robot in the middle of a simple 8 x 6 m room with a few colored obstacles.

To check that everything is publishing, run this in another terminal:

```bash
docker compose run --rm shell /ws/scripts/check_topics.sh
```

To get a shell with ROS on the same network:

```bash
docker compose run --rm shell
ros2 topic list
```

## What's in the simulation

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity command (**input**) |
| `/odom` | `nav_msgs/msg/Odometry` | Wheel odometry |
| `/tf`, `/tf_static` | `tf2_msgs/msg/TFMessage` | Transform tree (`odom → base_link → lidar_link`, `camera_link`, …) |
| `/scan` | `sensor_msgs/msg/LaserScan` | 360° lidar, 10 Hz, 0.15 to 12 m |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | RGB camera, 640x480, 15 Hz |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera calibration |
| `/robot_description` | `std_msgs/msg/String` | Robot URDF |

You also get the standard Create 3 topics, the same ones the real robot has: `/imu`, `/hazard_detection`, `/dock_status`, `/battery_state`, the `/dock` and `/undock` actions, and so on.

Layout:

```
docker/                 image Dockerfile and entrypoint
docker-compose.yml      services (sim, shell)
ws/src/rcrew_sim/       ROS 2 package: URDF (Create 3 + lidar + camera), world, GUI config and launch file
scripts/                utilities
```

---

## Your task

### 1. Keyboard teleop

Make it possible to drive the robot from the keyboard by publishing to `/cmd_vel`.

- It must run in Docker, integrated into `docker-compose.yml` (for example, as a new service).
- You can use an existing package or write your own node. Writing your own earns extra credit.
- Document how to use it.

### 2. RViz

Make it possible to open RViz and see:

- the robot model,
- the lidar scan,
- the camera image,
- the odometry or TF.

It must run in Docker, and the RViz configuration must be saved in the repo, so that RViz opens with everything already showing and nothing to set up by hand.

### Optional extras

These are not required, but if you have time left:

- A single command that brings everything up (sim + RViz + teleop).
- A parameter that caps the teleop's maximum speed.
- A node that stops the robot when the lidar sees an obstacle closer than X meters.
- Anything else you think is useful. Tell us why.

## Submission

- A git repo (GitHub/GitLab, or a `.zip` that includes the `.git` folder) with commits that show how you progressed.
- Update this README, or add a `SOLUTION.md`, explaining:
  - how to run your solution, step by step;
  - what decisions you made and why;
  - what problems you ran into and how you solved them;
  - what you would improve with more time.
- A screenshot or short video of RViz with the robot moving is a big plus.

We will test it on a clean machine following **only** your instructions.

---

## Troubleshooting

**`cannot open display` or Gazebo doesn't open a window.** Run `xhost +local:docker` and check that `echo $DISPLAY` is not empty.

**Gazebo opens but freezes or shows a black screen.** Try software rendering by setting `LIBGL_ALWAYS_SOFTWARE=1` in `.env`. It's slower, but it works.

**NVIDIA.** Install `nvidia-container-toolkit` and add this to the service:
```yaml
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
```

**`/dev/dri` doesn't exist.** Remove the `devices` section from `docker-compose.yml` and set `LIBGL_ALWAYS_SOFTWARE=1`.

**`apt-get update` hangs or fails during the build.** Some Docker setups have broken DNS on the default bridge network. The build already uses `network: host` to avoid this. If it still fails, check your host's DNS settings.

**Topics aren't visible from another container or from the host.** Make sure everything uses the same `ROS_DOMAIN_ID`, and that `network_mode: host` and `ipc: host` are set.

**The robot stops or ignores commands after hitting something.** That's the Create 3's built-in safety (bump/cliff reflexes), same as on the real robot. Back off with a negative linear velocity.

Questions? Reach out. Asking won't cost you points.
