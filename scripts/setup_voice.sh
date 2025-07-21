#!/bin/bash

# Pi Life Hub Voice Setup Script
# Installs and configures voice recognition capabilities

set -e  # Exit on any error

echo "🎤 Pi Life Hub Voice Setup"
echo "=========================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install system audio dependencies
echo "🔊 Installing system audio dependencies..."
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    alsa-utils \
    pulseaudio \
    usbutils

# Add user to audio group
echo "👤 Adding user to audio group..."
sudo usermod -a -G audio $(whoami)

# Navigate to project directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install Python voice dependencies
echo "📚 Installing Python voice dependencies..."
pip install --upgrade pip
pip install pyaudio==0.2.13 SpeechRecognition==3.10.1

# Test voice dependencies
echo "🧪 Testing voice dependencies..."
if python3 -c "import pyaudio, speech_recognition; print('✅ Voice dependencies installed successfully!')" 2>/dev/null; then
    echo "✅ Voice module ready!"
else
    echo "❌ Voice dependency installation failed"
    exit 1
fi

# Create audio test script
echo "🎙️ Creating audio test script..."
cat > "$PROJECT_DIR/scripts/test_microphone.sh" << 'EOF'
#!/bin/bash

echo "🎙️ Microphone Test"
echo "=================="

echo "📱 Available audio devices:"
arecord -l

echo ""
echo "🔊 Testing microphone recording (5 seconds)..."
echo "   Recording will start in 3 seconds..."
sleep 3
echo "   Recording now... (speak into microphone)"

arecord -d 5 -f cd -t wav test_recording.wav 2>/dev/null && echo "✅ Recording complete" || echo "❌ Recording failed"

if [ -f test_recording.wav ]; then
    echo "🔉 Playing back recording..."
    aplay test_recording.wav 2>/dev/null && echo "✅ Playback complete" || echo "❌ Playback failed"
    rm -f test_recording.wav
fi

echo ""
echo "🎤 USB microphones detected:"
lsusb | grep -i audio || echo "   No USB audio devices found"

echo ""
echo "🔧 Audio device information:"
cat /proc/asound/cards 2>/dev/null || echo "   No audio cards found"
EOF

chmod +x "$PROJECT_DIR/scripts/test_microphone.sh"

# Restart Life Hub service if it exists
if systemctl is-active --quiet lifehub.service 2>/dev/null; then
    echo "🔄 Restarting Life Hub service..."
    sudo systemctl restart lifehub.service
    sleep 2
elif pgrep -f "uvicorn.*8001" > /dev/null; then
    echo "🔄 Life Hub is running manually - restart recommended"
fi

# Test voice API
echo "🌐 Testing voice API..."
sleep 1
if curl -s http://localhost:8001/api/voice/status > /dev/null 2>&1; then
    echo "✅ Voice API is responding"
    echo "📊 Microphone status:"
    curl -s http://localhost:8001/api/voice/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8001/api/voice/status
else
    echo "⚠️ Voice API not responding - ensure Life Hub service is running"
fi

echo ""
echo "🎉 Voice setup complete!"
echo ""
echo "📋 What was configured:"
echo "   ✅ System audio dependencies installed"
echo "   ✅ Python voice libraries installed (pyaudio, SpeechRecognition)"
echo "   ✅ User added to audio group"
echo "   ✅ Microphone test script created"
echo ""
echo "🔄 Next steps:"
echo "   1. Logout and login again (for audio group to take effect)"
echo "   2. Plug in a USB microphone"
echo "   3. Test microphone: $PROJECT_DIR/scripts/test_microphone.sh"
echo "   4. Test voice API: $PROJECT_DIR/scripts/test_voice.sh"
echo "   5. Access dashboard: http://localhost:8001"
echo ""
echo "🗣️ Available voice commands:"
echo "   'Hey Hub, start 5 minute timer'"
echo "   'Hey Hub, start 10 minute timer'"
echo "   'Hey Hub, start 25 minute timer'"
echo "   'Hey Hub, add todo wash dishes'"
echo "   'Hey Hub, what's the weather'"
echo "   'Hey Hub, what time is it'"
echo ""
echo "🧪 Manual voice tests:"
echo "   Single command: curl -X POST http://localhost:8001/api/voice/listen"
echo "   Start listening: curl -X POST http://localhost:8001/api/voice/start"
echo "   Stop listening:  curl -X POST http://localhost:8001/api/voice/stop"
echo "   Check status:    curl http://localhost:8001/api/voice/status"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Check microphone: arecord -l"
echo "   - Test recording: arecord -d 5 test.wav && aplay test.wav"
echo "   - Check permissions: groups | grep audio"
echo "   - View logs: sudo journalctl -u lifehub.service -f"