# 🏠 Raspberry Pi Life Hub

A secure, touch-optimized family dashboard for Raspberry Pi 5 with 7" touchscreen. Displays time, manages family todo lists, provides weather updates, calendar integration, and family photo slideshow.

## 🛡️ Security First

**Pi Life Hub implements enterprise-grade security:**
- ✅ **Zero hardcoded credentials** - All sensitive data in environment variables
- ✅ **Secure token storage** - OAuth tokens encrypted in `~/.config/lifehub/`
- ✅ **Git protection** - Comprehensive `.gitignore` prevents credential leaks
- ✅ **File permissions** - 600/700 permissions on sensitive files
- ✅ **Automated setup** - Security validation and configuration scripts

🔒 **[Read full security documentation](docs/SECURITY.md)**

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/davidpm1021/pi-lifehub.git
cd pi-lifehub

# Run security setup (creates .env, sets permissions)
./scripts/setup_security.sh

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Edit .env with your Google OAuth credentials
nano .env

# Required variables:
# GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=your_client_secret
# SECRET_KEY=automatically_generated_secure_key
```

### 3. Development Workflow Setup

**For development sessions, mount your Pi filesystem:**

```bash
# Create mount point (one-time setup)
mkdir -p ~/pi-mount

# Mount Pi filesystem for development
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount

# Navigate to project
cd ~/pi-mount/lifehub

# Verify mount and check status
pwd  # Should show: ~/pi-mount/lifehub
git status
```

**Environment file workflow:**
- `.env` files are **local to each device** and **never committed**
- Each new device needs its own `.env` configuration
- Use `.env.example` as template

```bash
# Set up environment on new device
cp .env.example .env
nano .env  # Add your actual Google OAuth credentials
./scripts/setup_security.sh
python3 config/env_config.py  # Validate
```

📖 **[Complete Development Workflow Guide](docs/DEVELOPMENT_WORKFLOW.md)**

### 4. Pi Deployment

```bash
# SSH to your Pi
ssh davidpm@192.168.86.36
cd /home/davidpm/lifehub

# Run the setup script
./scripts/setup_pi.sh

# Reboot your Pi
sudo reboot
```

### 5. Kiosk Mode Setup

```bash
# Configure auto-start kiosk mode
./scripts/setup_kiosk_autostart.sh

# Test kiosk mode
./scripts/test_kiosk.sh
```

**Dashboard will auto-start in kiosk mode on port 8001\!**

## 🎯 Features

### 📱 Core Dashboard (MVP) ✅
- **🕐 Always-on time/date display** - Large, readable clock in Eastern Time
- **👨‍👩‍👧‍👦 Family member profiles** - Switch between family members
- **📝 Personal todo lists** - Add/complete tasks per person
- **👆 Touch-optimized UI** - 48px+ touch targets for 7" screen
- **💾 Local SQLite storage** - No internet required for core features
- **🔄 Auto-start on boot** - Runs in kiosk mode

### ✨ Enhanced Features ✅
- **🌤️ Weather widget** - Current conditions with auto-refresh
- **📸 Photo slideshow** - Family photos with smooth transitions
- **⏰ Timer functionality** - Quick presets (5min, 10min, 25min Pomodoro)
- **📅 Google Calendar integration** - Weekly grid view with OAuth security
- **🎤 Voice commands** - "Hey Hub" wake word support
- **📱 Swipeable interface** - 5-page carousel with navigation

### 🛡️ Security Features ✅
- **🔐 Environment-based config** - No hardcoded secrets
- **🔑 Secure OAuth flow** - Automatic token refresh
- **📁 Encrypted storage** - Protected credential files
- **🚫 Git protection** - Comprehensive ignore patterns
- **✅ Configuration validation** - Automated security checks
- **📋 Setup automation** - One-command security configuration

## 🏗️ Architecture

### Swipeable Carousel Layout
The dashboard features a 5-page carousel interface:

1. **Family & Todos** - Member selection and personal task lists
2. **Weather** - Current conditions for Medford, NJ
3. **Calendar** - Weekly grid view (Sunday to Saturday)
4. **Photos** - Family photo slideshow with fade transitions
5. **Timers & Actions** - Timer controls and quick actions

### Security Architecture
```
┌─ Environment Variables (.env) ──────────────────┐
│  ├─ Google OAuth credentials                   │
│  ├─ API keys and secrets                       │
│  └─ Application configuration                  │
└────────────────────────────────────────────────┘
                           │
┌─ Secure Token Storage (~/.config/lifehub/) ────┐
│  ├─ OAuth access tokens (encrypted)            │
│  ├─ Refresh tokens (automatic renewal)         │
│  └─ File permissions: 600 (owner only)         │
└────────────────────────────────────────────────┘
                           │
┌─ Application Layer ─────────────────────────────┐
│  ├─ FastAPI backend (port 8001)                │
│  ├─ Static file serving                        │
│  ├─ SQLite database (local storage)            │
│  └─ Chromium kiosk mode frontend               │
└────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
lifehub/
├── 🛡️ Security
│   ├── .env.example              # Secure configuration template
│   ├── .gitignore               # Comprehensive protection
│   ├── config/env_config.py     # Environment management
│   └── docs/SECURITY.md         # Security documentation
├── 🚀 Application
│   ├── backend/main.py          # FastAPI server
│   ├── frontend/               # Static web files
│   ├── modules/                # Feature modules
│   │   ├── calendar/           # Google Calendar integration
│   │   └── photos/             # Photo slideshow
│   └── scripts/                # Setup and maintenance
├── 📖 Documentation
│   ├── docs/KIOSK_SETUP.md     # Kiosk configuration
│   ├── docs/SECURITY.md        # Security guide
│   └── FEATURES.md             # Feature documentation
└── 🔧 Configuration
    ├── requirements.txt        # Python dependencies
    └── lifehub.db             # SQLite database
```

## 🔐 Environment Configuration FAQ

### Q: Are my .env files saved when I git pull on another device?
**A: No, .env files are local-only and never committed to Git for security.**

- ✅ **What IS saved**: `.env.example` template (safe to commit)
- ❌ **What is NOT saved**: `.env` with your actual secrets (local only)
- 🔄 **On new devices**: Copy `.env.example` to `.env` and configure

### Q: How do I set up .env on a new device?
```bash
# 1. Clone/pull the repository
git pull origin main

# 2. Create local environment file
cp .env.example .env

# 3. Configure with your actual credentials
nano .env  # Add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.

# 4. Run security setup
./scripts/setup_security.sh

# 5. Validate configuration
python3 config/env_config.py
```

### Q: What happens when I work from multiple devices?
- Each device needs its own `.env` configuration
- Your secrets stay secure and local
- Code changes sync via Git, but environment stays private
- Mount your Pi via SSHFS to edit files directly on the Pi

📖 **[Complete Development Workflow Guide](docs/DEVELOPMENT_WORKFLOW.md)**

## 🔧 Development

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Validate configuration
python3 config/env_config.py

# Run development server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Open browser
open http://localhost:8001
```

### Testing Security

```bash
# Test OAuth authentication
python3 complete_auth_secure.py

# Validate environment
python3 config/env_config.py

# Check file permissions
ls -la .env                    # Should be -rw-------
ls -la ~/.config/lifehub/     # Should be drwx------

# Verify Git protection
git check-ignore .env          # Should be ignored
```

### API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/time` - Current time/date
- `GET /api/todos` - Family todo lists
- `POST /api/todos` - Add new todo
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo
- `GET /api/weather` - Weather data
- `GET /api/calendar` - Calendar events
- `GET /api/health` - System health check

## 📚 Documentation Index

### Core Documentation
- **[README.md](README.md)** - Project overview and quick start
- **[FEATURES.md](FEATURES.md)** - Complete feature list and specifications
- **[docs/SECURITY.md](docs/SECURITY.md)** - Enterprise security documentation

### Setup and Development
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Complete installation guide
- **[docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)** - Development workflow and Pi mounting
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick command reference
- **[docs/KIOSK_SETUP.md](docs/KIOSK_SETUP.md)** - Kiosk mode configuration

### Module Documentation
- **[modules/README.md](modules/README.md)** - Module architecture and development


## 📋 Setup Scripts

- `./scripts/setup_security.sh` - Configure environment and security
- `./scripts/setup_pi.sh` - Full Pi setup and configuration
- `./scripts/setup_kiosk_autostart.sh` - Enable kiosk auto-start
- `./scripts/test_kiosk.sh` - Test kiosk mode functionality
- `./scripts/test_voice.sh` - Test voice commands
- `./scripts/test_microphone.sh` - Test microphone input

## 🐛 Troubleshooting

### Common Issues

**Development-Specific Issues:**

4. **SSHFS Mount Issues**
   ```bash
   # Mount becomes unresponsive
   fusermount -u ~/pi-mount
   sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount
   
   # Permission denied mounting
   sudo usermod -a -G fuse $USER  # Add user to fuse group
   # Then logout and login again
   ```

5. **Environment File Missing After Git Pull**
   ```bash
   # This is normal! .env files are local-only
   cp .env.example .env
   nano .env  # Configure your credentials
   ./scripts/setup_security.sh
   python3 config/env_config.py  # Validate
   ```

6. **Different Behavior on Pi vs Development Machine**
   ```bash
   # Check if you're editing the right files
   pwd  # Should show ~/pi-mount/lifehub
   
   # Verify mount is working
   ls -la  # Should show Pi files, not local files
   
   # Test direct Pi access
   ssh davidpm@192.168.86.36 "cd lifehub && git status"
   ```

1. **OAuth Authentication Fails**
   ```bash
   # Check environment variables
   python3 config/env_config.py
   
   # Verify Google Cloud Console setup
   # Ensure redirect URI matches: http://localhost:8001/auth/callback
   ```

2. **Kiosk Mode Not Starting**
   ```bash
   # Check autostart configuration
   cat ~/.config/autostart/lifehub-kiosk.desktop
   
   # Test manual start
   ./scripts/test_kiosk.sh
   ```

3. **Permission Errors**
   ```bash
   # Run security setup
   ./scripts/setup_security.sh
   
   # Check file permissions
   ls -la .env ~/.config/lifehub/
   ```

### Health Checks

```bash
# System health
curl http://localhost:8001/api/health

# Service status
systemctl status lifehub

# Log analysis
tail -f logs/lifehub.log
```

## 🤝 Contributing

1. **Security First**: Never commit credentials or sensitive data
2. **Use Environment Variables**: All configuration via `.env`
3. **Test Security**: Run `./scripts/setup_security.sh` before commits
4. **Documentation**: Update relevant `.md` files for changes
5. **Follow Patterns**: Use existing code structure and conventions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI, SQLite, and modern web standards
- Optimized for Raspberry Pi 5 with 7" touchscreen
- Security-first design with enterprise-grade protection
- Family-focused features for daily household management

---

**🔒 Security Notice**: This project implements comprehensive security measures. Always keep your `.env` file secure and never commit it to version control. Review `docs/SECURITY.md` for complete security guidelines.
EOF < /dev/null
