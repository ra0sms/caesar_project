## Control Automatic Environment for Sound And Radio (CAESAR Project)

![CAESAR_overview](docs/CAESAR_overview.png)

## Ports

* `UDP 5000` - Audio stream from server to client
* `UDP 5002` - Audio stream from client to server
* `UDP 5001` - PTT control
* `UDP 5003` - check connection from server to client
* `UDP 5004` - check connection from client to server
* `UDP 3001` - cat control via USB-TTL (`ttyUSB0`)
* `UDP 3002` - WinKeyer control via USB-TTL (`ttyUSB1`)

Serial port for CAT - 19200 kb/s, 8N1

Serial port for WinKeyer - 1200 kb/s, 8N2

## Files

`install_server.sh` - install all dependencies for server


## Installation



## Orange Pi zero pinout

wPi `pin 11` - LED "Connection"

wPi `pin 12` - PTT input/output

![Orange-Pi-Zero-Pinout](docs/caesar_diagram_overview.jpg)

![Orange-Pi-Zero-Pinout](docs/caesar_diagram_server.jpg)

![Orange-Pi-Zero-Pinout](docs/caesar_diagram_client.jpg)

![Orange-Pi-Zero-Pinout](docs/Orange-Pi-Zero-Pinout.png)

![orange_pi_gpio_readall](docs/orange_pi_gpio_readall.png)

