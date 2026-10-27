#!/bin/bash
# Starts a virtual X display (:1) and serves it over noVNC on port 6080.
set -e

RESOLUTION=${RESOLUTION:-1920x1080}

# A socket left over from a previous run would make the healthcheck pass too early.
rm -f /tmp/.X11-unix/X1 /tmp/.X1-lock
mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

Xvfb :1 -screen 0 "${RESOLUTION}x24" -ac -nolisten tcp +extension GLX +render -noreset &
while [ ! -S /tmp/.X11-unix/X1 ]; do sleep 0.2; done

export DISPLAY=:1
openbox &
x11vnc -display :1 -forever -shared -nopw -rfbport 5900 -quiet &

echo "Desktop ready: open http://localhost:6080 in your browser"
exec websockify --web /usr/share/novnc 6080 localhost:5900
