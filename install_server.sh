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

echo -e "${GREEN}Installing wiringPO...${NC}"
cd wiringOP/
./build clean
./build
cd ../
cd wiringOP-Python/
python3 generate-bindings.py > bindings.i
python3 setup.py install
gpio readall


echo -e "${GREEN}Config ptt_server.service...${NC}"
cp ./ptt_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl start ptt_server.service
systemctl enable ptt_server.service
systemctl status ptt_server.service
echo -e "${GREEN}ptt_server.service started and enabled${NC}"

echo -e "${GREEN}Config cw_server.service...${NC}"
cp ./cw_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl start cw_server.service
systemctl enable cw_server.service
systemctl status cw_server.service
echo -e "${GREEN}cw_server.service started and enabled${NC}"


echo -e "${GREEN}Done${NC}"
