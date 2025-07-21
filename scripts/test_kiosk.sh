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