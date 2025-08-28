#!/bin/bash

sysctl -w net.ipv4.udp_rmem_min=4096
echo "26214400" | sudo tee /proc/sys/net/core/rmem_max
echo "26214400" | sudo tee /proc/sys/net/core/wmem_max

gst-launch-1.0   udpsrc port=5000 buffer-size=65536 caps="application/x-rtp,payload=96,clock-rate=48000,encoding-name=OPUS" !   rtpjitterbuffer latency=100 drop-on-latency=false do-lost=false !   queue max-size-time=50000000 leaky=downstream !   rtpopusdepay !   opusdec plc=false use-inband-fec=true !   queue !   audioconvert !   queue !   alsasink device=hw:0 buffer-time=100000 latency-time=1000 sync=false

