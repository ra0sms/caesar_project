from flask import Flask, render_template_string, request
import os
import socket
import time
import threading
from waitress import serve

app = Flask(__name__)
SPEAKER = 'Speaker'
MIC = 'numid=8'

# UDP Ping configuration
UDP_PORT = 5004
#UDP_PORT = 5003
TIMEOUT = 1.0
CHECK_INTERVAL = 0.3
MAGIC_PHRASE = b"PING_RESPONSE"
SERVER_IP_FILE = "/home/pi/caesar_project/server_ip.cfg"
#SERVER_IP_FILE = "/home/pi/caesar_project/client_ip.cfg"

# Global variables for status
current_rtt = None
last_update = None
status_active = False
status_thread = None

COMMON_STYLE = """
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
        color: #333;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
    }
    .control-group {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h2 {
        color: #3498db;
        margin-top: 0;
    }
    input[type="range"] {
        width: 100%;
        height: 10px;
        margin: 15px 0;
        -webkit-appearance: none;
        background: #ecf0f1;
        border-radius: 5px;
    }
    input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 25px;
        height: 25px;
        background: #3498db;
        border-radius: 50%;
        cursor: pointer;
    }
    button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s;
        margin-right: 10px;
    }
    button:hover {
        background-color: #2980b9;
    }
    .value-display {
        font-size: 18px;
        margin-top: 10px;
        padding: 10px;
        background-color: #ecf0f1;
        border-radius: 5px;
        text-align: center;
    }
    .container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    textarea {
        width: 100%;
        height: 40px;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-family: monospace;
        margin-bottom: 15px;
    }
    .nav {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .nav-button {
        padding: 10px 20px;
        margin: 0 5px;
    }
    .active {
        background-color: #2980b9;
        font-weight: bold;
    }
    .service-button {
        background-color: #e74c3c;
    }
    .service-button:hover {
        background-color: #c0392b;
    }
    .status-display {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    .good {
        color: #27ae60;
    }
    .warning {
        color: #f39c12;
    }
    .bad {
        color: #e74c3c;
    }
    .timestamp {
        font-size: 14px;
        color: #7f8c8d;
        text-align: center;
    }
</style>
"""

def start_status_monitoring():
    global status_active, status_thread
    if not status_active:
        status_active = True
        status_thread = threading.Thread(target=update_status)
        status_thread.daemon = True
        status_thread.start()

@app.before_first_request
def initialize():
    start_status_monitoring()


def get_ip_from_file():
    try:
        with open(SERVER_IP_FILE, 'r') as f:
            ip = f.read().strip()
            if not ip:
                raise ValueError("IP address is empty")
            return ip
    except:
        return None

def measure_udp_rtt(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(TIMEOUT)
            start = time.perf_counter()
            s.sendto(b"PING_REQUEST", (ip, UDP_PORT))
            data, addr = s.recvfrom(1024)
            if data == MAGIC_PHRASE and addr[0] == ip:
                return (time.perf_counter() - start) * 1000  # ms
    except:
        return None

def update_status():
    global current_rtt, last_update, status_active
    while status_active:
        ip = get_ip_from_file()
        if ip:
            rtt = measure_udp_rtt(ip)
            current_rtt = rtt
            last_update = time.strftime("%H:%M:%S")
        else:
            current_rtt = None
            last_update = "No server IP configured"
        time.sleep(CHECK_INTERVAL)

def start_status_monitoring():
    global status_active, status_thread
    if not status_active:
        status_active = True
        status_thread = threading.Thread(target=update_status)
        status_thread.daemon = True
        status_thread.start()

def get_volume_template(speaker_volume, mic_capture, active_page='volume'):
    active_volume = "active" if active_page == 'volume' else ""
    active_config = "active" if active_page == 'config' else ""
    active_status = "active" if active_page == 'status' else ""
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAESAR Volume Control</title>
    {COMMON_STYLE}
</head>
<body>
    <div class="container">
        <h1>CAESAR Control Panel</h1>
        
        <div class="nav">
            <a href="/"><button class="nav-button {active_volume}">Volume Control</button></a>
            <a href="/config"><button class="nav-button {active_config}">Configuration</button></a>
            <a href="/status"><button class="nav-button {active_status}">Status</button></a>
        </div>
        
        <form method="post">
            <div class="control-group">
                <h2>Speaker Volume</h2>
                <input type="range" name="speaker_volume" min="0" max="100" value="{speaker_volume}">
                <div class="value-display">{speaker_volume}%</div>
                <button type="submit" name="action" value="set_speaker">Set Speaker</button>
            </div>
            
            <div class="control-group">
                <h2>Microphone Level</h2>
                <input type="range" name="mic_capture" min="0" max="100" value="{mic_capture}">
                <div class="value-display">{mic_capture}%</div>
                <button type="submit" name="action" value="set_mic">Set Capture</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

def get_config_template(server_config, client_config, active_page='config', message=None):
    active_volume = "active" if active_page == 'volume' else ""
    active_config = "active" if active_page == 'config' else ""
    active_status = "active" if active_page == 'status' else ""
    
    message_html = f'<div class="value-display" style="color:#27ae60;margin-bottom:20px;">{message}</div>' if message else ''
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAESAR Configuration</title>
    {COMMON_STYLE}
</head>
<body>
    <div class="container">
        <h1>CAESAR Control Panel</h1>
        
        <div class="nav">
            <a href="/"><button class="nav-button {active_volume}">Volume Control</button></a>
            <a href="/config"><button class="nav-button {active_config}">Configuration</button></a>
            <a href="/status"><button class="nav-button {active_status}">Status</button></a>
        </div>
        
        {message_html}
        
        <form method="post">
            <div class="control-group">
                <h2>Server IP Configuration</h2>
                <textarea name="server_config">{server_config}</textarea>
                <button type="submit" name="action" value="save_server">Save Server Config</button>
            </div>
            
            <div class="control-group">
                <h2>Client IP Configuration</h2>
                <textarea name="client_config">{client_config}</textarea>
                <button type="submit" name="action" value="save_client">Save Client Config</button>
            </div>
            
            <div class="control-group">
                <button type="submit" name="action" value="restart_services" class="service-button">Restart Services</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

def get_status_template(active_page='status'):
    active_volume = "active" if active_page == 'volume' else ""
    active_config = "active" if active_page == 'config' else ""
    active_status = "active" if active_page == 'status' else ""
    
    if current_rtt is None:
        status_html = '<div class="status-display bad">No connection</div>'
    else:
        if current_rtt < 50:
            status_class = "good"
        elif current_rtt < 100:
            status_class = "warning"
        else:
            status_class = "bad"
        status_html = f'<div class="status-display {status_class}">{current_rtt:.1f} ms</div>'
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAESAR Status</title>
    {COMMON_STYLE}
    <meta http-equiv="refresh" content="1">
</head>
<body>
    <div class="container">
        <h1>CAESAR Control Panel</h1>
        
        <div class="nav">
            <a href="/"><button class="nav-button {active_volume}">Volume Control</button></a>
            <a href="/config"><button class="nav-button {active_config}">Configuration</button></a>
            <a href="/status"><button class="nav-button {active_status}">Status</button></a>
        </div>
        
        <div class="control-group">
            <h2>Server Connection Status</h2>
            {status_html}
            <div class="timestamp">Last update: {last_update}</div>
        </div>
    </div>
</body>
</html>
"""

def percent_to_alsa(vol_percent):
    """Convert percentage (0-100) to ALSA value (0-16)"""
    return min(16, max(0, round(float(vol_percent) * 16 / 100)))

def alsa_to_percent(alsa_value):
    """Convert ALSA value (0-16) to percentage (0-100)"""
    return min(100, max(0, round(float(alsa_value) * 100 / 16)))

def get_mic_value():
    """Get current mic capture value from ALSA"""
    raw = os.popen(
        f"amixer cget {MIC} | grep -o 'values=[0-9]*' | cut -d= -f2 | tac | head -n 1"
    ).read().strip()
    return int(raw) if raw.isdigit() else 8  # Default to 8 (50%)

def get_speaker_volume():
    """Get current speaker volume from ALSA"""
    raw = os.popen(
        f"amixer get {SPEAKER} | grep -o '[0-9]*%' | head -1"
    ).read().strip()
    return raw[:-1] if raw else "50"  # Default to 50%

def read_config_file(path):
    """Read configuration file content"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ""

def write_config_file(path, content):
    """Write content to configuration file"""
    with open(path, 'w') as f:
        f.write(content)

@app.route("/", methods=["GET", "POST"])
def index():
    speaker_vol = get_speaker_volume()
    mic_alsa = get_mic_value()
    mic_capture_display = alsa_to_percent(mic_alsa)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "set_speaker":
            speaker_vol = request.form.get("speaker_volume", speaker_vol)
            os.system(f"amixer set {SPEAKER} {speaker_vol}%")
        elif action == "set_mic":
            mic_capture_display = request.form.get("mic_capture", mic_capture_display)
            alsa_value = percent_to_alsa(mic_capture_display)
            os.system(f"amixer cset {MIC} {alsa_value}")
            mic_alsa = alsa_value

    return get_volume_template(speaker_vol, mic_capture_display, 'volume')

@app.route("/config", methods=["GET", "POST"])
def config_editor():
    server_config = read_config_file("/home/pi/caesar_project/server_ip.cfg")
    client_config = read_config_file("/home/pi/caesar_project/client_ip.cfg")
    message = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_server":
            server_config = request.form.get("server_config", "")
            write_config_file("/home/pi/caesar_project/server_ip.cfg", server_config)
            message = "Server configuration saved successfully!"
        elif action == "save_client":
            client_config = request.form.get("client_config", "")
            write_config_file("/home/pi/caesar_project/client_ip.cfg", client_config)
            message = "Client configuration saved successfully!"
        elif action == "restart_services":
            os.system("sudo /home/pi/caesar_project/restart_services_on_client.sh")
            message = "Services restarted successfully!"

    return get_config_template(server_config, client_config, 'config', message)

@app.route("/status")
def status_page():
    return get_status_template('status')

if __name__ == "__main__":
    # При запуске через Waitress этот код не выполняется, поэтому
    # используем декоратор @app.before_first_request
    if os.environ.get('WAITRESS') != '1':
        start_status_monitoring()
        app.run(host="0.0.0.0", port=8080)
    else:
        serve(app, host="0.0.0.0", port=8080)
