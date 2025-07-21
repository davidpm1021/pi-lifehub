#!/bin/bash

# Pi Life Hub Kiosk Autostart Setup Script
# This script sets up auto-startup for the Pi Life Hub dashboard in kiosk mode

set -e  # Exit on any error

echo "🖥️ Setting up Pi Life Hub Kiosk Mode Auto-Startup..."

# Get the current user
USER=$(whoami)
HOME_DIR="/home/$USER"

# Create autostart directory
echo "📁 Creating autostart directory..."
mkdir -p "$HOME_DIR/.config/autostart"

# Create kiosk mode autostart entry
echo "🌐 Creating kiosk mode autostart entry..."
cat > "$HOME_DIR/.config/autostart/lifehub-kiosk.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Pi Life Hub Kiosk
Comment=Launch Pi Life Hub dashboard in kiosk mode
Exec=/usr/bin/chromium-browser --kiosk --no-sandbox --disable-infobars --disable-extensions --disable-plugins --disable-web-security --disable-features=TranslateUI --disable-ipc-flooding-protection --disable-dev-shm-usage --no-first-run --disable-default-apps --disable-sync --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-background-networking http://localhost:8001
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
Categories=Network;WebBrowser;
EOF

# Create cursor hiding autostart entry
echo "🖱️ Creating cursor hiding autostart entry..."
cat > "$HOME_DIR/.config/autostart/unclutter.desktop" << 'EOF'
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
EOF

# Make desktop files executable
chmod +x "$HOME_DIR/.config/autostart/lifehub-kiosk.desktop"
chmod +x "$HOME_DIR/.config/autostart/unclutter.desktop"

# Check if required packages are installed
echo "📦 Checking required packages..."

# Check for chromium browser
if ! command -v chromium-browser &> /dev/null; then
    echo "⚠️ Chromium browser not found. Installing..."
    sudo apt update
    sudo apt install -y chromium-browser
fi

# Check for unclutter
if ! command -v unclutter &> /dev/null; then
    echo "⚠️ Unclutter not found. Installing..."
    sudo apt install -y unclutter
fi

# Check for X11 utilities
if ! command -v xset &> /dev/null; then
    echo "⚠️ X11 utilities not found. Installing..."
    sudo apt install -y x11-xserver-utils
fi

# Create a test script
echo "🧪 Creating test script..."
cat > "$HOME_DIR/pi-lifehub/scripts/test_kiosk.sh" << 'EOF'
#!/bin/bash

# Test script for kiosk mode setup
echo "🧪 Testing Pi Life Hub Kiosk Setup..."

# Check if Life Hub service is running
if systemctl is-active --quiet lifehub.service 2>/dev/null || pgrep -f "uvicorn.*8001" > /dev/null; then
    echo "✅ Life Hub service is running"
else
    echo "❌ Life Hub service is not running"
    echo "   Check: sudo systemctl status lifehub.service"
    echo "   Or manually: cd ~/pi-lifehub && python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001"
fi

# Check if service responds
if curl -s http://localhost:8001/api/time > /dev/null 2>&1; then
    echo "✅ Life Hub API is responding on port 8001"
else
    echo "❌ Life Hub API is not responding on port 8001"
fi

# Check autostart files
if [ -f "$HOME/.config/autostart/lifehub-kiosk.desktop" ]; then
    echo "✅ Kiosk autostart file exists"
else
    echo "❌ Kiosk autostart file missing"
fi

if [ -f "$HOME/.config/autostart/unclutter.desktop" ]; then
    echo "✅ Cursor hiding autostart file exists"
else
    echo "❌ Cursor hiding autostart file missing"
fi

# Check required packages
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium browser is installed"
else
    echo "❌ Chromium browser is not installed"
fi

if command -v unclutter &> /dev/null; then
    echo "✅ Unclutter is installed"
else
    echo "❌ Unclutter is not installed"
fi

# Test voice functionality
echo ""
echo "🎤 Testing voice functionality..."
curl -s http://localhost:8001/api/voice/status | python3 -m json.tool

echo ""
echo "📋 Desktop Environment Info:"
echo "   Desktop Session: $DESKTOP_SESSION"
echo "   XDG Desktop: $XDG_CURRENT_DESKTOP"
echo "   Display: $DISPLAY"

echo ""
echo "🔄 To manually test kiosk mode:"
echo "   chromium-browser --kiosk http://localhost:8001"
echo ""
echo "📱 To test in windowed mode:"
echo "   chromium-browser --new-window http://localhost:8001"
EOF

chmod +x "$HOME_DIR/pi-lifehub/scripts/test_kiosk.sh"

echo ""
echo "🎉 Kiosk mode autostart setup complete!"
echo ""
echo "📋 What was configured:"
echo "   ✅ Autostart directory created: $HOME_DIR/.config/autostart/"
echo "   ✅ Kiosk mode desktop entry: lifehub-kiosk.desktop"
echo "   ✅ Cursor hiding desktop entry: unclutter.desktop"
echo "   ✅ Test script created: scripts/test_kiosk.sh"
echo ""
echo "🔄 Next steps:"
echo "   1. Reboot your Pi to test autostart: sudo reboot"
echo "   2. Or manually test: $HOME_DIR/pi-lifehub/scripts/test_kiosk.sh"
echo "   3. Dashboard will open at: http://localhost:8001"
echo ""
echo "🎛️ Manual kiosk test:"
echo "   chromium-browser --kiosk http://localhost:8001"
echo ""
echo "🔧 Troubleshooting:"
echo "   - View autostart logs: journalctl --user -u lifehub-kiosk"
echo "   - Check service: sudo systemctl status lifehub.service"
echo "   - Test API: curl http://localhost:8001/api/time"