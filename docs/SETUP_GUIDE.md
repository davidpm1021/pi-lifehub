# 🚀 Complete Setup Guide

This guide provides step-by-step instructions for setting up Pi Life Hub with maximum security and functionality.

## 📋 Prerequisites

### Hardware Requirements
- **Raspberry Pi 5** (recommended) or Pi 4
- **7" Touchscreen** (800x480 resolution)
- **MicroSD Card** (32GB+ recommended)
- **USB Microphone** (optional, for voice commands)
- **Internet Connection** (for initial setup and cloud features)

### Software Requirements
- **Raspberry Pi OS** (Bookworm/Debian 12 recommended)
- **Python 3.12+** (included in latest Pi OS)
- **Git** (for repository management)
- **Chromium Browser** (for kiosk mode)

## 🛡️ Security-First Setup

### Step 1: Clone Repository

```bash
# SSH to your Raspberry Pi
ssh pi@your-pi-ip-address

# Clone the repository
git clone https://github.com/davidpm1021/pi-lifehub.git
cd pi-lifehub
```

### Step 2: Security Configuration

```bash
# Run the comprehensive security setup
./scripts/setup_security.sh
```

This script will:
- ✅ Create `.env` from template
- ✅ Set secure file permissions (600/700)
- ✅ Generate secure SECRET_KEY
- ✅ Create protected directories
- ✅ Validate configuration
- ✅ Check Git security

### Step 3: Google OAuth Setup

1. **Google Cloud Console Configuration**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable **Google Calendar API**
   - Create **OAuth 2.0 Client ID** (Desktop Application)
   - Download credentials JSON

2. **Update Environment Variables**:
   ```bash
   # Edit the .env file
   nano .env
   
   # Update these required variables:
   GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   ```

3. **Validate Configuration**:
   ```bash
   # Check configuration validity
   python3 config/env_config.py
   
   # Should show: ✅ Configuration is valid\!
   ```

### Step 4: Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import fastapi, uvicorn, dotenv; print('✅ Dependencies installed')"
```

### Step 5: Database Setup

```bash
# Initialize SQLite database
python3 -c "
import sqlite3
conn = sqlite3.connect('lifehub.db')
conn.execute('''CREATE TABLE IF NOT EXISTS todos 
                (id INTEGER PRIMARY KEY, 
                 family_member TEXT, 
                 task TEXT, 
                 completed BOOLEAN,
                 created_date TIMESTAMP)''')
conn.commit()
conn.close()
print('✅ Database initialized')
"
```

## 🖥️ Application Setup

### Step 6: Test Backend

```bash
# Start the development server
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Test in another terminal
curl http://localhost:8001/api/time
# Should return current time JSON

# Test web interface
# Open browser to: http://your-pi-ip:8001
```

### Step 7: OAuth Authentication

```bash
# Test OAuth flow (first time only)
python3 complete_auth_secure.py

# Follow the authentication prompts
# Tokens will be stored securely in ~/.config/lifehub/
```

### Step 8: Service Configuration

```bash
# Run the full Pi setup script
./scripts/setup_pi.sh
```

This will:
- ✅ Create systemd service
- ✅ Configure auto-start
- ✅ Set up log rotation
- ✅ Configure kiosk mode
- ✅ Test all components

## 📺 Kiosk Mode Setup

### Step 9: Kiosk Configuration

```bash
# Configure kiosk auto-start
./scripts/setup_kiosk_autostart.sh

# Test kiosk mode
./scripts/test_kiosk.sh
```

### Step 10: Autostart Configuration

The setup creates this autostart file:
```ini
# ~/.config/autostart/lifehub-kiosk.desktop
[Desktop Entry]
Type=Application
Name=Pi Life Hub Kiosk
Exec=/usr/bin/chromium-browser --kiosk --no-sandbox --disable-infobars [...]
X-GNOME-Autostart-enabled=true
```

### Step 11: Final Reboot

```bash
# Reboot to test auto-start
sudo reboot
```

After reboot, the dashboard should automatically start in kiosk mode\!

## 🔧 Advanced Configuration

### Voice Commands (Optional)

```bash
# Test microphone
./scripts/test_microphone.sh

# Setup voice recognition
./scripts/setup_voice.sh

# Test voice commands
./scripts/test_voice.sh
```

### Weather Configuration

```bash
# Add to .env file
echo "WEATHER_API_KEY=your_openweather_api_key" >> .env
echo "WEATHER_LOCATION=Medford,NJ,US" >> .env
```

### Photo Slideshow

```bash
# Create photos directory
mkdir -p frontend/static/photos

# Add family photos (JPG/PNG)
# Photos will automatically appear in slideshow
```

## 🩺 Health Checks & Monitoring

### System Health

```bash
# Check all services
curl http://localhost:8001/api/health

# View logs
tail -f logs/lifehub.log

# Check service status
systemctl status lifehub
```

### Security Validation

```bash
# Validate environment
python3 config/env_config.py

# Check file permissions
ls -la .env                    # Should be -rw-------
ls -la ~/.config/lifehub/     # Should be drwx------

# Verify Git protection
git status                     # Should not show .env or credentials
git check-ignore .env         # Should be ignored
```

### Performance Monitoring

```bash
# CPU and memory usage
htop

# Disk usage
df -h

# Network connections
netstat -tlnp  < /dev/null |  grep 8001
```

## 🐛 Troubleshooting

### Common Issues

1. **"Permission denied" errors**:
   ```bash
   ./scripts/setup_security.sh
   sudo chown -R pi:pi /home/pi/lifehub
   ```

2. **OAuth authentication fails**:
   ```bash
   # Check environment variables
   python3 config/env_config.py
   
   # Verify Google Cloud Console redirect URI:
   # http://localhost:8001/auth/callback
   ```

3. **Service won't start**:
   ```bash
   # Check logs
   journalctl -u lifehub -f
   
   # Restart service
   sudo systemctl restart lifehub
   ```

4. **Kiosk mode not working**:
   ```bash
   # Check autostart file
   cat ~/.config/autostart/lifehub-kiosk.desktop
   
   # Test manually
   ./scripts/test_kiosk.sh
   ```

5. **Database errors**:
   ```bash
   # Check database file
   ls -la lifehub.db
   
   # Test database connection
   python3 -c "import sqlite3; conn=sqlite3.connect('lifehub.db'); print('✅ DB OK')"
   ```

### Log Analysis

```bash
# Application logs
tail -f logs/lifehub.log

# System logs
sudo journalctl -u lifehub -f

# Chromium logs (if kiosk issues)
ls ~/.config/chromium/
```

### Recovery Procedures

```bash
# Reset environment
rm .env
./scripts/setup_security.sh

# Reset OAuth tokens
rm -rf ~/.config/lifehub/
python3 complete_auth_secure.py

# Reset database
rm lifehub.db
# Re-run database setup from Step 5

# Complete reset
git stash
git pull origin main
./scripts/setup_pi.sh
```

## 📋 Maintenance

### Regular Updates

```bash
# Update codebase
cd /home/pi/lifehub
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart lifehub
```

### Security Maintenance

```bash
# Rotate secret key (annually)
python3 -c "
import secrets, string
key = ''.join(secrets.choice(string.ascii_letters + string.digits + '\!@#$%^&*') for _ in range(64))
print(f'SECRET_KEY={key}')
" >> .env.new
# Then replace in .env

# Review permissions
./scripts/setup_security.sh

# Check for updates
sudo apt update && sudo apt upgrade
```

### Backup Procedures

```bash
# Backup database
cp lifehub.db lifehub.db.backup.$(date +%Y%m%d)

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Full system backup (recommended)
sudo dd if=/dev/mmcblk0 of=/path/to/backup.img bs=4M status=progress
```

## 🎯 Next Steps

After successful setup:

1. **Customize family members** in the web interface
2. **Add family photos** to `frontend/static/photos/`
3. **Configure weather location** in `.env`
4. **Set up voice commands** (optional)
5. **Create backup schedule** for important data
6. **Monitor logs** for any issues
7. **Review security documentation** in `docs/SECURITY.md`

## 📞 Support

For issues or questions:
- 📖 Check `docs/SECURITY.md` for security-related issues
- 🔧 Run `./scripts/setup_security.sh` to fix common problems
- 💻 Review logs in `logs/lifehub.log`
- 🩺 Use `/api/health` endpoint for system status

---

**🔒 Security Reminder**: Keep your `.env` file secure and never commit it to version control. Review security settings regularly and keep the system updated.
