#!/bin/bash

if ! amixer scontrols >/dev/null 2>&1; then
    echo "ALSA mixer returned an error, restarting USB..."
    echo 0 | sudo tee /sys/bus/usb/devices/usb*/authorized >/dev/null
    sleep 1
    echo 1 | sudo tee /sys/bus/usb/devices/usb*/authorized >/dev/null
    echo "USB restart."
else
    echo "alsamixer works properly"
fi