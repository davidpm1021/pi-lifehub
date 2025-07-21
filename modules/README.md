# Pi Life Hub Modules

This directory contains the modular components of Pi Life Hub, each implementing specific functionality with secure, environment-based configuration.

## 🛡️ Security-First Architecture

All modules follow security best practices:
- **Environment-based configuration** - No hardcoded credentials
- **Secure token management** - OAuth tokens stored safely
- **Input validation** - All user inputs sanitized
- **Error handling** - Graceful failure with logging

## 📁 Module Structure

### 📅 Calendar Module (`calendar/`)
Google Calendar integration with secure OAuth flow.

**Files:**
- `service_secure.py` - Secure calendar service with environment config
- `service.py` - Legacy service (deprecated)
- `api.py` - FastAPI endpoints for calendar data
- `models.py` - Data models and schemas
- `config.py` - Configuration management
- `credentials.json` - OAuth client config (gitignored)
- `token.json` - Access tokens (gitignored)

**Features:**
- ✅ Secure OAuth 2.0 authentication
- ✅ Automatic token refresh
- ✅ Weekly grid view (Sunday-Saturday)
- ✅ Multi-day event support
- ✅ Error handling and logging

**API Endpoints:**
- `GET /api/calendar/events` - Upcoming calendar events
- `GET /api/calendar/week` - Weekly view data
- `GET /api/calendar/health` - Service health check

### 📸 Photos Module (`photos/`)
Family photo slideshow with smooth transitions.

**Files:**
- `service.py` - Photo management service
- `api.py` - FastAPI endpoints for photo data
- `models.py` - Photo data models
- `config.py` - Photo slideshow configuration

**Features:**
- ✅ Automatic photo discovery
- ✅ Multiple format support (JPG, PNG, GIF)
- ✅ Smooth fade transitions
- ✅ Random shuffle option
- ✅ Configurable timing

**API Endpoints:**
- `GET /api/photos/list` - Available photos
- `GET /api/photos/random` - Random photo selection
- `GET /api/photos/config` - Slideshow settings

## 🔧 Module Development

### Adding New Modules

1. **Create module directory:**
   ```bash
   mkdir modules/new_module
   cd modules/new_module
   ```

2. **Module structure:**
   ```
   new_module/
   ├── __init__.py          # Module initialization
   ├── service.py           # Core service logic
   ├── api.py              # FastAPI routes
   ├── models.py           # Data models
   ├── config.py           # Configuration
   └── README.md           # Module documentation
   ```

3. **Security requirements:**
   - Use environment variables for all secrets
   - Implement proper error handling
   - Add input validation
   - Include logging
   - Write security tests

4. **Integration:**
   - Register routes in `backend/main.py`
   - Add configuration to `config/env_config.py`
   - Update documentation
   - Add to health checks

### Module Guidelines

**Security:**
- Never hardcode credentials or API keys
- Use `config.env_config` for environment variables
- Implement proper authentication/authorization
- Validate all inputs
- Log security events

**Performance:**
- Use async/await for I/O operations
- Implement caching where appropriate
- Handle rate limiting
- Graceful degradation on errors

**Testing:**
- Unit tests for core logic
- Integration tests for API endpoints
- Security tests for authentication
- Health check validation

**Documentation:**
- Clear module README
- API endpoint documentation
- Configuration options
- Security considerations

## 📋 Environment Variables

Each module can define its own environment variables in `.env`:

```bash
# Calendar Module
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
CALENDAR_REFRESH_INTERVAL=300

# Photos Module
PHOTOS_DIRECTORY=frontend/static/photos
PHOTO_TRANSITION_TIME=5
PHOTO_FADE_DURATION=1

# Weather Module (if implemented)
WEATHER_API_KEY=your_api_key
WEATHER_LOCATION=Medford,NJ,US
WEATHER_REFRESH_INTERVAL=600
```

## 🩺 Health Monitoring

Each module should implement health checks:

```python
def health_check() -> Dict[str, Any]:
    """
    Return module health status
    """
    return {
        'module': 'calendar',
        'status': 'healthy',
        'last_check': datetime.now().isoformat(),
        'authenticated': True,
        'api_available': True
    }
```

Access via: `GET /api/{module}/health`

## 🔄 Module Lifecycle

### Initialization
1. Load environment configuration
2. Initialize secure services
3. Register API routes
4. Start background tasks
5. Validate connectivity

### Runtime
1. Handle API requests
2. Refresh data periodically
3. Monitor health status
4. Log operations
5. Handle errors gracefully

### Shutdown
1. Save state if needed
2. Close connections
3. Clean up resources
4. Log shutdown

## 🚀 Future Modules

Planned modules for future development:

- **🏠 Smart Home** - IoT device integration
- **📊 Analytics** - Usage statistics and insights
- **🎵 Music** - Spotify/Apple Music integration
- **📰 News** - News feed display
- **🍽️ Meals** - Meal planning and recipes
- **💰 Budget** - Family expense tracking
- **🎯 Goals** - Family goal tracking
- **📚 Learning** - Educational content for kids

Each new module will follow the same security-first, environment-based architecture.

---

**🔒 Security Note**: All modules must follow security guidelines. Never commit credentials, always use environment variables, and implement proper error handling and logging.
EOF < /dev/null
