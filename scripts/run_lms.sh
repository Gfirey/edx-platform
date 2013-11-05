#!/bin/sh
[ ! -d "/edx/edx-platform/log" ] && mkdir /edx/edx-platform/log
echo "Starting edX platform (lms)..."
nohup rake lms[cms.dev,0.0.0.0:8000] 2>&1 1>/edx/edx-platform/log/lms.log &
echo "done"
