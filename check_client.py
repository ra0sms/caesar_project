#!/usr/bin/python3

import subprocess
import time
from wiringpi import GPIO
import wiringpi

CONN_PIN = 11
wiringpi.wiringPiSetup()
wiringpi.pinMode(CONN_PIN, wiringpi.OUTPUT)

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

def check_ip_availability(ip_address):
    try:
        output = subprocess.run(["ping", "-c", "1", "-W", "1", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception as e:
        print(f"Ping error: {e}")
        return False

def monitor_ip(ip_address, check_interval=5):
    while True:
        if not check_ip_availability(ip_address):
            print(f"Client {ip_address} turn off")
            wiringpi.digitalWrite(CONN_PIN, GPIO.LOW)
        else:
            print(f"Client {ip_address} turn on")
            wiringpi.digitalWrite(CONN_PIN, GPIO.HIGH)
        time.sleep(check_interval)

if __name__ == "__main__":
    ip_file_path = "client_ip.cfg"
    ip_to_monitor = read_ip_from_file(ip_file_path)
    print(f"Monitoring: {ip_to_monitor}")
    check_interval = 1
    monitor_ip(ip_to_monitor, check_interval)
