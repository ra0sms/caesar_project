## Control Automatic Environment for Sound And Radio (CAESAR Project)

![CAESAR_overview](docs/CAESAR_overview.png)  

## Overview

![Caesar_project_overview](docs/caesar_diagram_overview.jpg)  

The server and client connect to each other over the internet. Both are based on **Orange Pi Zero** boards.
All services start automatically after the OS boots. The following data is transmitted:  
* **Audio** in both directions – from the server to the client and vice versa. This is suitable for operating in FT8 or SSB modes.  
* **CAT protocol** transmission from the server to the client (```ser2net``` service).  
* **Telegraph keying** transmission via the Winkeyer protocol (also using the ```ser2net``` service).  
* **PTT signal** transmission from the client to the server to activate transmit (can use the RTS pin or a foot switch).  
Additionally, the client and server continuously check each other's availability using a UDP-based ping-like command.  

## Server part

![Caesar_project_server](docs/caesar_diagram_server.jpg)  

The transceiver connects to the server via an audio interface (requiring both audio input and output from the transceiver). This can be either a dedicated external interface or a simple sound card. The Orange Pi Zero has a built-in sound card, with audio input and output routed to the pin header (see [Orange Pi Zero pinout](#orange-pi-zero-pinout)):  
* **LINEOUTR & LINEOUTL** – Audio output  
* **MIC1P & MIC1N** – Audio input

Additionally, the PTT output of the server must be connected to the PTT input (TX GND) of the transceiver. On the Orange Pi Zero, this is Pin `wPI 12`. The PTT connection can be implemented using a transistor switch or an optocoupler.  
#### USB Connections
The Orange Pi Zero’s USB ports must be used to connect:
* The transceiver’s CAT interface  
* The Winkeyer telegraph key (e.g., [NanoKeyer](https://ra0sms.com/cw-key-k3ng/)).  

**Important sequence!**  
**First, plug in the CAT interface, then the Winkeyer.** 

Do not disconnect them until the installation is complete (see the [Installation](#installation)). The Orange Pi Zero has one built-in USB port, and a second USB port can be added using the pin header (pins **USB-DP2 & USB-DM2**).  
The status LED indicating the server-client connection is located on pin `wPi 11` (**CONNECTION LED**). It can be connected directly to the Orange Pi Zero.

## Client part

![Caesar_project_client](docs/caesar_diagram_client.jpg)  

The client can be used in two modes:  
1. **Standalone mode** (without a computer) – Only for audio and PTT signal transmission. In this case, the client is physically connected only to headphones, a microphone, and a foot pedal. This setup is suitable for SSB operation.  
2. **Computer-assisted mode** (for digital modes and telegraphy) – Let’s examine the second option in more detail.  
#### Audio and PTT Transmission on the Client Side
Audio transmission on the client uses the same method and built-in sound card as on the server. This part of the setup is identical. Unlike the server, the client’s PTT pin (`wPi 12`) acts as an input. It must be connected to:
* A foot switch (for manual TX activation).  
* The RTS signal from the first USB-UART adapter (for CAT-controlled PTT).

#### USB-UART Adapters and Serial Ports
Two USB-UART adapters are required:
* First adapter (**CAT protocol & PTT control via RTS**): Connected to `ttyS1`.
* Second adapter (**Winkeyer protocol**): Connected to `ttyS2`.
* **Wiring note**: The connections must be crossed (RX to TX and vice versa).
#### Orange Pi Zero Built-in UART Ports (only for the client)
The board has two native UART ports (`ttyS1` and `ttyS2`), which are used for:
* ttyS1 → CAT interface (first USB-UART adapter).  
* ttyS2 → Winkeyer (second USB-UART adapter).  
#### Key Clarifications
PTT Activation:
* The RTS signal from the CAT adapter triggers PTT automatically (e.g., via WSJT-X).  
* The foot switch provides manual override (grounds the PTT pin).  
* **Crossed Wiring:** Ensures proper UART communication (e.g., adapter’s TX → Orange Pi’s RX).  

**Serial port for CAT - 19200 kb/s, 8N1**   
**Serial port for WinKeyer - 1200 kb/s, 8N2**

#### Client Operation Instructions
 
* Open any logging program (e.g., JTDX, DXLog, TR4W).  
* Select CAT port (mapped to the first USB-UART adapter, e.g., `COM3` or` /dev/ttyUSB0`).  
* Select Winkeyer port (mapped to the second USB-UART adapter, e.g., `COM4` or `/dev/ttyUSB1`).  
* The client automatically exchanges data with the server and transceiver once ports are configured.  
* No manual intervention is needed for normal operation.  
* Auto-restart: All services reboot automatically after connection drops (e.g., network timeouts) and system reboots (client or server).  
* Winkeyer setup must be manually reinitialized in the logging software after a reboot.  
* CAT connection restores itself without user action.  

## Ports

* `UDP 5000` - Audio stream from server to client
* `UDP 5001` - PTT control
* `UDP 5002` - Audio stream from client to server
* `UDP 5003` - check connection from server to client
* `UDP 5004` - check connection from client to server
* `UDP 3001` - cat control via USB-TTL (`ttyUSB0`)
* `UDP 3002` - WinKeyer control via USB-TTL (`ttyUSB1`)  

Serial port for CAT - 19200 kb/s, 8N1  
Serial port for WinKeyer - 1200 kb/s, 8N2  

## Files

`install_server.sh` - install all dependencies for server  

## Installation

* First of all you need to create SD-card for your orange pi zero.  
 Here is the [Armbian img](http://ra0sms.com:8000/img/Armbian_community_25.5.0_minimal.tar.gz).  
You can create it with BalenaEltcher sotware - https://etcher.balena.io/  
After first Armbian starting (or ssh connection) you need to create user ```pi``` (don't forget about password)  
* All settings can be done via ```ssh``` connection (putty, for example, if you use Windows OS)  
* Connect to your orange pi via ```ssh```. You will be in ```HOME``` directory (```/home/pi/```).  
* Clone ```caesar_project``` from GitHub:  
   ``` bash
      sudo apt update
      sudo apt install git
      git clone https://github.com/ra0sms/caesar_project.git 
      cd caesar_project
   ```  
* Before the next step you need to connect CAT interface and winkeyer in USB ports server's orange pi zero.  
* To install server - run ```sudo ./install_server.sh```  
   If you see some errors it can be connect with USB to Serial interfaces.  
   By default the script uses names ```ttyUSB0``` and ```ttyUSB1```. In your case it can be different. So you need to correct ```fix_usb_ports.sh``` script. 
   ```bash
    ls /dev/tty*
    # find your names (something like ttyACM0)
    nano ./fix_usb_ports.sh
    # put your names instead of ttyUSB0 and ttyUSB1
    sudo ./fix_usb_ports.sh
   ```  
* To install client - run ```sudo ./install_client.sh```  
* Then you need to write IP addresses for ```server``` and ```client``` 
   ```bash
      nano ./server_ip.cfg 
      nano ./client_ip.cfg
   ```  
* If ```server``` and ```client``` are not in one local network you need to do port forwarding (see [Ports](#ports)) on your router settings.  
* Reboot both orange pi zero.  
* If everything is done rigth you will see that LEDs "connection" on both devices are turn ON.  

## Orange Pi zero pinout

wPi `pin 11` - LED "Connection"  
wPi `pin 12` - PTT input/output
![Orange-Pi-Zero-Pinout](docs/Orange-Pi-Zero-Pinout.png)  
![orange_pi_gpio_readall](docs/orange_pi_gpio_readall.png)




