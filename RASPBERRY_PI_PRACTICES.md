# Raspberry Pi Production Development Framework

## 1. Iterative Development Workflow
- Start with working MVP features
- Test each feature on actual hardware before moving on
- Use git commits as checkpoints after each working feature
- Document hardware connections in code comments

### SSHFS Development Setup
**CRITICAL**: When using SSHFS mount for development:
- Mount point: `/home/davidpm/pi-lifehub` (development machine)
- Pi actual path: `/home/davidpm/lifehub` (on Pi device)
- Virtual environments MUST be created on the Pi directly, not through SSHFS
- Python venv stores absolute paths that break across mount boundaries

**Setup Process:**
1. SSHFS mount: `sshfs davidpm@192.168.86.36:/home/davidpm/lifehub /home/davidpm/pi-lifehub`
2. Develop through mount, but create venv on Pi:
   ```bash
   # On Pi directly:
   ssh davidpm@192.168.86.36
   cd /home/davidpm/lifehub
   rm -rf venv  # if exists with wrong paths
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

**Project Structure:**
- Development machine mount: `/home/davidpm/pi-lifehub/` (SSHFS mounted)
- Pi actual files: `/home/davidpm/lifehub/` (on 192.168.86.36)
- Git repository: Only work in `/home/davidpm/pi-lifehub/` (mounted directory)
- Service runs from: `/home/davidpm/lifehub/` on Pi

## 2. Claude Code Optimization Patterns
Use parallel operations for efficiency:
'Simultaneously create: 1) sensor reading module, 2) web dashboard, 3) systemd service, 4) monitoring script'

## 3. Resource Management
- Monitor memory usage: keep under 1GB for Pi 5
- Use generators for data processing
- Implement connection pooling for databases
- Cache static content aggressively
- Profile CPU usage regularly

## 4. Sensor Integration Template
All sensor code must follow:
- Initialize with error handling
- Implement read retry logic (3 attempts)
- Log failures but continue operation
- Provide fallback/cached values
- Clean disconnect handling

## 5. Production Monitoring
Required for all deployments:
- CPU temperature logging
- Memory usage tracking  
- Service uptime monitoring
- Error rate tracking
- Network connectivity status

## 6. Debugging Workflow
When errors occur:
1. Check system logs: journalctl -u service-name
2. Verify GPIO connections
3. Test sensors individually
4. Monitor resource usage
5. Check for thermal throttling

## 7. Deployment Checklist
Before production:
- [ ] Error handling on all I/O operations
- [ ] Systemd service created and tested
- [ ] Logs rotating properly
- [ ] Health endpoint responding
- [ ] Resource limits configured
- [ ] Auto-restart verified
- [ ] Hardware disconnection handled
- [ ] Security measures in place

## 8. Common Pi Gotchas
- GPIO pins not released properly
- I2C bus conflicts
- Power supply inadequate
- SD card wear from excessive logging
- Network disconnections
- Temperature throttling

## 9. Performance Benchmarks
Target metrics for Pi 5:
- Web response time: <200ms
- Sensor read cycle: <100ms  
- CPU usage idle: <10%
- Memory usage: <1GB
- Temperature: <60°C normal operation

## 10. Business Scaling Path
MVP → Enhanced → Commercial:
- Local dashboard → Cloud integration
- Single device → Multi-device support
- Free → Subscription model
- Individual → Multi-tenant

Document specific to Pi Life Hub family dashboard project.