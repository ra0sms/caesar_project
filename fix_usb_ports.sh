#!/bin/bash

# Check root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: use sudo." >&2
    exit 1
fi

# udev file
UDEV_RULES_FILE="/etc/udev/rules.d/99-usb-fixed-ports.rules"

# Check connection of both devices
if [ ! -e "/dev/ttyUSB0" ] || [ ! -e "/dev/ttyUSB1" ]; then
    echo "Error: ttyUSB0 and/or ttyUSB1 not found" >&2
    echo "Connect devices" >&2
    exit 1
fi

# Get ID_PATH for ttyUSB0 and ttyUSB1
ID_PATH_USB0=$(udevadm info --name=/dev/ttyUSB0 | grep "ID_PATH=" | cut -d'=' -f2)
ID_PATH_USB1=$(udevadm info --name=/dev/ttyUSB1 | grep "ID_PATH=" | cut -d'=' -f2)

if [ -z "$ID_PATH_USB0" ] || [ -z "$ID_PATH_USB1" ]; then
    echo "Cannot find ID_PATH" >&2
    exit 1
fi

# Create rules for udev
echo "SUBSYSTEM==\"tty\", ENV{ID_PATH}==\"$ID_PATH_USB0\", SYMLINK+=\"ttyCAT\"" > "$UDEV_RULES_FILE"
echo "SUBSYSTEM==\"tty\", ENV{ID_PATH}==\"$ID_PATH_USB1\", SYMLINK+=\"ttyWK\"" >> "$UDEV_RULES_FILE"

# Apply rules
udevadm control --reload-rules
udevadm trigger

echo "udev rules added:"
echo "- /dev/ttyUSB0 → /dev/ttyCAT (ID_PATH: $ID_PATH_USB0)"
echo "- /dev/ttyUSB1 → /dev/ttyWK (ID_PATH: $ID_PATH_USB1)"
echo "Reboot for connection"
