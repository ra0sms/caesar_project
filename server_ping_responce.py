#!/usr/bin/python3
import socket

UDP_PORT = 5004
RESPONSE_PHRASE = b"PING_RESPONSE"

def run_udp_responder():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_PORT))
    
    print(f"UDP responder started on port {UDP_PORT}")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            
            # Если получен запрос "PING_REQUEST"
            if data == b"PING_REQUEST":
                print(f"Received ping from {addr[0]}")
                sock.sendto(RESPONSE_PHRASE, addr)
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        sock.close()

if __name__ == "__main__":
    run_udp_responder()
