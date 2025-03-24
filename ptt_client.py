#!/usr/bin/python3
from wiringpi import GPIO
import wiringpi
import socket
import time

SERVER_IP = '192.168.0.201'  # Listen to all interfaces
SERVER_PORT = 5001
PTT_PIN = 12
button_state = 0
i = 0

wiringpi.wiringPiSetup()
wiringpi.pinMode(PTT_PIN, wiringpi.INPUT)


# Создание UDP сокета
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Отправка состояния кнопки
try:
    while True:
        if wiringpi.digitalRead(PTT_PIN) and button_state == 1:
            print("Send 1")
            button_state = 0
            sock.sendto(str(button_state).encode(), (SERVER_IP, SERVER_PORT))
        if not wiringpi.digitalRead(PTT_PIN) and button_state == 0:
            print("Send 0")
            button_state = 1
            sock.sendto(str(button_state).encode(), (SERVER_IP, SERVER_PORT)) 
except KeyboardInterrupt:
    print("Программа завершена.")
finally:
    sock.close()
