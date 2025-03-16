#!/bin/bash

# Обновление списка пакетов
echo "Обновление списка пакетов..."
sudo apt-get update

# Обновление установленных пакетов
echo "Обновление установленных пакетов..."
sudo apt-get upgrade -y

# Установка новых пакетов
echo "Установка новых пакетов..."
sudo apt-get install -y git make gcc python3 python3-pip ser2net swig python3-dev python3-setuptools 

# Очистка кеша и удаление ненужных пакетов
echo "Очистка кеша и удаление ненужных пакетов..."
sudo apt-get autoremove -y
sudo apt-get autoclean -y

echo "Обновление и установка пакетов завершена!"
