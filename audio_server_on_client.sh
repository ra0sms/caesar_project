#!/bin/bash

# Чтение IP-адреса из файла
IP_FILE="/home/pi/caesar_project/server_ip.cfg"
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
/usr/bin/amixer -c 0 cset numid=7 6
/usr/bin/amixer -c 0 cset numid=18 on
/usr/bin/amixer -c 0 cset numid=8 6
/usr/bin/amixer -c 0 cset numid=13 off

# Audio stream
gst-launch-1.0   alsasrc device=hw:0 buffer-time=300000 latency-time=20000 !   audioconvert !   audioresample !   capsfilter caps="audio/x-raw,rate=48000,channels=1,format=S16LE" !   opusenc bitrate=24000 frame-size=20 complexity=0 !   rtpopuspay !   udpsink host=$IP_ADDRESS port=5002 sync=false

