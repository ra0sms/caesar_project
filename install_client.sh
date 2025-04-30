#!/bin/bash
# Install all needed packages and set up environment for CLIENT part

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

echo -e "${GREEN}Upgrading...${NC}"
apt-get upgrade -y || { echo -e "${RED}Failed to upgrade packages${NC}"; exit 1; }

echo -e "${GREEN}Installing new packages...${NC}"
apt-get install -y git make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools mc socat || { echo -e "${RED}Failed to install basic packages${NC}"; exit 1; }
apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-alsa gstreamer1.0-tools gstreamer1.0-plugins-good || { echo -e "${RED}Failed to install gstreamer good packages${NC}"; exit 1; }
apt-get install -y gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav || { echo -e "${RED}Failed to install gstreamer other packages${NC}"; exit 1; }

echo -e "${GREEN}Cleaning...${NC}"
apt-get autoremove -y || { echo -e "${RED}Failed to autoremove packages${NC}"; exit 1; }
apt-get autoclean -y || { echo -e "${RED}Failed to autoclean packages${NC}"; exit 1; }
usermod -a -G dialout pi || { echo -e "${RED}Failed to modify user groups${NC}"; exit 1; }

echo -e "${GREEN}Config hardware...${NC}"
rm -f /boot/armbianEnv.txt || { echo -e "${RED}Failed to remove old armbianEnv.txt${NC}"; exit 1; }
cp ./armbianEnv.txt /boot/ || { echo -e "${RED}Failed to copy armbianEnv.txt${NC}"; exit 1; }


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

echo -e "${GREEN}Config ptt_client.service...${NC}"
cd ../
chmod +x ./ptt_client.py
cp ./ptt_client.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy ptt_client.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start ptt_client.service || { echo -e "${RED}Failed to start ptt_client.service${NC}"; exit 1; }
systemctl enable ptt_client.service || { echo -e "${RED}Failed to enable ptt_client.service${NC}"; exit 1; }
systemctl status ptt_client.service || { echo -e "${RED}Failed to get status of ptt_client.service${NC}"; exit 1; }
echo -e "${GREEN}ptt_client.service started and enabled${NC}"

echo -e "${GREEN}Config check_server.service...${NC}"
cp ./check_server.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy check_server.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start check_server.service || { echo -e "${RED}Failed to start check_server.service${NC}"; exit 1; }
systemctl enable check_server.service || { echo -e "${RED}Failed to enable check_server.service${NC}"; exit 1; }
systemctl status check_server.service || { echo -e "${RED}Failed to get status of check_server.service${NC}"; exit 1; }
echo -e "${GREEN}check_server.service started and enabled${NC}"

echo -e "${GREEN}Config audio_client.service...${NC}"
cp ./audio_client.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy audio_client.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start audio_client.service || { echo -e "${RED}Failed to start audio_client.service${NC}"; exit 1; }
systemctl enable audio_client.service || { echo -e "${RED}Failed to enable audio_sclient.service${NC}"; exit 1; }
echo -e "${GREEN}audio_client.service started and enabled${NC}"

echo -e "${GREEN}Config audio_server_on_client.service...${NC}"
cp ./audio_server_on_client.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy audio_server_on_client.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start audio_server_on_client.service || { echo -e "${RED}Failed to start audio_server_on_client.service${NC}"; exit 1; }
systemctl enable audio_server_on_client.service || { echo -e "${RED}Failed to enable audio_server_on_client.service${NC}"; exit 1; }
echo -e "${GREEN}audio_server_on_client.service started and enabled${NC}"

echo -e "${GREEN}Config client_ping_responce.service...${NC}"
cp ./client_ping_responce.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy client_ping_responce.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start client_ping_responce.service || { echo -e "${RED}Failed to start client_ping_responce.service${NC}"; exit 1; }
systemctl enable client_ping_responce.service || { echo -e "${RED}Failed to enable client_ping_responce.service${NC}"; exit 1; }
systemctl status client_ping_responce.service || { echo -e "${RED}Failed to get status of client_ping_responce.service${NC}"; exit 1; }
echo -e "${GREEN}client_ping_responce.service started and enabled${NC}"

echo -e "${GREEN}Config client_ser2net.service...${NC}"
cp ./client_ser2net.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy client_ser2net.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start client_ser2net.service || { echo -e "${RED}Failed to start client_ser2net.service${NC}"; exit 1; }
systemctl enable client_ser2net.service || { echo -e "${RED}Failed to enable client_ser2net.service${NC}"; exit 1; }
echo -e "${GREEN}client_ser2net.service started and enabled${NC}"

echo -e "${GREEN}Config client_winkeyer.service...${NC}"
cp ./client_winkeyer.service /etc/systemd/system/ || { echo -e "${RED}Failed to copy client_winkeyer.service${NC}"; exit 1; }
systemctl daemon-reload || { echo -e "${RED}Failed to reload systemd daemon${NC}"; exit 1; }
systemctl start client_winkeyer.service || { echo -e "${RED}Failed to start client_winkeyer.service${NC}"; exit 1; }
systemctl enable client_winkeyer.service || { echo -e "${RED}Failed to enable client_winkeyer.service${NC}"; exit 1; }
echo -e "${GREEN}client_winkeyer.service started and enabled${NC}"

echo -e "${GREEN}Done. You need to edit ${RED}client_ip.cfg and server_ip.cfg${GREEN} and reboot (sudo reboot).${NC}"