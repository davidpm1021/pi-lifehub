# GitHub Setup Instructions

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" button and select "New repository"
3. Repository name: `pi-lifehub`
4. Description: `Touch-optimized family dashboard for Raspberry Pi 5 with voice commands and smart features`
5. Make it **Public** (or Private if you prefer)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the GitHub repo, run these commands on your Pi:

```bash
cd /home/davidpm/lifehub

# Add GitHub as remote origin
git remote add origin https://github.com/davidpm1021/pi-lifehub.git

# Push to GitHub
git push -u origin main
```

## Step 3: Verify Setup

- Visit your GitHub repository
- You should see all 24 files
- Check that README.md displays properly
- Verify .gitignore is working (no venv/ or logs/ should be visible)

## Step 4: Future Development Workflow

```bash
# Make changes to code
# Stage and commit
git add .
git commit -m "feat: add new feature"

# Push to GitHub
git push origin main

# On Pi, pull latest changes
git pull origin main
```

## Repository Features to Enable

1. **Issues**: Enable for bug tracking and feature requests
2. **Actions**: Set up CI/CD for automated testing
3. **Branch Protection**: Protect main branch, require reviews
4. **Topics**: Add tags like `raspberry-pi`, `iot`, `dashboard`, `python`, `fastapi`

## Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for new features  
- `feature/voice-commands`: Individual feature branches
- `feature/weather-widget`: etc.

## Collaborative Development

If working with others:
1. Fork the repository
2. Create feature branches
3. Submit Pull Requests
4. Code review before merging

## Backup Strategy

GitHub serves as primary backup, but also consider:
- Pi SD card imaging
- Local development machine clone
- Cloud sync of configuration files