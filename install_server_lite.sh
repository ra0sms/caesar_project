#!/bin/bash
# Install all needed packages and set up environment for SERVER part

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to handle errors
handle_error() {
    echo -e "${RED}Error occurred in command: $1${NC}"
    echo -e "${RED}Exiting script...${NC}"
    exit 1
}

# Enable error trapping
set -e
trap 'handle_error "$BASH_COMMAND"' ERR

echo -e "${GREEN}Updating...${NC}"
apt-get update || { echo -e "${RED}Failed to update packages${NC}"; exit 1; }

echo -e "${GREEN}Installing new packages...${NC}"
apt-get install -y make gcc python3 python3-pip swig python3-dev python3-setuptools mc socat avahi-daemon python3-flask python3-waitress || { echo -e "${RED}Failed to install basic packages${NC}"; exit 1; }
apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-alsa gstreamer1.0-tools gstreamer1.0-plugins-good || { echo -e "${RED}Failed to install gstreamer good packages${NC}"; exit 1; }
apt-get install -y gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav || { echo -e "${RED}Failed to install gstreamer other packages${NC}"; exit 1; }

echo -e "${GREEN}Cleaning...${NC}"
apt-get autoremove -y || { echo -e "${RED}Failed to autoremove packages${NC}"; exit 1; }
apt-get autoclean -y || { echo -e "${RED}Failed to autoclean packages${NC}"; exit 1; }
usermod -a -G dialout pi || { echo -e "${RED}Failed to modify user groups${NC}"; exit 1; }

echo -e "${GREEN}Set hostname...${NC}"
hostnamectl set-hostname caesar-server || { echo -e "${RED}Failed to set hostname${NC}"; exit 1; }
echo -e "${GREEN}Hostname changed...${NC}"

echo -e "${GREEN}Config hardware...${NC}"
rm -f /boot/armbianEnv.txt || { echo -e "${RED}Failed to remove old armbianEnv.txt${NC}"; exit 1; }
cp ./armbianEnv_lite.txt /boot/armbianEnv.txt || { echo -e "${RED}Failed to copy armbianEnv.txt${NC}"; exit 1; }

echo -e "${GREEN}Installing wiringPO...${NC}"
cd wiringOP/ || { echo -e "${RED}Failed to enter wiringOP directory${NC}"; exit 1; }
./build clean || { echo -e "${RED}Failed to clean wiringOP${NC}"; exit 1; }
./build || { echo -e "${RED}Failed to build wiringOP${NC}"; exit 1; }
cd ../
cd wiringOP-Python/ || { echo -e "${RED}Failed to enter wiringOP-Python directory${NC}"; exit 1; }
python3 generate-bindings.py > bindings.i || { echo -e "${RED}Failed to generate bindings${NC}"; exit 1; }
python3 setup.py install || { echo -e "${RED}Failed to install wiringOP-Python${NC}"; exit 1; }
gpio readall || { echo -e "${RED}Failed to run gpio readall${NC}"; exit 1; }
echo -e "${GREEN}wiringPO installed...${NC}"

echo -e "${GREEN}Config ptt_server.service...${NC}"
cd ../
chmod +x ./ptt_server.py
cp ./ptt_server.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy ptt_server.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start ptt_server.service || { echo -e "${RED}Failed to start ptt_server.service${NC}"; exit 1; }
systemctl enable ptt_server.service || { echo -e "${RED}Failed to enable ptt_server.service${NC}"; exit 1; }
systemctl status ptt_server.service || { echo -e "${RED}Failed to get status of ptt_server.service${NC}"; exit 1; }
echo -e "${GREEN}ptt_server.service started and enabled${NC}"

echo -e "${GREEN}Config check_client.service...${NC}"
cp ./check_client.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy check_client.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start check_client.service || { echo -e "${RED}Failed to start check_client.service${NC}"; exit 1; }
systemctl enable check_client.service || { echo -e "${RED}Failed to enable check_client.service${NC}"; exit 1; }
systemctl status check_client.service || { echo -e "${RED}Failed to get status of check_client.service${NC}"; exit 1; }
echo -e "${GREEN}check_client.service started and enabled${NC}"

echo -e "${GREEN}Config audio_server.service...${NC}"
cp ./audio_server.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy audio_server.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start audio_server.service || { echo -e "${RED}Failed to start audio_server.service${NC}"; exit 1; }
systemctl enable audio_server.service || { echo -e "${RED}Failed to enable audio_server.service${NC}"; exit 1; }
echo -e "${GREEN}audio_server.service started and enabled${NC}"

echo -e "${GREEN}Config audio_client_on_server.service...${NC}"
cp ./audio_client_on_server.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy audio_client_on_server.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start audio_client_on_server.service || { echo -e "${RED}Failed to start audio_client_on_server.service${NC}"; exit 1; }
systemctl enable audio_client_on_server.service || { echo -e "${RED}Failed to enable audio_client_on_server.service${NC}"; exit 1; }
echo -e "${GREEN}audio_client_on_server.service started and enabled${NC}"

echo -e "${GREEN}Config server_ping_responce.service...${NC}"
cp ./server_ping_responce.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy server_ping_responce.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start server_ping_responce.service || { echo -e "${RED}Failed to start server_ping_responce.service${NC}"; exit 1; }
systemctl enable server_ping_responce.service || { echo -e "${RED}Failed to enable server_ping_responce.service${NC}"; exit 1; }
systemctl status server_ping_responce.service || { echo -e "${RED}Failed to get status of server_ping_responce.service${NC}"; exit 1; }
echo -e "${GREEN}server_ping_responce.service started and enabled${NC}"

echo -e "${GREEN}Disable wi-fi module...${NC}"
modprobe -r xradio_wlan || { echo -e "${RED}Failed to disable wi-fi  module${NC}"; exit 1; }
echo "blacklist xradio_wlan" | tee -a /etc/modprobe.d/blacklist.conf || { echo -e "${RED}Failed to disable wi-fi  module${NC}"; exit 1; }
update-initramfs -u || { echo -e "${RED}Failed to update initramfs${NC}"; exit 1; }
echo -e "${GREEN}wi-fi module disabled${NC}"

echo -e "${GREEN}Config restart_services_on_client...${NC}"
echo "pi ALL=(ALL) NOPASSWD: /home/pi/caesar_project/restart_services_on_server.sh" | tee -a /etc/sudoers || { echo -e "${RED}Failed to config sudoers${NC}"; exit 1; }

echo -e "${GREEN}Config alsa_restore.service...${NC}"
cp ./alsa_restore.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy alsa_restore.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start alsa_restore.service || { echo -e "${RED}Failed to start alsa_restore.service${NC}"; exit 1; }
systemctl enable alsa_restore.service || { echo -e "${RED}Failed to enable alsa_restore.service${NC}"; exit 1; }
systemctl status alsa_restore.service || { echo -e "${RED}Failed to get status of alsa_restore.service${NC}"; exit 1; }
echo -e "${GREEN}alsa_restore.service started and enabled${NC}"

echo -e "${GREEN}Config web_config_server.service...${NC}"
cp ./web_config_server.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy web_config.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start web_config_server.service || { echo -e "${RED}Failed to start web_config.service${NC}"; exit 1; }
systemctl enable web_config_server.service || { echo -e "${RED}Failed to enable web_config.service${NC}"; exit 1; }
systemctl status web_config_server.service || { echo -e "${RED}Failed to get status of web_config.service${NC}"; exit 1; }
echo -e "${GREEN}web_config_server.service started and enabled${NC}"

echo -e "${GREEN}Create server_ip.cfg and client_ip.cfg...${NC}"
touch ./server_ip.cfg || { echo -e "${RED}Failed to create server_ip.cfg${NC}"; exit 1; }
touch ./client_ip.cfg || { echo -e "${RED}Failed to create client_ip.cfg${NC}"; exit 1; }

echo -e "${GREEN}Done. You need to edit ${RED}client_ip.cfg and server_ip.cfg${GREEN} and reboot (sudo reboot).${NC}"
