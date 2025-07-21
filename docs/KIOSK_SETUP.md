# Pi Life Hub Kiosk Mode Setup

This document provides comprehensive instructions for setting up the Pi Life Hub to automatically display in kiosk mode when the Raspberry Pi boots up.

## Overview

The kiosk mode setup includes:
- **Auto-startup**: Dashboard launches automatically on boot
- **Kiosk mode**: Full-screen browser without UI elements
- **Cursor hiding**: Mouse cursor hides when idle
- **Voice commands**: Hands-free interaction (optional)

## Current Configuration

- **Service Port**: 8001 (http://localhost:8001)
- **Backend**: FastAPI running via uvicorn
- **Frontend**: Static files served by backend
- **Browser**: Chromium in kiosk mode
- **Autostart**: XDG autostart desktop entries

## Quick Setup

### 1. Run the Kiosk Setup Script
```bash
cd ~/pi-lifehub
bash scripts/setup_kiosk_autostart.sh
```

### 2. Install Voice Support (Optional)
```bash
bash scripts/setup_voice.sh
```

### 3. Reboot to Test
```bash
sudo reboot
```

## Manual Setup Steps

### 1. Create Autostart Directory
```bash
mkdir -p ~/.config/autostart
```

### 2. Create Kiosk Mode Desktop Entry
File: `~/.config/autostart/lifehub-kiosk.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Pi Life Hub Kiosk
Comment=Launch Pi Life Hub dashboard in kiosk mode
Exec=/usr/bin/chromium-browser --kiosk --no-sandbox --disable-infobars --disable-extensions --disable-plugins --disable-web-security --disable-features=TranslateUI --disable-ipc-flooding-protection --disable-dev-shm-usage --no-first-run --disable-default-apps --disable-sync http://localhost:8001
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
Categories=Network;WebBrowser;
```

### 3. Create Cursor Hiding Entry
File: `~/.config/autostart/unclutter.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Unclutter
Comment=Hide mouse cursor when idle
Exec=unclutter -idle 3 -root
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
Categories=Utility;
```

### 4. Install Required Packages
```bash
sudo apt update
sudo apt install -y chromium-browser unclutter x11-xserver-utils
```

## Voice Commands Setup

### System Dependencies
```bash
sudo apt install -y portaudio19-dev python3-pyaudio libasound2-dev alsa-utils
sudo usermod -a -G audio $(whoami)
```

### Python Dependencies
```bash
# In virtual environment
pip install pyaudio==0.2.13 SpeechRecognition==3.10.1
```

### Available Voice Commands
- "Hey Hub, start 5 minute timer"
- "Hey Hub, start 10 minute timer" 
- "Hey Hub, start 25 minute timer"
- "Hey Hub, add todo wash dishes"
- "Hey Hub, what's the weather"
- "Hey Hub, what time is it"

## Testing

### Test Kiosk Setup
```bash
# Run comprehensive test
bash scripts/test_kiosk.sh

# Manual kiosk test
chromium-browser --kiosk http://localhost:8001
```

### Test Voice Functionality
```bash
# Run voice tests
bash scripts/test_voice.sh

# Test microphone
bash scripts/test_microphone.sh

# Test voice API
curl http://localhost:8001/api/voice/status
curl -X POST http://localhost:8001/api/voice/listen
```

### Test Service
```bash
# Check service status
sudo systemctl status lifehub.service

# Test API response
curl http://localhost:8001/api/time

# View logs
sudo journalctl -u lifehub.service -f
```

## Desktop Environment Compatibility

The autostart configuration works with:
- **LXDE** (default on Raspberry Pi OS Lite with Desktop)
- **GNOME** (Ubuntu Desktop)
- **XFCE** (Xubuntu)
- **KDE** (Kubuntu)
- **Any XDG-compliant desktop environment**

## Troubleshooting

### Dashboard Doesn't Auto-Start
1. Check if desktop entries exist:
   ```bash
   ls -la ~/.config/autostart/
   ```

2. Verify Chromium is installed:
   ```bash
   which chromium-browser
   ```

3. Test manual launch:
   ```bash
   chromium-browser --kiosk http://localhost:8001
   ```

### Service Not Responding
1. Check service status:
   ```bash
   sudo systemctl status lifehub.service
   ```

2. Check if port is in use:
   ```bash
   netstat -tlnp | grep 8001
   ```

3. Restart service:
   ```bash
   sudo systemctl restart lifehub.service
   ```

### Voice Commands Not Working
1. Check microphone connection:
   ```bash
   arecord -l
   lsusb | grep -i audio
   ```

2. Test recording:
   ```bash
   arecord -d 5 test.wav
   aplay test.wav
   ```

3. Check permissions:
   ```bash
   groups | grep audio
   ```

4. Check voice API:
   ```bash
   curl http://localhost:8001/api/voice/status
   ```

### Cursor Still Visible
1. Install unclutter:
   ```bash
   sudo apt install unclutter
   ```

2. Verify autostart entry exists:
   ```bash
   cat ~/.config/autostart/unclutter.desktop
   ```

## Advanced Configuration

### Custom Chromium Flags
Edit the kiosk desktop entry to add additional flags:
- `--disable-web-security`: Allow local file access
- `--disable-features=TranslateUI`: Disable translation prompts
- `--no-first-run`: Skip first-run setup
- `--disable-sync`: Disable Chrome sync
- `--kiosk`: Full-screen mode
- `--no-sandbox`: Required for some Pi configurations

### Screen Rotation
Add to `/boot/config.txt`:
```
display_rotate=1  # 90 degrees
display_rotate=2  # 180 degrees
display_rotate=3  # 270 degrees
```

### Touchscreen Calibration
Create `/etc/X11/xorg.conf.d/40-libinput.conf`:
```
Section "InputClass"
    Identifier "libinput touchscreen catchall"
    MatchIsTouchscreen "on"
    MatchDevicePath "/dev/input/event*"
    Driver "libinput"
    Option "Calibration" "0 800 0 480"
EndSection
```

## File Locations

### Configuration Files
- Kiosk autostart: `~/.config/autostart/lifehub-kiosk.desktop`
- Cursor hiding: `~/.config/autostart/unclutter.desktop`
- Service definition: `/etc/systemd/system/lifehub.service`

### Scripts
- Kiosk setup: `scripts/setup_kiosk_autostart.sh`
- Voice setup: `scripts/setup_voice.sh`
- Kiosk test: `scripts/test_kiosk.sh`
- Voice test: `scripts/test_voice.sh`
- Microphone test: `scripts/test_microphone.sh`

### Logs
- Service logs: `sudo journalctl -u lifehub.service`
- Application logs: `/var/log/pi-life-hub/lifehub.log`
- System logs: `/var/log/syslog`

## Security Considerations

- Chromium runs with `--no-sandbox` for Pi compatibility
- Local network access only (0.0.0.0:8001)
- No external authentication required
- Voice data sent to Google Speech Recognition API
- Database stored locally in SQLite

## Performance Optimization

### GPU Memory
Add to `/boot/config.txt`:
```
gpu_mem=128
```

### Disable Unnecessary Services
```bash
sudo systemctl disable bluetooth
sudo systemctl disable wifi-country
```

### Reduce Boot Time
Add to `/boot/cmdline.txt`:
```
quiet splash
```

## Backup and Recovery

### Backup Configuration
```bash
# Backup autostart configs
tar -czf kiosk-config-backup.tar.gz ~/.config/autostart/

# Backup service definition
sudo cp /etc/systemd/system/lifehub.service lifehub.service.backup
```

### Recovery
```bash
# Restore autostart configs
tar -xzf kiosk-config-backup.tar.gz -C ~/

# Restore service
sudo cp lifehub.service.backup /etc/systemd/system/lifehub.service
sudo systemctl daemon-reload
```

---

For additional help, check the troubleshooting section or run the test scripts to diagnose issues.