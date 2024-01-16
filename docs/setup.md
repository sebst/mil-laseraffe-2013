# WiFi Setup
- `sudo raspi-config`
- SSID: `seb.st iPhone 14 Pro`
- `sudo route del default gw 192.168.0.1`
- `sudo apt-get update && sudo apt-get install python3-opencv`

```
sudo route del default gw 192.168.0.1 && sudo apt-get update && sudo apt-get install -y python3-opencv
```

# PIs updated
## Setup 2 (201..210)
- 01: ✔️
- 02: ✔️
- 03: ✔️
- 04: ✔️
- 05: ✔️
- 06: ✔️
- 07: ✔️
- 08: ✔️
- 09: ✔️
- 10: ✔️

# SSH Key Copy
- `ssh-copy-id -i ~/.ssh/id_rsa 192.168.0.201` (https://www.ssh.com/academy/ssh/copy-id)
- If needs to be generated: `ssh-keygen -f ~/id_rsa -t ecdsa -b 521` (https://www.ssh.com/academy/ssh/keygen)


# Measurement 20240116-1245
- No detection on 202, 208, 210