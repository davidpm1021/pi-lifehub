# Pi Life Hub Voice Setup Instructions

## Install Voice Dependencies on Your Pi (192.168.86.36)

SSH into your Pi and run these commands:

### 1. Install System Audio Dependencies
```bash
# Update system packages
sudo apt update

# Install audio system libraries
sudo apt install -y portaudio19-dev python3-pyaudio libasound2-dev

# Install additional audio tools (optional)
sudo apt install -y alsa-utils pulseaudio
```

### 2. Install Python Voice Libraries
```bash
# Navigate to your pi-lifehub directory
cd /home/pi/pi-lifehub

# Activate virtual environment
source venv/bin/activate

# Install voice dependencies
pip install pyaudio==0.2.13 SpeechRecognition==3.10.1
```

### 3. Test Your Microphone
```bash
# Check if microphone is detected
arecord -l

# Test recording (press Ctrl+C to stop)
arecord -d 5 -f cd test.wav
aplay test.wav
```

### 4. Restart the Life Hub Service
```bash
# Restart the service to load voice modules
sudo systemctl restart lifehub

# Check service status
sudo systemctl status lifehub

# View logs
sudo journalctl -u lifehub -f
```

### 5. Test Voice Commands

Visit your dashboard: **http://192.168.86.36:8001/dashboard-enhanced.html**

**Available Voice Commands:**
- "Hey Hub, start 5 minute timer"
- "Hey Hub, start 10 minute timer" 
- "Hey Hub, start 25 minute timer"
- "Hey Hub, add todo wash dishes"
- "Hey Hub, add todo walk the dog"
- "Hey Hub, what's the weather"
- "Hey Hub, what time is it"

### 6. Test Voice API Directly
```bash
# Check voice service status
curl http://localhost:8001/api/voice/status

# Test single voice command
curl -X POST http://localhost:8001/api/voice/listen

# Start continuous listening
curl -X POST http://localhost:8001/api/voice/start
```

## Troubleshooting

### If Microphone Not Working:
```bash
# Check audio devices
lsusb | grep -i audio
cat /proc/asound/cards

# Set default audio device (if needed)
sudo nano /etc/asound.conf
# Add:
# pcm.!default {
#     type hw
#     card 1
# }
```

### If Voice Recognition Fails:
```bash
# Check internet connection (Google Speech Recognition needs internet)
ping google.com

# Verify microphone permissions
sudo usermod -a -G audio pi

# Check system logs
dmesg | grep -i audio
```

### If Service Won't Start:
```bash
# Check for missing dependencies
python3 -c "import pyaudio, speech_recognition; print('Voice dependencies OK!')"

# Manual service restart
sudo systemctl stop lifehub
sudo systemctl start lifehub
sudo systemctl status lifehub
```

## Voice Feature Status

Once installed, your voice features will include:

- **Wake Word**: "Hey Hub" to activate listening
- **Timer Commands**: Start quick timers with voice
- **Todo Commands**: Add tasks hands-free
- **Weather Commands**: Get weather updates
- **Time Commands**: Ask for current time
- **Continuous Listening**: Always-on voice detection

The voice module integrates with:
- ✅ Timer system (start timers)
- ✅ Todo system (add tasks) 
- ✅ Weather system (get conditions)
- ✅ Time system (current time)

Perfect for hands-free family dashboard control!