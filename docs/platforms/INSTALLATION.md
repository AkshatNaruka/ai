# Platform-Specific Installation Guide

SECI AI Assistant (Jarvis) can be installed on virtually any device. This guide provides platform-specific instructions.

## Table of Contents

- [Linux](#linux)
- [macOS](#macos)
- [Windows](#windows)
- [Raspberry Pi / ARM Devices](#raspberry-pi--arm-devices)
- [Android (Termux)](#android-termux)
- [Docker](#docker)
- [Cloud Deployment](#cloud-deployment)

---

## Linux

### Prerequisites
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Fedora/RHEL
sudo dnf install python3 python3-pip git

# Arch Linux
sudo pacman -S python python-pip git
```

### Installation
```bash
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python3 install.py
```

### Running as a Service
```bash
# Install systemd service
sudo cp systemd/jarvis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis

# Check status
sudo systemctl status jarvis
```

### Recommended Specs
- **Minimum**: 1GB RAM, 1 CPU core
- **Recommended**: 2GB+ RAM, 2+ CPU cores

---

## macOS

### Prerequisites
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11 git
```

### Installation
```bash
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python3 install.py
```

---

## Windows

### Prerequisites
1. Install Python 3.8+: https://www.python.org/downloads/
2. Install Git: https://git-scm.com/download/win

### Installation (PowerShell)
```powershell
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python install.py
```

---

## Raspberry Pi / ARM Devices

### Installation (Minimal Mode)
```bash
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python3 install.py --minimal
```

---

## Android (Termux)

### Prerequisites
1. Install Termux from F-Droid
2. Update packages:
```bash
pkg update
pkg upgrade
pkg install python git clang
```

### Installation
```bash
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python install.py --minimal
```

---

## Docker

```bash
docker build -t jarvis .
docker run -d -p 8000:8000 jarvis
```

For detailed platform-specific instructions, see the full documentation.
