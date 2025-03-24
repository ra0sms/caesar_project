#!/usr/bin/python3
from wiringpi import GPIO
import wiringpi
import socket

SERVER_IP = '0.0.0.0'  # Listen to all interfaces
SERVER_PORT = 5001
PTT_PIN = 12

def read_allowed_ip(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
            if not content:
                print(f"File {filename} is empty. Using default IP.")
                return '0.0.0.0'
            return content
    except FileNotFoundError:
        print(f"File {filename} not found. Using default IP.")
        return '0.0.0.0'

ALLOWED_IP = read_allowed_ip('client_ip.cfg') 

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

wiringpi.wiringPiSetup()
wiringpi.pinMode(PTT_PIN, wiringpi.OUTPUT)

print(f"Waiting for {ALLOWED_IP}...")


try:
    while True:
        data, addr = sock.recvfrom(1024)
        sender_ip, sender_port = addr
        if sender_ip == ALLOWED_IP:
            data = data.decode().strip()

            if data == '1':
                #print("PTT ON")
                wiringpi.digitalWrite(PTT_PIN, GPIO.HIGH)
            elif data == '0':
                #print("PTT OFF")
                wiringpi.digitalWrite(PTT_PIN, GPIO.LOW)
            else:
                print(f"Unknown command: {data}")
        else:
            print(f"Data from unknown IP: {sender_ip}. Ignore.")


except KeyboardInterrupt:
    print("Stop")
finally:
    sock.close()
