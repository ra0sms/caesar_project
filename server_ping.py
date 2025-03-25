#!/usr/bin/python3
import socket
import time
from wiringpi import GPIO
import wiringpi

CONN_PIN = 11
UDP_PORT = 5004
TIMEOUT = 1.0
CHECK_INTERVAL = 1
MAGIC_PHRASE = b"PING_RESPONSE"

def read_ip_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            ip_address = file.read().strip()
            if not ip_address:
                raise ValueError("IP address not found or empty.")
            return ip_address
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        exit(1)
    except Exception as e:
        print(f"Reading error: {e}")
        exit(1)

def check_udp_availability(ip_address):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(TIMEOUT)
        sock.sendto(b"PING_REQUEST", (ip_address, UDP_PORT))
        try:
            data, addr = sock.recvfrom(1024)
            return data == MAGIC_PHRASE and addr[0] == ip_address
        except socket.timeout:
            return False
        finally:
            sock.close()
    except Exception as e:
        print(f"UDP check error: {e}")
        return False

def monitor_ip(ip_address, check_interval):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(CONN_PIN, wiringpi.OUTPUT)
    while True:
        if check_udp_availability(ip_address):
            print(f"Client {ip_address} is online")
            wiringpi.digitalWrite(CONN_PIN, GPIO.HIGH)
        else:
            print(f"Client {ip_address} is offline")
            wiringpi.digitalWrite(CONN_PIN, GPIO.LOW)
        
        time.sleep(check_interval)

if __name__ == "__main__":
    ip_file_path = "server_ip.cfg"
    ip_to_monitor = read_ip_from_file(ip_file_path)
    print(f"Monitoring UDP availability for: {ip_to_monitor}")
    monitor_ip(ip_to_monitor, CHECK_INTERVAL)
