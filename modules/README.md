# Pi Life Hub Modules

This directory contains modular features for the Pi Life Hub dashboard. Each module is designed to be independent and follows production best practices.

## Module Structure

Each module follows this structure:
```
module_name/
├── __init__.py       # Module exports
├── api.py           # FastAPI routes
├── service.py       # Business logic
├── models.py        # Data models
├── config.py        # Module configuration
└── README.md        # Module documentation
```

## Phase 2 Modules

### Voice Module (`/modules/voice/`)
- Voice command recognition using "Hey Hub" wake word
- USB microphone integration
- Command processing with error handling
- Fallback to button controls

### Weather Module (`/modules/weather/`)
- Local weather data caching
- API integration with rate limiting
- Offline fallback display
- Temperature monitoring

### Photos Module (`/modules/photos/`)
- Family photo slideshow
- Local storage management
- Touch controls for navigation
- Auto-rotation with configurable timing

### Timer Module (`/modules/timer/`)
- Quick timer presets
- Visual and audio alerts
- Multiple concurrent timers
- Touch-friendly controls

## Production Requirements

All modules must:
1. Handle hardware disconnection gracefully
2. Log errors to `/var/log/pi-life-hub/`
3. Provide health check endpoints
4. Work offline when possible
5. Follow 48px minimum touch target rule
6. Keep CPU usage under 10% when idle
7. Implement proper error boundaries

## Adding New Modules

1. Create module directory under `/modules/`
2. Implement required files following structure
3. Add module routes to main FastAPI app
4. Update systemd service if needed
5. Test on actual Pi hardware
6. Document GPIO/hardware usage