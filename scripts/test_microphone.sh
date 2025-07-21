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