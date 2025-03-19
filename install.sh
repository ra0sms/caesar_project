#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Updating...${NC}"
apt-get update

echo -e "${GREEN}Upgrading...${NC}"
apt-get upgrade -y

echo -e "${GREEN}Installing new packages...${NC}"
apt-get install -y git make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools 

echo -e "${GREEN}Cleaning...${NC}"
apt-get autoremove -y
apt-get autoclean -y

echo -e "${GREEN}Config ser2net...${NC}"
./create_ser2net_yaml.sh

echo -e "${GREEN}Config ptt_server.service...${NC}"
cp ./ptt_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl start ptt_server.service
systemctl enable ptt_server.service
systemctl status ptt_server.service
echo -e "${GREEN}ptt_server.service started and enabled${NC}"

echo -e "${GREEN}Done${NC}"
