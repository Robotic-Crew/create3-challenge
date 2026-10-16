#!/bin/bash
# Checks that the simulation is publishing the main topics.
# Usage (with the sim running):  docker compose run --rm shell /ws/scripts/check_topics.sh

source /opt/ros/humble/setup.bash

ok=0
check() {
    local topic=$1
    if timeout 15 ros2 topic echo --once --no-arr "$topic" >/dev/null 2>&1; then
        echo "  OK    $topic"
    else
        echo "  FAIL  $topic (no message received in 15s)"
        ok=1
    fi
}

echo "Checking topics on ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}..."
for t in /clock /odom /tf /scan /camera/image_raw /camera/camera_info; do
    check "$t"
done
exit $ok
