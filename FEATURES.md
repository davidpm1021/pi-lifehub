# Pi Life Hub Features

## 🚀 Core Features (MVP) ✅
- **🕐 Always-on time/date display** - Large, readable clock in Eastern Time
- **👨‍👩‍👧‍👦 Family member profiles** - Switch between family members
- **📝 Personal todo lists** - Add/complete tasks per person
- **👆 Touch-optimized UI** - 48px+ touch targets for 7" screen
- **💾 Local SQLite storage** - No internet required for core features
- **🔄 Auto-start on boot** - Runs in kiosk mode

## ✨ Enhanced Features ✅
- **🌤️ Weather widget** - Current conditions with auto-refresh (OpenWeather API)
- **📸 Photo slideshow** - Family photos with smooth fade transitions
- **⏰ Timer functionality** - Quick presets (5min, 10min, 25min Pomodoro)
- **📅 Google Calendar integration** - Weekly grid view (Sun-Sat) with multi-day event expansion
- **🎤 Voice commands** - "Hey Hub" wake word support with USB microphone
- **📱 Swipeable interface** - Full-page widgets with navigation dots

## 📱 User Interface

### Swipeable Carousel Layout
The dashboard features a 5-page carousel interface:

1. **Page 1: Family & Todos** - Family member selection and personal todo lists
2. **Page 2: Weather** - Current weather conditions for Medford, NJ
3. **Page 3: Calendar** - Weekly grid view (Sunday to Saturday)
4. **Page 4: Photos** - Family photo slideshow with fade transitions
5. **Page 5: Timers & Actions** - Timer controls and quick action buttons

### Weekly Calendar View
- **7-column grid layout** - Sunday through Saturday
- **Multi-day event expansion** - Events spanning multiple days appear as separate daily entries
- **Today highlighting** - Current day column highlighted in green
- **Compact event display** - Truncated titles with start times
- **Scrollable columns** - Days with many events can scroll within their column

## 🔧 Technical Implementation

### Google Calendar Integration
- **OAuth 2.0 authentication** - Secure access to family Google Calendar
- **Timezone conversion** - UTC to Eastern Time using pytz
- **Multi-day event handling** - Events like "Charlotte Art Camp" (Mon-Fri) split into daily occurrences
- **API rate limiting** - Respects Google Calendar API quotas with 10-minute refresh intervals

### Voice Command System
- **Wake word detection** - "Hey Hub" activation
- **USB microphone support** - Automatic detection of USB PnP Sound Device
- **Command processing** - Timer creation, todo management

### Photo Management
- **Auto-discovery** - Scans ~/Pictures directory
- **Multiple formats** - JPG, PNG, HEIC support
- **Smooth transitions** - Fade effects between photos
- **5-second intervals** - Optimized for viewing experience

### Weather Integration
- **OpenWeather API** - Current conditions and forecasts
- **Auto-refresh** - Updates every 10 minutes to stay within free tier limits
- **Fahrenheit display** - Temperature in °F for US users
- **Error handling** - Graceful fallbacks when API unavailable

## 🛠️ Development Status

### Phase 2 (Week 2) ✅ COMPLETED
- ✅ Voice commands ("Hey Hub") 
- ✅ Weather widget with auto-refresh
- ✅ Photo slideshow with fade transitions
- ✅ Timer functionality with quick presets
- ✅ Google Calendar integration with weekly grid view
- ✅ Swipeable carousel interface with full-page widgets

### Phase 3 (Week 3) - In Progress
- 🔄 Photo widget optimization for full-screen real estate
- ⏳ Samsung Health integration for fitness data
- ⏳ Grocery list management system
- ⏳ Educational games for kids (Charlotte & Daisy)

### Phase 4 (Week 4+) - Planned
- Custom sensors integration
- AI meal planning
- Smart home controls
- Energy monitoring