#!/bin/bash
# Install required packages and configure environment for SERVER part

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'


handle_error() {
    echo -e "${RED}Error in command: $1${NC}"
    echo -e "${RED}Exiting script...${NC}"
    exit 1
}

set -e
trap 'handle_error "$BASH_COMMAND"' ERR

echo -e "${GREEN}Updating package lists...${NC}"
apt-get update || { echo -e "${RED}Failed to update packages${NC}"; exit 1; }

echo -e "${GREEN}Installing required packages...${NC}"
apt-get install -y \
  make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools mc socat avahi-daemon \
  python3-flask python3-waitress gstreamer1.0-plugins-base gstreamer1.0-alsa \
  gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly gstreamer1.0-libav || 
  { echo -e "${RED}Failed to install packages${NC}"; exit 1; }

echo -e "${GREEN}Cleaning up...${NC}"
apt-get autoremove -y && apt-get autoclean -y
usermod -a -G dialout pi || { echo -e "${RED}Failed to modify user groups${NC}"; exit 1; }

echo -e "${GREEN}Setting hostname...${NC}"
hostnamectl set-hostname caesar-server-1 || { echo -e "${RED}Failed to set hostname${NC}"; exit 1; }

echo -e "${GREEN}Configuring hardware...${NC}"
rm -f /boot/armbianEnv.txt && cp ./armbianEnv.txt /boot/armbianEnv.txt

echo -e "${GREEN}Creating IP configuration files...${NC}"
cat <<EOF > server_ip.cfg || { echo -e "${RED}Failed to create server_ip.cfg${NC}"; exit 1; }
10.0.0.2
EOF

cat <<EOF > client_ip.cfg || { echo -e "${RED}Failed to create client_ip.cfg${NC}"; exit 1; }
10.0.0.3
EOF

/usr/sbin/alsactl -f /var/lib/alsa/asound.state store

echo -e "${GREEN}Installing wiringOP...${NC}"
pushd wiringOP/ || { echo -e "${RED}Failed to enter wiringOP directory${NC}"; exit 1; }
./build clean && ./build
popd

pushd wiringOP-Python/ || { echo -e "${RED}Failed to enter wiringOP-Python directory${NC}"; exit 1; }
python3 generate-bindings.py > bindings.i && python3 setup.py install
gpio readall
popd

echo -e "${GREEN}Fixing COM-ports for CAT and WinKeyer...${NC}"
./fix_usb_ports.sh || { echo -e "${RED}Failed to run fix_usb_ports.sh${NC}"; exit 1; }

echo -e "${GREEN}Config ser2net...${NC}"
./create_ser2net_yaml.sh || { echo -e "${RED}Failed to run create_ser2net_yaml.sh${NC}"; exit 1; }


setup_service() {
  local service_name=$1
  cp ./${service_name}.service /etc/systemd/system/ || 
    { echo -e "${RED}Failed to copy ${service_name}.service${NC}"; exit 1; }
  systemctl daemon-reload
  systemctl start ${service_name}.service || 
    { echo -e "${RED}Failed to start ${service_name}.service${NC}"; exit 1; }
  systemctl enable ${service_name}.service || 
    { echo -e "${RED}Failed to enable ${service_name}.service${NC}"; exit 1; }
  echo -e "${GREEN}${service_name}.service configured successfully${NC}"
}

services=("ptt_server" "check_client" "audio_server" "audio_client_on_server" 
          "server_ping_responce" "web_config_server" "alsa_restore")

for service in "${services[@]}"; do
  setup_service "$service"
done

echo -e "${GREEN}Disabling Wi-Fi module...${NC}"
modprobe -r xradio_wlan
echo "blacklist xradio_wlan" | tee -a /etc/modprobe.d/blacklist.conf
update-initramfs -u

sudoers_entry="pi ALL=(ALL) NOPASSWD: /home/pi/caesar_project/restart_services_on_server.sh"
grep -qF "$sudoers_entry" /etc/sudoers || 
  { echo "$sudoers_entry" | sudo EDITOR='tee -a' visudo; }

echo -e "${GREEN}Configuration completed successfully. Please edit client_ip.cfg and server_ip.cfg, then reboot (sudo reboot).${NC}"
