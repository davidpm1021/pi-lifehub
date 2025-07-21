#!/bin/bash

# Raspberry Pi Life Hub Setup Script
# Run this script on your Pi 5 to install all dependencies and configure the system

set -e  # Exit on any error

echo "🍓 Setting up Raspberry Pi Life Hub..."
echo "This will install Python dependencies, configure autostart, and optimize for touchscreen use."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not present
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    chromium-browser \
    unclutter \
    x11-xserver-utils \
    sqlite3

# Create Python virtual environment
echo "🏗️ Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Make the backend executable
chmod +x backend/main.py

# Create systemd service for the Life Hub backend
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/lifehub.service > /dev/null << EOF
[Unit]
Description=Pi Life Hub Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-lifehub
Environment=PATH=/home/pi/pi-lifehub/venv/bin
ExecStart=/home/pi/pi-lifehub/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable lifehub.service
sudo systemctl start lifehub.service

# Configure autostart for kiosk mode
echo "🖥️ Configuring kiosk mode..."
mkdir -p /home/pi/.config/autostart

# Create autostart entry for Chromium in kiosk mode
tee /home/pi/.config/autostart/lifehub-kiosk.desktop > /dev/null << EOF
[Desktop Entry]
Type=Application
Name=Life Hub Kiosk
Exec=/usr/bin/chromium-browser --kiosk --no-sandbox --disable-infobars --disable-extensions --disable-plugins --disable-web-security --disable-features=TranslateUI --disable-ipc-flooding-protection --disable-dev-shm-usage --no-first-run --disable-default-apps --disable-sync http://localhost:8001
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Hide cursor when idle
tee /home/pi/.config/autostart/unclutter.desktop > /dev/null << EOF
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 1 -root
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Configure touchscreen calibration and orientation
echo "📱 Configuring touchscreen..."

# Create X11 config for touchscreen
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/40-libinput.conf > /dev/null << EOF
Section "InputClass"
    Identifier "libinput touchscreen catchall"
    MatchIsTouchscreen "on"
    MatchDevicePath "/dev/input/event*"
    Driver "libinput"
    Option "Calibration" "0 800 0 480"
EndSection
EOF

# Optimize Pi for performance
echo "⚡ Optimizing system performance..."

# Update config.txt for better performance
sudo tee -a /boot/config.txt > /dev/null << EOF

# Life Hub Optimizations
gpu_mem=128
disable_overscan=1
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Enable I2C and SPI for future sensors
dtparam=i2c_arm=on
dtparam=spi=on

# Touchscreen display
dtoverlay=rpi-ft5406
display_auto_detect=1
EOF

# Create a startup check script
tee /home/pi/pi-lifehub/scripts/health_check.sh > /dev/null << 'EOF'
#!/bin/bash

# Health check script for Life Hub
echo "🔍 Life Hub Health Check"

# Check if backend is running
if systemctl is-active --quiet lifehub.service; then
    echo "✅ Backend service is running"
else
    echo "❌ Backend service is not running"
    echo "   Try: sudo systemctl start lifehub.service"
fi

# Check if backend responds
if curl -s http://localhost:8001/api/time > /dev/null; then
    echo "✅ API is responding"
else
    echo "❌ API is not responding"
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage is healthy ($DISK_USAGE%)"
else
    echo "⚠️ Disk usage is high ($DISK_USAGE%)"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -lt 80 ]; then
    echo "✅ Memory usage is healthy ($MEM_USAGE%)"
else
    echo "⚠️ Memory usage is high ($MEM_USAGE%)"
fi

echo ""
echo "📊 System Status:"
echo "   Uptime: $(uptime -p)"
echo "   Temperature: $(vcgencmd measure_temp)"
echo "   Load: $(uptime | awk -F'load average:' '{print $2}')"
EOF

chmod +x /home/pi/pi-lifehub/scripts/health_check.sh

# Create update script
tee /home/pi/pi-lifehub/scripts/update.sh > /dev/null << 'EOF'
#!/bin/bash

# Update script for Life Hub
echo "🔄 Updating Life Hub..."

cd /home/pi/pi-lifehub

# Pull latest changes if git repo
if [ -d .git ]; then
    git pull
fi

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart lifehub.service

echo "✅ Update complete!"
EOF

chmod +x /home/pi/pi-lifehub/scripts/update.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Reboot your Pi: sudo reboot"
echo "2. The dashboard will auto-start in kiosk mode"
echo "3. Access via browser at: http://[PI_IP]:8001"
echo ""
echo "Useful commands:"
echo "  Health check: ~/pi-lifehub/scripts/health_check.sh"
echo "  Update system: ~/pi-lifehub/scripts/update.sh"
echo "  View logs: sudo journalctl -u lifehub.service -f"
echo "  Restart service: sudo systemctl restart lifehub.service"
echo ""
echo "🍓 Happy Life Hub-ing!"