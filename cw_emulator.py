#!/usr/bin/env python3
import time
import gpiozero as gpio
import socket
from threading import Thread, Lock
import re

class CWEmulator:
    def __init__(self):
        # Hardware settings
        self.gpio_pin = 14          # GPIO14 (физический пин 8)
        self.udp_port = 3003        # Порт для ser2net

        # CW parameters
        self.wpm = 15               # Скорость (WPM)
        self.dot_duration = 1.2 / self.wpm
        self.dash_duration = 3 * self.dot_duration
        self.symbol_space = self.dot_duration

        # Morse code
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

        # Инициализация
        self.gpio = gpio.DigitalOutputDevice(self.gpio_pin)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('0.0.0.0', self.udp_port))
        self.lock = Lock()
        self.running = True

    def update_timing(self):
        """Обновление таймингов при изменении скорости"""
        self.dot_duration = 1.2 / self.wpm
        self.dash_duration = 3 * self.dot_duration
        self.symbol_space = self.dot_duration

    def send_symbol(self, symbol):
        """Отправка точки или тире"""
        with self.lock:
            self.gpio.on()
            time.sleep(self.dot_duration if symbol == '.' else self.dash_duration)
            self.gpio.off()
            time.sleep(self.symbol_space)

    def send_text(self, text):
        """Отправка текста"""
        for char in text.upper():
            if char in self.morse_code:
                for symbol in self.morse_code[char]:
                    self.send_symbol(symbol)
                time.sleep(self.symbol_space * 2)  # Пауза между символами
            elif char == ' ':
                time.sleep(self.symbol_space * 4)  # Пауза между словами

    def process_command(self, command):
        """Обработка Winkeyer-команд"""
        command = command.strip()

        # Установка скорости (0-99)
        if re.match(r'^\d{1,2}$', command):
            self.wpm = max(5, min(99, int(command)))
            self.update_timing()
            print(f"Скорость установлена: {self.wpm} WPM")

        # Передача текста (T...)
        elif command.startswith('T'):
            text = command[1:]
            print(f"Передача: {text}")
            Thread(target=self.send_text, args=(text,), daemon=True).start()

        # Статус (S)
        elif command == 'S':
            status = (
                f"Текущие настройки:\n"
                f"Скорость: {self.wpm} WPM\n"
                f"GPIO: {self.gpio_pin}\n"
                f"UDP-порт: {self.udp_port}"
            )
            print(status)

    def udp_listener(self):
        """Прослушивание UDP-порта"""
        print(f"Ожидание Winkeyer-команд на UDP-порту {self.udp_port}...")

        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                command = data.decode('ascii', errors='ignore').strip()
                if command:
                    print(f"Команда от {addr}: {command}")
                    self.process_command(command)

            except Exception as e:
                print(f"Ошибка UDP: {e}")

    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        self.gpio.off()
        self.udp_socket.close()
        print("Эмулятор остановлен")

if __name__ == "__main__":
    emulator = CWEmulator()
    udp_thread = Thread(target=emulator.udp_listener, daemon=True)
    udp_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        emulator.cleanup()
