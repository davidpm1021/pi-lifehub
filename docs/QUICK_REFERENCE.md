# 🚀 Quick Reference Card

## Every Development Session

### 1. Mount Your Pi
```bash
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount
cd ~/pi-mount/lifehub
```

### 2. Check Status
```bash
git status
git pull origin main  # if needed
python3 config/env_config.py  # validate environment
```

### 3. Start Development
```bash
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

## New Device Setup

### 1. Mount Pi
```bash
mkdir -p ~/pi-mount
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount
cd ~/pi-mount/lifehub
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your Google OAuth credentials
./scripts/setup_security.sh
python3 config/env_config.py  # validate
```

### 3. Test Setup
```bash
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

## Essential Commands

### Pi Access
```bash
# SSH to Pi
ssh davidpm@192.168.86.36

# Mount Pi filesystem
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount

# Unmount (if needed)
fusermount -u ~/pi-mount
```

### Environment Management
```bash
# Validate configuration
python3 config/env_config.py

# Reset environment
cp .env.example .env
./scripts/setup_security.sh

# Check what's ignored by Git
git check-ignore .env  # Should confirm .env is ignored
```

### Service Management
```bash
# Check service status on Pi
ssh davidpm@192.168.86.36 "systemctl status lifehub"

# View logs
ssh davidpm@192.168.86.36 "tail -f /home/davidpm/lifehub/logs/lifehub.log"

# Restart service
ssh davidpm@192.168.86.36 "sudo systemctl restart lifehub"
```

### Health Checks
```bash
# API health check
curl http://192.168.86.36:8001/api/health

# Configuration validation
python3 config/env_config.py

# OAuth authentication test
python3 complete_auth_secure.py
```

## Troubleshooting

### Mount Issues
```bash
# If mount becomes unresponsive
fusermount -u ~/pi-mount
sshfs davidpm@192.168.86.36:/home/davidpm ~/pi-mount

# Check Pi connectivity
ping 192.168.86.36
```

### Environment Issues
```bash
# Missing .env
cp .env.example .env
nano .env  # Configure credentials
./scripts/setup_security.sh

# Validation errors
python3 config/env_config.py
# Follow error messages to fix issues
```

### Git Issues
```bash
# Accidentally staged .env
git reset HEAD .env

# Uncommitted changes blocking pull
git stash
git pull origin main
git stash pop
```

## Important File Locations

### Your Development Machine
```
~/pi-mount/lifehub/           # Project root (mounted from Pi)
├── .env                      # Your local config (never committed)
├── .env.example             # Template (safe to commit)
└── docs/DEVELOPMENT_WORKFLOW.md  # Complete guide
```

### Your Raspberry Pi
```
/home/davidpm/lifehub/       # Project root on Pi
├── .env                     # Pi's local config
├── lifehub.db              # SQLite database
├── logs/lifehub.log        # Application logs
└── venv/                   # Python virtual environment
```

## Key Concepts

### Environment Files
- ✅ `.env.example` - Template (committed to Git, safe)
- ❌ `.env` - Your secrets (local only, never committed)
- 🔄 Each device needs its own `.env` configuration

### Development Workflow
1. **Mount Pi** - Access files directly on Pi via SSHFS
2. **Edit locally** - Use your preferred editor on mounted files
3. **Changes are live** - Instantly available on both dev machine and Pi
4. **Commit changes** - Git manages code, environment stays local

### Security
- Secrets never leave your local environment
- Each device configures its own credentials
- Git only tracks safe template files
- Automatic validation prevents misconfigurations

## Need More Help?

- 📖 **[Complete Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)**
- 🛡️ **[Security Documentation](docs/SECURITY.md)**
- 🚀 **[Setup Guide](docs/SETUP_GUIDE.md)**
- 🎯 **[Main README](../README.md)**

---

**💡 Pro Tip**: Bookmark this file for quick access during development sessions\!
EOF < /dev/null
