#!/bin/bash

# Audio settings
/usr/bin/amixer -c 0 cset numid=3 31

# Audio stream receive
socat -u udp-recv:5000 - | aplay -f S16_LE -r 44100 -c 1

