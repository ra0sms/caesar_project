#!/bin/bash

# Audio settings
/usr/bin/amixer -c 0 cset numid=3 31

# Audio stream receive
gst-launch-1.0   udpsrc port=5000 caps="application/x-rtp,payload=96" !   rtpjitterbuffer latency=200 drop-on-latency=true !   queue max-size-time=20000000 leaky=downstream !   rtpopusdepay !   opusdec plc=true !   queue !   audioconvert !   queue !   alsasink sync=false


