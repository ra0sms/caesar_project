#!/bin/sh

CONFIG_FILE="server_ip.cfg"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: File $CONFIG_FILE not found"
  exit 1
fi

SERVER_IP=$(head -n 1 "$CONFIG_FILE" | tr -d '\r\n')

if [ -z "$SERVER_IP" ]; then
  echo "Error: IP address not found in $CONFIG_FILE"
  exit 1
fi

if ! echo "$SERVER_IP" | grep -Eq '^([0-9]{1,3}\.){3}[0-9]{1,3}$'; then
  echo "Error: incorrect IP $CONFIG_FILE: $SERVER_IP"
  exit 1
fi

echo "Using IP address: $SERVER_IP"

exec socat -d -d \
  "UDP:$SERVER_IP:3002" \
  "/dev/ttyS2,raw,echo=0,b1200,cs8,parenb=0,cstopb=1"
