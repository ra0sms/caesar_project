#!/bin/bash
systemctl restart audio_server.service
systemctl restart audio_client_on_server.service
systemctl restart check_client.service
systemctl restart server_ping_responce.service
systemctl restart ptt_server.service
alsactl store