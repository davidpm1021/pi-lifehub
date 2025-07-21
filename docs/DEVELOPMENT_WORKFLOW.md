# 💻 Development Workflow Guide

This guide explains how to set up your development environment for Pi Life Hub, including mounting your Raspberry Pi and managing environment configuration across devices.

## 🚀 Quick Start for Development Sessions

### Step 1: Mount Your Raspberry Pi

Every development session starts by mounting your Pi's filesystem:

```bash
# Create mount point (one time setup)
mkdir -p ~/pi-mount

# Mount your Pi's filesystem via SSHFS
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount

# Navigate to the project
cd ~/pi-mount/lifehub
```

**What this does:**
- Mounts your Pi's home directory to `~/pi-mount`
- Allows you to edit files locally while they're stored on the Pi
- Changes are immediately available on both your dev machine and Pi
- No need to transfer files back and forth

### Step 2: Verify Project Status

```bash
# Check Git status
git status

# Verify you're in the right location
pwd
# Should show: /home/[your-user]/pi-mount/lifehub

# Check if environment is configured
ls -la .env*
# Should show: .env.example (and .env if configured)
```

### Step 3: Environment Configuration

Your `.env` file is **local to each device** and **never committed to Git**:

```bash
# If .env doesn't exist, create it from template
if [ \! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from template - you need to configure it\!"
fi

# Validate current configuration
python3 config/env_config.py
```

## 🔐 Environment File Workflow

### Understanding .env File Behavior

**✅ What's Protected:**
- `.env` files are **never committed** to Git (protected by .gitignore)
- Each device/Pi needs its own `.env` configuration
- Your secrets stay local and secure

**📋 What You Need to Know:**
- **`.env.example`**: Template file (committed to Git, safe to share)
- **`.env`**: Your actual configuration (local only, contains secrets)
- When you `git pull` on a new device, you only get `.env.example`

### Setting Up .env on New Devices

When you clone/pull the repo on a new device:

```bash
# 1. You'll only have the template
ls -la .env*
# Shows: .env.example

# 2. Create your local .env
cp .env.example .env

# 3. Configure with your actual credentials
nano .env
# Update: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.

# 4. Run security setup
./scripts/setup_security.sh

# 5. Validate configuration
python3 config/env_config.py
```

### Environment Variables You Need

**Required (must be configured):**
```bash
GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_actual_client_secret
SECRET_KEY=automatically_generated_64_char_string
```

**Optional (have sensible defaults):**
```bash
SERVER_HOST=localhost
SERVER_PORT=8001
DEBUG_MODE=false
WEATHER_API_KEY=your_openweather_api_key
```

## 🏗️ Development Setup Workflow

### First Time Setup on New Machine

```bash
# 1. Mount your Pi
mkdir -p ~/pi-mount
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount
cd ~/pi-mount/lifehub

# 2. Pull latest changes
git pull origin main

# 3. Set up environment
cp .env.example .env
nano .env  # Configure your actual credentials
./scripts/setup_security.sh

# 4. Validate setup
python3 config/env_config.py

# 5. Test development server
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Regular Development Session

```bash
# 1. Mount Pi (if not already mounted)
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount

# 2. Navigate to project
cd ~/pi-mount/lifehub

# 3. Check for updates
git status
git pull origin main  # if needed

# 4. Verify environment (should already be configured)
python3 config/env_config.py

# 5. Start development
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📂 Directory Structure for Development

```
Your Development Machine:
~/pi-mount/                    # SSHFS mount point
└── lifehub/                   # Pi Life Hub project
    ├── .env                   # Your local config (never committed)
    ├── .env.example          # Template (committed, safe)
    ├── backend/              # FastAPI application
    ├── frontend/             # Static web files
    ├── config/               # Configuration management
    ├── docs/                 # Documentation
    └── scripts/              # Setup and utility scripts

Your Raspberry Pi:
/home/davidpm/
└── lifehub/                  # Same project, but on Pi
    ├── .env                  # Pi's local config
    ├── venv/                 # Python virtual environment
    ├── lifehub.db           # SQLite database
    └── logs/                # Application logs
```

## 🔄 Common Development Tasks

### Making Code Changes

```bash
# 1. Mount Pi and navigate
cd ~/pi-mount/lifehub

# 2. Make your changes using your preferred editor
code .  # VS Code
vim backend/main.py  # or any editor

# 3. Changes are immediately available on Pi
# No need to copy files\!

# 4. Test changes
curl http://192.168.86.36:8001/api/health

# 5. Commit when ready
git add .
git commit -m "Your changes"
git push origin main
```

### Updating Dependencies

```bash
# 1. Mount and navigate
cd ~/pi-mount/lifehub

# 2. Activate virtual environment
source venv/bin/activate

# 3. Update requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 4. Install on Pi
pip install -r requirements.txt

# 5. Commit changes
git add requirements.txt
git commit -m "Add new dependency"
git push origin main
```

### Database Changes

```bash
# 1. Connect to Pi database
cd ~/pi-mount/lifehub
sqlite3 lifehub.db

# 2. Make schema changes
.schema  # view current schema
ALTER TABLE todos ADD COLUMN priority INTEGER DEFAULT 1;

# 3. Update models if needed
vim modules/*/models.py

# 4. Test changes
python3 -c "import sqlite3; conn=sqlite3.connect('lifehub.db'); print('DB OK')"
```

## 🐛 Troubleshooting Development Issues

### Mount Issues

```bash
# If mount fails or becomes unresponsive
fusermount -u ~/pi-mount  # Unmount
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount  # Remount

# Check if Pi is accessible
ping 192.168.86.36
ssh davidpm@192.168.86.36 "echo 'Pi is accessible'"
```

### Environment Issues

```bash
# .env file missing or corrupted
cd ~/pi-mount/lifehub
cp .env.example .env
./scripts/setup_security.sh

# Validation fails
python3 config/env_config.py
# Follow the error messages to fix configuration

# OAuth issues
rm -rf ~/.config/lifehub/  # Clear cached tokens
python3 complete_auth_secure.py  # Re-authenticate
```

### Service Issues

```bash
# Check if service is running on Pi
ssh davidpm@192.168.86.36 "systemctl status lifehub"

# Check logs
ssh davidpm@192.168.86.36 "tail -f /home/davidpm/lifehub/logs/lifehub.log"

# Restart service
ssh davidpm@192.168.86.36 "sudo systemctl restart lifehub"
```

### Git Issues

```bash
# Accidentally staged .env file
git reset HEAD .env

# Uncommitted changes conflict with pull
git stash
git pull origin main
git stash pop

# Force push (use with caution)
git push origin main --force
```

## 🛡️ Security Reminders for Development

### Before Each Session

```bash
# Verify .env is not tracked
git check-ignore .env  # Should confirm it's ignored

# Check for staged secrets
git status  # Should not show .env or credential files

# Validate security setup
python3 config/env_config.py
```

### Before Committing

```bash
# Security pre-commit check
git diff --cached --name-only  < /dev/null |  grep -E "\.(env|json)$|credentials|token"
# Should return nothing (no secrets staged)

# Run security validation
./scripts/setup_security.sh

# Final check
git status  # Verify only intended files are staged
```

## 📋 Development Checklist

### Starting a Session
- [ ] Mount Pi via SSHFS
- [ ] Navigate to project directory
- [ ] Check Git status and pull updates
- [ ] Verify .env configuration
- [ ] Validate environment with `python3 config/env_config.py`
- [ ] Start development server

### Ending a Session
- [ ] Commit and push changes
- [ ] Check no secrets are staged
- [ ] Stop development server
- [ ] Unmount Pi (optional - can stay mounted)

### Weekly Maintenance
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Check Pi system updates: `ssh davidpm@192.168.86.36 "sudo apt update && sudo apt upgrade"`
- [ ] Review logs: `tail -f ~/pi-mount/lifehub/logs/lifehub.log`
- [ ] Backup database: `cp ~/pi-mount/lifehub/lifehub.db ./backup/`

## 🎯 Pro Tips

1. **Keep mount persistent**: SSHFS mounts can stay active between sessions
2. **Use VS Code Remote**: Install "Remote - SSH" extension for seamless editing
3. **Alias common commands**: Add to your shell profile:
   ```bash
   alias mount-pi="sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount"
   alias lifehub="cd ~/pi-mount/lifehub"
   alias pi-ssh="ssh davidpm@192.168.86.36"
   ```
4. **Monitor in real-time**: Use `watch` command for continuous monitoring:
   ```bash
   watch -n 2 "curl -s http://192.168.86.36:8001/api/health | jq"
   ```

---

**🔒 Security Note**: Your `.env` files remain local to each device and are never committed to Git. This means each new device needs its own configuration, but your secrets stay secure.
