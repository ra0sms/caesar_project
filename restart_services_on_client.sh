#!/bin/bash
systemctl restart audio_client.service
systemctl restart audio_server_on_client.service
systemctl restart check_server.service
systemctl restart client_ping_responce.service
systemctl restart ptt_client.service
