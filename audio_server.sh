#!/bin/bash

# Чтение IP-адреса из файла
IP_FILE="/home/pi/caesar_project/client_ip.cfg"
if [[ ! -f "$IP_FILE" ]]; then
  echo "File was not found: $IP_FILE"
  exit 1
fi

IP_ADDRESS=$(cat "$IP_FILE" | tr -d '\n' | tr -d ' ')  # Удаляем лишние символы (например, переносы строк)
if [[ -z "$IP_ADDRESS" ]]; then
  echo "IP address was not found: $IP_FILE"
  exit 1
fi

# Audio settings
/usr/bin/amixer -c 0 cset numid=7 4
/usr/bin/amixer -c 0 cset numid=18 on
/usr/bin/amixer -c 0 cset numid=8 1
/usr/bin/amixer -c 0 cset numid=13 off

# Audio stream
arecord -D hw:0,0 -f S16_LE -r 48000 -c 1 --buffer-size=2048 --period-size=512 | socat - udp-sendto:$IP_ADDRESS:5000
