# Challenge simulator: ROS 2 Humble + Ignition Gazebo Fortress + Create 3.
FROM ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-humble-irobot-create-ignition-sim \
        ros-humble-irobot-create-description \
        ros-humble-ros-gz \
        ros-humble-xacro \
        libgl1-mesa-dri \
        mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# The stock Create 3 URDF runs the Sensors system on Ogre 1, where gpu_lidar
# returns range_min on every ray with recent Mesa drivers. Ogre 2 works.
RUN sed -i 's#<render_engine>ogre</render_engine>#<render_engine>ogre2</render_engine>#' \
        /opt/ros/humble/share/irobot_create_description/urdf/create3.urdf.xacro

WORKDIR /ws
COPY ws/src src
RUN . /opt/ros/humble/setup.sh && colcon build && rm -rf build log

COPY scripts /ws/scripts
COPY docker/entrypoint.sh /entrypoint.sh
# Strip CRLF and restore the exec bit in case the repo was checked out on Windows.
RUN sed -i 's/\r$//' /entrypoint.sh /ws/scripts/*.sh \
    && chmod +x /entrypoint.sh /ws/scripts/*.sh \
    && echo 'source /ws/install/setup.bash' >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
