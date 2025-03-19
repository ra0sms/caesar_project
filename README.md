## Control Automatic Environment for Sound And Radio (CAESAR Project)

![CAESAR_overview](docs/CAESAR_overview.png)

## Ports

* `UDP 5001` - PTT control
* `UDP 5002` - CW control
* `UDP 3001` - cat control via USB-TTL (`ttyUSB0`)
* `UDP 3002` - cat control via internal serial port (`ttyS1`)

Serial port - 19200 kb/s, 8N1

## Files

`create_ser2net_yaml.sh` - create config file `ser2net.yaml` and put in `/etc` (need `sudo`)



## Installation

Armbian img - https://ra0sms.com/wp-content/uploads/2025/03/Armbian_community_25.5.0_minimal.tar.gz



