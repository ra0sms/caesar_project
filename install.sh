#!/bin/bash

echo "Updating..."
sudo apt-get update

echo "Upgrading..."
sudo apt-get upgrade -y

echo "Installing new packages..."
sudo apt-get install -y git make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools 

echo "Cleaning..."
sudo apt-get autoremove -y
sudo apt-get autoclean -y

echo "Done"
