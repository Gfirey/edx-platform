#!/bin/sh
[ ! -d "/edx/edx-platform/log" ] && mkdir /edx/edx-platform/log
echo "Starting edX Studio (cms)..."
nohup rake cms[dev,0.0.0.0:8001] 2>&1 1>/edx/edx-platform/log/cms.log &
echo "done"
