#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Updating...${NC}"
sudo apt-get update

echo -e "${GREEN}Upgrading...${NC}"
sudo apt-get upgrade -y

echo -e "${GREEN}Installing new packages...${NC}"
sudo apt-get install -y git make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools 

echo -e "${GREEN}Cleaning...${NC}"
sudo apt-get autoremove -y
sudo apt-get autoclean -y

echo -e "${GREEN}Done${NC}"
