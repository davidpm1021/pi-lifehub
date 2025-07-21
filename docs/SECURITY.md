# Security Documentation

## Overview

This document outlines the security measures implemented in Pi Life Hub to protect sensitive data and maintain secure operations.

## Security Features

### 1. Environment Variable Management

- **Secure Storage**: All sensitive configuration stored in `.env` file
- **Type Safety**: Environment variables validated and type-checked
- **Required Validation**: Critical variables marked as required
- **Default Values**: Safe defaults for non-critical settings

### 2. OAuth Credential Security

- **No Hardcoded Secrets**: All OAuth credentials loaded from environment
- **Secure Token Storage**: Tokens stored in `~/.config/lifehub/` with 600 permissions
- **Automatic Refresh**: Expired tokens refreshed automatically
- **Device Flow**: Headless authentication for kiosk mode

### 3. File System Security

- **Restrictive Permissions**: 
  - `.env` files: 600 (owner read/write only)
  - Token files: 600 (owner read/write only)
  - Config directory: 700 (owner access only)
  - Log directory: 755 (standard permissions)

### 4. Git Security

- **Comprehensive .gitignore**: Prevents accidental commit of sensitive files
- **Multiple Patterns**: Covers various credential file naming conventions
- **Environment Files**: All `.env` variants ignored
- **Backup Protection**: Backup files (`.bak`, `*.backup`) ignored

## File Structure

```
lifehub/
├── .env                          # Sensitive configuration (gitignored)
├── .env.example                  # Template with safe defaults
├── .gitignore                    # Comprehensive ignore patterns
├── config/
│   └── env_config.py            # Secure environment management
├── modules/calendar/
│   ├── service_secure.py        # Secure calendar service
│   ├── credentials.json         # OAuth config (gitignored)
│   └── token.json              # Access tokens (gitignored)
└── ~/.config/lifehub/           # Secure token storage
    └── calendar_token.json      # Encrypted storage location
```

## Required Environment Variables

### Critical (Required)
- `GOOGLE_CLIENT_ID`: OAuth client identifier
- `GOOGLE_CLIENT_SECRET`: OAuth client secret
- `SECRET_KEY`: Application secret key (64+ random characters)

### Server Configuration
- `SERVER_HOST`: Server bind address (default: localhost)
- `SERVER_PORT`: Server port (default: 8001)
- `DEBUG_MODE`: Enable debug mode (default: false)

### Security Settings
- `CORS_ORIGINS`: Allowed CORS origins
- `ALLOWED_HOSTS`: Permitted host headers
- `SESSION_TIMEOUT`: Session expiry time in seconds

## Setup Instructions

### 1. Initial Security Setup

```bash
# Run the security setup script
./scripts/setup_security.sh
```

This script will:
- Create `.env` from template if missing
- Set up secure directories with proper permissions
- Generate a secure `SECRET_KEY`
- Validate configuration
- Check Git security

### 2. Configure OAuth Credentials

1. **Google Cloud Console Setup**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download credentials JSON

2. **Update .env File**:
   ```bash
   GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:8001/auth/callback
   ```

### 3. Validate Configuration

```bash
# Check configuration validity
python3 config/env_config.py

# Test authentication
python3 complete_auth_secure.py
```

## Security Best Practices

### 1. Development

- Never commit `.env` files to version control
- Use `.env.example` for sharing configuration templates
- Rotate secrets regularly
- Use different credentials for development/production

### 2. Production Deployment

- Use strong, unique secret keys
- Enable HTTPS in production
- Restrict CORS origins to known domains
- Monitor logs for security events
- Keep dependencies updated

### 3. Access Control

- Limit file system permissions
- Use dedicated service accounts
- Implement rate limiting
- Monitor API usage

## Security Validation

### Automated Checks

The `env_config.py` module includes validation:

```python
# Validate configuration
from config.env_config import Config
errors = Config.validate()
if errors:
    print("Security issues found:", errors)
```

### Manual Checks

```bash
# Check for staged secrets
git diff --cached --name-only  < /dev/null |  grep -E "\.(env|json)$|credentials|token"

# Verify file permissions
ls -la .env                    # Should show -rw-------
ls -la ~/.config/lifehub/     # Should show drwx------

# Check gitignore coverage
git check-ignore .env          # Should be ignored
git check-ignore modules/calendar/credentials.json  # Should be ignored
```

## Incident Response

### If Secrets Are Compromised

1. **Immediate Actions**:
   - Revoke compromised OAuth credentials in Google Cloud Console
   - Generate new client ID/secret
   - Update `.env` with new credentials
   - Restart all services

2. **Git History Cleanup** (if committed):
   ```bash
   # Remove from history (use with caution)
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push (destructive)
   git push origin --force --all
   ```

3. **Audit and Monitor**:
   - Review access logs
   - Check for unauthorized API usage
   - Monitor for unusual activity

### Recovery Steps

1. Generate new credentials in Google Cloud Console
2. Update `.env` with new values
3. Clear cached tokens: `rm ~/.config/lifehub/calendar_token.json`
4. Re-authenticate: `python3 complete_auth_secure.py`
5. Verify services are working
6. Document incident and improve security measures

## Monitoring

### Log Analysis

Monitor these log patterns for security events:

- Authentication failures
- Invalid OAuth requests
- Unusual API access patterns
- File permission errors
- Configuration validation failures

### Health Checks

```python
# Check service security status
from modules.calendar.service_secure import get_calendar_service
service = get_calendar_service()
health = service.health_check()
print(health)
```

## Contact

For security issues or questions:
- Review this documentation
- Check configuration with `python3 config/env_config.py`
- Run security setup: `./scripts/setup_security.sh`

Remember: **Security is a process, not a destination.** Regularly review and update these measures.
