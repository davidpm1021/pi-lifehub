# Pi Life Hub Project Context

## Project Overview
Pi Life Hub is a touch-optimized family dashboard running on Raspberry Pi 5 with a 7" touchscreen. It serves as a central command center for daily family life management.

## Current Architecture

### Backend (FastAPI)
- **Main Server**: `backend/main.py` running on port 8001
- **Database**: SQLite with users and todos tables
- **API Endpoints**: Health monitoring, time, users, todos
- **Features**: Family member profiles, personal todo lists, real-time clock

### Frontend (Vanilla JS)
- **Interface**: Touch-optimized HTML/CSS/JS dashboard
- **Layout**: Responsive grid for 7" screen (800x480)
- **Touch Targets**: 48px+ minimum for accessibility
- **Updates**: Real-time clock, 30-second data refresh

### Modular System
- **Voice Module**: Complete framework (needs dependencies)
- **Weather Module**: Stub only
- **Photos Module**: Stub only  
- **Timer Module**: Stub only

## Hardware Target
- **Device**: Raspberry Pi 5 (8GB RAM)
- **Display**: 7" touchscreen (800x480)
- **Audio**: USB microphone, mini speaker
- **Storage**: 64GB micro SD
- **Cooling**: Active cooling case

## Development Setup
- **SSHFS Mount**: `/home/davidpm/pi-lifehub` (dev) ’ `/home/davidpm/lifehub` (Pi)
- **Git**: Connected to https://github.com/davidpm1021/pi-lifehub.git
- **Environment**: Virtual environment on Pi directly (not through mount)

## Current Status (July 20, 2025)

###  Working Features
- Touch-optimized family dashboard
- Real-time clock display
- Family member selection
- Personal todo lists per member
- Add/complete todo functionality
- Health monitoring API
- SQLite database with user management

### = Partial Implementation
- **Voice Commands**: Framework complete, needs PyAudio/SpeechRecognition
- **Auto-startup**: Scripts exist but not configured as service

### L Not Yet Implemented
- Weather widget
- Photo slideshow
- Timer functionality
- NFC reader integration
- Auto-startup service (on Pi)

## Database Schema
```sql
-- Users table with NFC support
users (id, name, nfc_tag_id, created_at)

-- Todos with user relationships  
todos (id, user_id, task, completed, created_at)
```

## API Endpoints
- `GET /health` - System health check
- `GET /api/time` - Current time/date
- `GET /api/users` - List family members
- `POST /api/users` - Create family member
- `GET /api/todos/{user_id}` - Get user todos
- `POST /api/todos/{user_id}` - Add todo
- `PUT /api/todos/{todo_id}` - Update todo
- `GET /api/voice/status` - Voice system status (needs deps)

## Key Files
- `backend/main.py` - FastAPI server
- `frontend/index.html` - Dashboard interface
- `scripts/setup_pi.sh` - Pi configuration automation
- `modules/voice/` - Voice command system
- `lifehub.db` - SQLite database
- `requirements.txt` - Python dependencies

## Development Notes
- Backend running manually on port 8001 (not auto-started)
- Database has duplicate test users (needs cleanup)
- Voice module architecture complete but missing audio libraries
- Setup script not run on Pi hardware yet
- Touch interface tested in browser, needs Pi touchscreen validation

## Next Development Priority
1. Deploy to actual Pi 5 hardware
2. Run setup script for auto-startup
3. Install voice dependencies if voice features wanted
4. Implement weather/photos/timer modules
5. Clean up database duplicates
6. Test touch functionality on 7" screen