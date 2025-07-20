# Pi Life Hub Setup Instructions

## 1. OpenWeather API Setup

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Set environment variable on your Pi:

```bash
# Add to ~/.bashrc or /etc/environment
export OPENWEATHER_API_KEY="922a6d6d103ceaf2883dc81cbf75bf53"
export WEATHER_LOCATION="Medford,NJ,US"
```

5. Test the weather API:
```bash
curl "http://localhost:8001/api/weather/current"
```

## 2. Photo Configuration Options

### Option A: Local Photos (Recommended - Simple)
```bash
# Create photo directory on Pi
mkdir -p /home/pi/Photos
mkdir -p /home/pi/Photos/thumbnails

# Copy your photos to the directory
# The system will auto-scan and create thumbnails

# Set environment variables (optional)
export PHOTOS_DIRECTORY="/home/pi/Photos"
export SLIDESHOW_INTERVAL="10"  # seconds
```

### Option B: Google Photos Integration (Complex)
Google Photos API requires:
- Google Cloud Console project
- OAuth 2.0 credentials
- Photos Library API enabled
- User consent flow

**Recommendation**: Use local photos for now, we can add Google Photos later if needed.

## 3. Auto-Startup Service Configuration

Run on your Pi:
```bash
cd /home/pi/pi-lifehub
sudo ./scripts/setup_pi.sh
```

This will:
- Install dependencies
- Create systemd service
- Configure kiosk mode
- Set up auto-start

## 4. Voice Dependencies (Optional)

On the Pi:
```bash
# Install audio system dependencies
sudo apt install portaudio19-dev python3-pyaudio

# Install Python audio packages
source venv/bin/activate
pip install pyaudio SpeechRecognition
```

## 5. Testing Your Setup

1. **Backend Health**: `curl http://localhost:8001/health`
2. **Weather**: `curl http://localhost:8001/api/weather/current`
3. **Photos**: `curl http://localhost:8001/api/photos/status`
4. **Timer**: `curl http://localhost:8001/api/timer/status`
5. **Users**: `curl http://localhost:8001/api/users`

## 6. Dashboard Access

- **Local**: http://localhost:8001
- **Network**: http://[PI_IP]:8001
- **Kiosk Mode**: Auto-starts after reboot

## 7. Troubleshooting

```bash
# Check service status
sudo systemctl status lifehub

# View logs
sudo journalctl -u lifehub -f

# Restart service
sudo systemctl restart lifehub

# Health check
~/pi-lifehub/scripts/health_check.sh
```

## Next Steps After Setup

1. Test all family members can add todos
2. Configure weather for your location
3. Add family photos to slideshow
4. Set up timer presets for common activities
5. Test voice commands (if enabled)
6. Customize dashboard appearance