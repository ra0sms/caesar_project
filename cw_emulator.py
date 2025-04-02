#!/usr/bin/env python3
import wiringpi
import socket
import time
import re
from threading import Thread, Lock

class CWEmulator:
    def __init__(self):
        # Настройки GPIO
        self.gpio_pin = 14  # Физический пин 8 (WiringPi номер 15)

        # Настройки UDP
        self.udp_port = 3003

        # Параметры CW
        self.wpm = 15
        self.dot_duration = 1.2 / self.wpm
        self.dash_duration = 3 * self.dot_duration

        # Инициализация WiringPi
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self.gpio_pin, wiringpi.OUTPUT)

        # Таблица Морзе
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
            '9': '----.', ' ': '/'
        }

        # UDP сокет
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.udp_port))

        # Блокировка для потокобезопасности
        self.lock = Lock()
        self.running = True

    def update_timing(self):
        """Обновление таймингов"""
        self.dot_duration = 1.2 / self.wpm
        self.dash_duration = 3 * self.dot_duration

    def send_symbol(self, symbol):
        """Отправка символа Морзе"""
        with self.lock:
            wiringpi.digitalWrite(self.gpio_pin, wiringpi.HIGH)
            time.sleep(self.dot_duration if symbol == '.' else self.dash_duration)
            wiringpi.digitalWrite(self.gpio_pin, wiringpi.LOW)
            time.sleep(self.dot_duration)

    def send_text(self, text):
        """Отправка текста"""
        for char in text.upper():
            if char in self.morse_code:
                for symbol in self.morse_code[char]:
                    self.send_symbol(symbol)
                time.sleep(self.dot_duration * 2)  # Пауза между символами
            elif char == ' ':
                time.sleep(self.dot_duration * 4)  # Пауза между словами

    def process_command(self, cmd):
        """Обработка команд"""
        cmd = cmd.strip()

        # Установка скорости
        if re.match(r'^\d{1,2}$', cmd):
            self.wpm = max(5, min(99, int(cmd)))
            self.update_timing()
            return f"Speed set to {self.wpm} WPM"

        # Передача текста
        elif cmd.startswith('T'):
            Thread(target=self.send_text, args=(cmd[1:],), daemon=True).start()
            return f"Transmitting: {cmd[1:]}"

        # Статус
        elif cmd == 'S':
            return (
                f"Status: {self.wpm} WPM\n"
                f"GPIO: {self.gpio_pin}\n"
                f"UDP port: {self.udp_port}"
            )

        else:
            return "ERROR: Unknown command"

    def udp_listener(self):
        """Слушатель UDP-порта"""
        print(f"Listening on UDP port {self.udp_port}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                cmd = data.decode('ascii', errors='ignore')
                response = self.process_command(cmd)
                if response:
                    self.sock.sendto(response.encode(), addr)
            except Exception as e:
                print(f"UDP error: {e}")

    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        wiringpi.digitalWrite(self.gpio_pin, wiringpi.LOW)
        self.sock.close()
        print("CW Emulator stopped")

if __name__ == "__main__":
    emulator = CWEmulator()
    udp_thread = Thread(target=emulator.udp_listener)
    udp_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        emulator.cleanup()
