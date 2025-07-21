#!/bin/bash

# Voice Module Test Script for Pi Life Hub
# Tests microphone detection, voice dependencies, and API endpoints

echo "🎤 Pi Life Hub Voice Module Test"
echo "================================"

# Test 1: Check if voice dependencies are installed
echo ""
echo "📦 Testing voice dependencies..."
if python3 -c "import pyaudio, speech_recognition; print('✅ Voice dependencies available!')" 2>/dev/null; then
    DEPS_OK=true
else
    echo "❌ Voice dependencies missing"
    echo "   Install with: pip install pyaudio==0.2.13 SpeechRecognition==3.10.1"
    DEPS_OK=false
fi

# Test 2: Check system audio
echo ""
echo "🔊 Testing system audio..."
if command -v arecord &> /dev/null; then
    echo "✅ ALSA audio tools available"
    echo "📱 Audio devices:"
    arecord -l 2>/dev/null || echo "   No recording devices found"
else
    echo "❌ ALSA audio tools not found"
    echo "   Install with: sudo apt install alsa-utils"
fi

# Test 3: Check USB audio devices
echo ""
echo "🔌 Checking USB audio devices..."
if lsusb | grep -i audio > /dev/null; then
    echo "✅ USB audio devices found:"
    lsusb | grep -i audio
else
    echo "⚠️ No USB audio devices detected"
    echo "   Plug in a USB microphone for voice commands"
fi

# Test 4: Test Life Hub voice API
echo ""
echo "🌐 Testing Life Hub voice API..."
if curl -s http://localhost:8001/api/voice/status > /dev/null 2>&1; then
    echo "✅ Voice API is responding"
    echo "📊 Microphone status:"
    curl -s http://localhost:8001/api/voice/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8001/api/voice/status
else
    echo "❌ Voice API not responding"
    echo "   Check if Life Hub service is running: systemctl status lifehub.service"
fi

# Test 5: Test voice commands (if everything is working)
if [ "$DEPS_OK" = true ]; then
    echo ""
    echo "🗣️ Available voice commands:"
    echo "   'Hey Hub, start 5 minute timer'"
    echo "   'Hey Hub, start 10 minute timer'"
    echo "   'Hey Hub, start 25 minute timer'"
    echo "   'Hey Hub, add todo wash dishes'"
    echo "   'Hey Hub, what's the weather'"
    echo "   'Hey Hub, what time is it'"
    
    echo ""
    echo "🧪 To test voice recognition manually:"
    echo "   curl -X POST http://localhost:8001/api/voice/listen"
    echo ""
    echo "🔄 To start continuous listening:"
    echo "   curl -X POST http://localhost:8001/api/voice/start"
    echo ""
    echo "⏹️ To stop listening:"
    echo "   curl -X POST http://localhost:8001/api/voice/stop"
fi

# Test 6: Check audio permissions
echo ""
echo "👤 Checking audio permissions..."
if groups | grep -q audio; then
    echo "✅ User is in audio group"
else
    echo "⚠️ User not in audio group"
    echo "   Add with: sudo usermod -a -G audio $(whoami)"
    echo "   Then logout and login again"
fi

# Test 7: Internet connectivity (needed for Google Speech Recognition)
echo ""
echo "🌍 Testing internet connectivity..."
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✅ Internet connection available"
    echo "   Google Speech Recognition will work"
else
    echo "❌ No internet connection"
    echo "   Voice recognition requires internet for Google Speech API"
fi

echo ""
echo "📋 Voice Setup Summary:"
echo "======================="

if [ "$DEPS_OK" = true ]; then
    echo "✅ Python dependencies: OK"
else
    echo "❌ Python dependencies: Missing"
fi

if lsusb | grep -i audio > /dev/null; then
    echo "✅ USB microphone: Detected"
else
    echo "⚠️ USB microphone: Not detected"
fi

if curl -s http://localhost:8001/api/voice/status | grep -q '"connected":true'; then
    echo "✅ Voice service: Connected"
elif curl -s http://localhost:8001/api/voice/status > /dev/null 2>&1; then
    echo "⚠️ Voice service: Available but no microphone"
else
    echo "❌ Voice service: Not responding"
fi

echo ""
echo "🔧 For complete voice setup, run:"
echo "   bash /home/$(whoami)/pi-lifehub/scripts/setup_voice.sh"