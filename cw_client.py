#!/usr/bin/python3
import wiringpi
import socket
import time


CONFIG_FILE = 'server_ip.cfg'
SERVER_PORT = 5002
CW_PIN = 14
DEBOUNCE_DELAY = 0.01

def read_ip_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except Exception as e:
        print(f"Error reading: {e}")
        return None

def main():
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(CW_PIN, wiringpi.INPUT)
    server_ip = read_ip_from_file(CONFIG_FILE)
    if not server_ip:
        print("Using default IP: 192.168.0.201")
        server_ip = '192.168.0.201'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    button_state =  wiringpi.digitalRead(CW_PIN)
    try:
        print(f"PTT server is running {server_ip}:{SERVER_PORT}")
        print(f"Starting button state: {button_state}")
        
        while True:
            current_state = wiringpi.digitalRead(CW_PIN)
            
            if current_state != button_state:
                time.sleep(DEBOUNCE_DELAY)
                current_state = wiringpi.digitalRead(CW_PIN)
                
                if current_state != button_state:
                    button_state = current_state
                    send_value = 1 if button_state == 0 else 0
                    print(f"Current state: {button_state}")
                    sock.sendto(str(send_value).encode(), (server_ip, SERVER_PORT))
            
            #time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nFinished.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
