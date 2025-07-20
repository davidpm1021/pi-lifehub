# Claude Code Instructions for Life Hub

## Project Context
This is a Raspberry Pi 5 family dashboard project. All code runs on ARM64 architecture with limited resources.

## Development Rules
1. **Performance First**: This runs on a Pi 5. Always consider CPU/RAM usage
2. **Touch Optimized**: Minimum 48px touch targets for 7" screen
3. **Modular Architecture**: Each feature must be independent
4. **Local Storage**: Use SQLite, minimize external API calls
5. **Error Handling**: Never crash the main dashboard
6. **Family Friendly**: UI must work for both kids and adults

## File Structure
- `/backend` - FastAPI services
- `/frontend` - Static web files  
- `/modules` - Feature modules
- `/scripts` - Utility scripts
- `/docs` - Documentation

## Coding Standards
- Python: Use type hints, async where possible
- JavaScript: Vanilla JS preferred, minimal dependencies
- CSS: Mobile-first, high contrast
- All times in local timezone
- All data encrypted at rest

## Testing Requirements
- Test on actual Pi hardware
- Verify touch targets on 7" screen
- Check resource usage stays under 50%
- Ensure 2-second max load time

## Production Best Practices

### Production Deployment
- All services must use systemd with automatic restart
- Implement health check endpoints at /health
- Log rotation mandatory (max 100MB per file)
- Monitor CPU temperature and throttle at 70°C
- Use environment variables for all configuration
- Implement graceful shutdown handlers for GPIO cleanup

### Error Handling Requirements
- All GPIO operations must have try-except blocks
- Network requests need timeout and retry logic
- Sensor reads must handle disconnection gracefully
- Log errors to /var/log/pi-life-hub/ with timestamps
- Never crash - degrade functionality instead

### Security Practices
- No hardcoded credentials anywhere
- API rate limiting on all endpoints
- Input sanitization mandatory
- Use HTTPS even for local network
- Implement authentication before deployment

### Version Control Workflow
- Commit after each working feature
- Use descriptive commit messages
- Test on actual hardware before committing
- Create branches for experimental features
- Document GPIO pin usage in commits

### SSHFS Development Notes
- Development mount: `/home/davidpm/pi-lifehub` → `pi:/home/davidpm/lifehub`
- Virtual environments must be created on Pi directly (path issues)
- Code changes through mount are real-time on Pi
- Always test venv activation on Pi after creating through mount
