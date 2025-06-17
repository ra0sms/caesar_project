from flask import Flask, render_template_string, request
import os

app = Flask(__name__)
SPEAKER = 'Speaker'
MIC = 'numid=8'

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
</style>
"""

def get_volume_template(speaker_volume, mic_capture, active_page='volume'):
    active_volume = "active" if active_page == 'volume' else ""
    active_config = "active" if active_page == 'config' else ""
    
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
