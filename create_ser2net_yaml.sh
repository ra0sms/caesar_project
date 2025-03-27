#!/bin/bash

# Получаем текущий IP-адрес компьютера
CURRENT_IP=$(hostname -I | awk '{print $1}')

# Шаблон конфигурации ser2net
CONFIG_TEMPLATE="%YAML 1.1
---
# This is a ser2net configuration file, tailored to be rather
# simple.
#
# Find detailed documentation in ser2net.yaml(5)
# A fully featured configuration file is in
# /usr/share/doc/ser2net/examples/ser2net.yaml.gz
# 
# If you find your configuration more useful than this very simple
# one, please submit it as a bugreport

define: &banner \\r\\nser2net port \\p device \\d [\\B] (Debian GNU/Linux)\\r\\n\\r\\n

connection: &con0096
    accepter: udp,${CURRENT_IP},3001
    enable: on
    options:
      banner: *banner
      kickolduser: true
      telnet-brk-on-sync: true
    connector: serialdev,
              /dev/ttyCAT,
              19200n81,local

connection: &con1096
    accepter: udp,${CURRENT_IP},3002
    enable: on
    options:
      banner: *banner
      kickolduser: true
      telnet-brk-on-sync: true
    connector: serialdev,
              /dev/ttyWK,
              1200n82,local
"

# Сохраняем конфигурацию в файл
echo "$CONFIG_TEMPLATE" > /etc/ser2net.yaml
sudo service ser2net restart

echo "File ser2net_config.yaml was created with IP: ${CURRENT_IP}"
