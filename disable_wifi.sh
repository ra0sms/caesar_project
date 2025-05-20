#!/bin/bash

echo -e "${GREEN}Disable wi-fi module...${NC}"
modprobe -r xradio_wlan || { echo -e "${RED}Failed to disable wi-fi  module${NC}"; exit 1; }
echo "blacklist xradio_wlan" | tee -a /etc/modprobe.d/blacklist.conf | { echo -e "${RED}Failed to disable wi-fi  module${NC}"; exit 1; }
update-initramfs -u || { echo -e "${RED}Failed to update initramfs${NC}"; exit 1; }
echo -e "${GREEN}wi-fi module disabled${NC}"