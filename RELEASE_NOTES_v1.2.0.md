# Tado CE v1.2.0 Release Notes

## 🎉 What's New in v1.2.0

This release focuses on **stability, reliability, and API quota management**. We've fixed critical race conditions, improved rate limiting, and enhanced the overall robustness of the integration.

---

## 🚨 Breaking Changes

### Zone-Based Device Organization

Each Tado zone now appears as a separate device in Home Assistant for better organization.

**What changed:**
- Zone entities (climate, sensors, switches) → Assigned to their respective zone devices
- Hub entities (API sensors, away mode, weather) → Remain on the Tado CE Hub device
- Device hierarchy: Zone devices are linked via the Hub device

**Good news:**
- ✅ **Entity IDs are preserved** - Your automations will continue to work
- ✅ No manual reconfiguration needed
- ✅ Better organization in the Devices page

See [BREAKING_CHANGES_v1.2.0.md](BREAKING_CHANGES_v1.2.0.md) for detailed migration guide.

---

## 🔧 Critical Fixes (Phase 1)

### 1. Token Refresh Race Condition (CRITICAL)

**Problem:** Multiple concurrent API calls could trigger duplicate token refreshes, causing authentication conflicts and potential quota exhaustion.

**Solution:** New centralized `AuthManager` with thread-safe token management:
- ✅ Thread-safe locking prevents race conditions
- ✅ Token caching (300s) reduces unnecessary refresh calls
- ✅ Automatic token rotation handling
- ✅ All platforms now use centralized auth

**Impact:** Eliminates authentication errors during high-concurrency scenarios (e.g., multiple climate entities updating simultaneously).

---

### 2. Incomplete API Call Tracking (HIGH)

**Problem:** Home state API calls (`/api/v2/homes/{id}/state`) were not being tracked, making quota monitoring incomplete.

**Solution:** Added `CALL_TYPE_HOME_STATE = 7` to the call tracker:
- ✅ All API calls now properly tracked
- ✅ Complete visibility into API usage
- ✅ Accurate quota monitoring

**Impact:** Better understanding of actual API usage, especially for away mode operations.

---

### 3. Immediate Refresh Without Rate Limiting (HIGH)

**Problem:** Rapid user actions (e.g., changing temperature multiple times) could exhaust API quota without any safeguards.

**Solution:** Enhanced immediate refresh with quota awareness:
- ✅ Increased minimum interval from 5s to 10s
- ✅ API quota checking before every refresh
- ✅ Exponential backoff on failures: 10s → 20s → 40s → 80s → 160s → 300s
- ✅ Respects quota thresholds (80% warning, 90% critical)
- ✅ Automatic recovery when quota becomes available

**Impact:** Prevents quota exhaustion while maintaining responsive UI updates.

---

### 4. Rate Limit Reset Time Calculation Bug (MEDIUM)

**Problem:** Buggy modulo logic (`reset_seconds % 86400`) caused incorrect reset time display, especially when reset time was in the past.

**Solution:** Three-strategy approach for accurate calculation:
- ✅ **Strategy 1:** Use API-provided reset time (most accurate)
- ✅ **Strategy 2:** Calculate from last known reset (24h rolling window)
- ✅ **Strategy 3:** Estimate from API call history (fallback)
- ✅ Properly handles negative reset times (shows "unknown" instead of wrong time)

**Impact:** Accurate reset time display helps users understand when their quota will refresh.

---

### 5. Centralized Error Handling (NEW)

**Problem:** Inconsistent error handling across different API calls, making it difficult to diagnose issues and manage entity availability.

**Solution:** New `APIErrorHandler` class for consistent error handling:
- ✅ **Automatic retry logic:** Retries once after 5 seconds on network errors
- ✅ **Detailed error logging:** All API failures logged with operation name and error details
- ✅ **Entity availability management:** Entities marked unavailable after double failure, restored on recovery
- ✅ **Rate limit handling:** Pauses polling until quota resets when rate limit exceeded (429 errors)
- ✅ **Authentication error handling:** Prompts for re-authentication on 401/403 errors
- ✅ **Graceful degradation:** System continues operating with stale data when API is temporarily unavailable

**Impact:** More robust error handling improves reliability and makes troubleshooting easier. Users get clear feedback when issues occur, and the system recovers automatically when API becomes available again.

---

### 6. Thread Safety in Immediate Refresh (CRITICAL)

**Problem:** `async_create_task` was being called from synchronous methods (`set_temperature`, `set_hvac_mode`, etc.), which violates Home Assistant's thread safety requirements and could cause crashes or data corruption.

**Solution:** Fixed async task scheduling in all affected files:
- ✅ **climate.py:** Both heating and AC climate entities now use `call_soon_threadsafe`
- ✅ **water_heater.py:** Hot water entity properly schedules async tasks
- ✅ **switch.py:** All switch entities (away mode, early start, child lock) fixed
- ✅ Proper thread-safe scheduling: Uses `hass.loop.call_soon_threadsafe` to schedule coroutines from sync context

**Impact:** Eliminates potential Home Assistant crashes and data corruption. System is now fully compliant with Home Assistant's async/thread safety requirements.

---

### 7. Database Performance - API Limit Sensor (MEDIUM)

**Problem:** API limit sensor stored all 24-hour call history in attributes (~20KB), exceeding Home Assistant's 16KB database limit and causing performance warnings.

**Solution:** Optimized attribute storage:
- ✅ **Reduced data**: Store only last 100 calls instead of all 24h calls
- ✅ **Size reduction**: 53% smaller (from ~20KB to ~10KB)
- ✅ **Statistics preserved**: Still track 24h call count for monitoring
- ✅ **Database friendly**: Well under 16KB limit with 40% safety margin

**Impact:** Eliminates database performance warnings while maintaining useful call history visibility.

---

## ✨ New Features

### Centralized Authentication Manager

New `AuthManager` class provides robust token management:
- Thread-safe token operations
- 300-second token caching
- Automatic refresh and rotation
- Eliminates duplicate refresh calls

### Enhanced Immediate Refresh

Immediate refresh now includes:
- Quota-aware triggering
- Exponential backoff on failures
- Configurable thresholds
- Automatic recovery

### Improved Rate Limit Tracking

Better visibility into API usage:
- Complete call tracking (including home state)
- Three-strategy reset time calculation
- Accurate quota monitoring
- Historical call data

---

## 🎨 User Experience Improvements

### Zone-Based Devices ([@wrowlands3](https://github.com/wrowlands3))

Each zone now has its own device for better organization:
- Cleaner device page
- Easier to find zone-specific entities
- Better logical grouping

### Improved Entity Naming ([@wrowlands3](https://github.com/wrowlands3))

Zone entities have cleaner names:
- Before: "Tado CE Living Room"
- After: "Living Room"
- Hub entities still have "Tado CE" prefix for clarity

### Optional Weather Sensors ([@ChrisMarriott38](https://github.com/ChrisMarriott38))

Toggle weather sensors on/off:
- **Default: Disabled** for new installations
- Saves 1 API call per sync when disabled
- Existing users: Setting preserved
- Enable in integration options if needed

### Customizable Polling ([@ChrisMarriott38](https://github.com/ChrisMarriott38))

Configure polling to your needs:
- Custom day/night hours (default: 7am-11pm day, 11pm-7am night)
- Custom polling intervals override smart polling
- Quota warning when intervals would exceed limits

---

## 📊 API Usage Optimization

### Before v1.2.0
- Normal polling: 4 API calls (full sync every time)
- Immediate refresh: No quota checking
- Token refresh: Potential duplicate calls
- Weather: Always enabled (1 call per sync)

### After v1.2.0
- Normal polling: 1-2 API calls (quick sync)
- Full sync: Every 6 hours only (4 calls)
- Immediate refresh: Quota-aware with backoff
- Token refresh: Centralized with caching
- Weather: Optional (disabled by default)

**Estimated savings:** ~60-70% reduction in API calls for typical usage.

---

## 🧪 Testing & Quality

### Comprehensive Test Coverage

v1.2.0 includes extensive testing to ensure reliability:

- **Unit Tests**: Thread safety, token caching, error handling
- **Integration Tests**: Complete API call tracking, rate limiting, reset time calculation
- **Property-Based Tests**: Using Hypothesis for edge cases and concurrent scenarios
- **Regression Tests**: 12-24 hour production testing before release

All critical fixes have been thoroughly tested with both unit tests and real-world scenarios.

---

## 🔄 Migration Guide

### For Existing Users

1. **Backup your configuration** (optional but recommended)
2. **Update to v1.2.0** via HACS or manual installation
3. **Restart Home Assistant**
4. **Verify entities** - All entity IDs should be preserved
5. **Check devices page** - Zones now have separate devices

### For New Users

1. **Install v1.2.0** via HACS
2. **Configure integration** with your Tado credentials
3. **Optional:** Enable weather sensors if needed (disabled by default)
4. **Optional:** Customize polling intervals

---

## 📝 Technical Details

### Files Modified

**New Files:**
- `custom_components/tado_ce/auth_manager.py` - Centralized authentication
- `custom_components/tado_ce/error_handler.py` - Centralized error handling

**Modified Files:**
- `custom_components/tado_ce/api_call_tracker.py` - Added CALL_TYPE_HOME_STATE
- `custom_components/tado_ce/tado_api.py` - Fixed reset time calculation, integrated error handler
- `custom_components/tado_ce/immediate_refresh_handler.py` - Added quota checking
- `custom_components/tado_ce/climate.py` - Use AuthManager, fixed thread safety
- `custom_components/tado_ce/sensor.py` - Use AuthManager, optimized API limit sensor attributes
- `custom_components/tado_ce/water_heater.py` - Use AuthManager, fixed thread safety
- `custom_components/tado_ce/switch.py` - Use AuthManager, fixed thread safety
- `custom_components/tado_ce/__init__.py` - Use AuthManager

### Architecture Improvements

1. **Centralized Authentication**
   - Single source of truth for tokens
   - Thread-safe operations
   - Reduced API calls through caching

2. **Centralized Error Handling**
   - Consistent error handling across all API calls
   - Automatic retry with configurable delays
   - Entity availability management
   - Rate limit and authentication error detection

3. **Quota-Aware Operations**
   - All refresh operations check quota first
   - Exponential backoff prevents quota exhaustion
   - Automatic recovery when quota available

4. **Accurate Monitoring**
   - Complete API call tracking
   - Three-strategy reset time calculation
   - Better visibility into usage patterns

---

## 🙏 Credits

### Feature Contributors

- **Zone-based devices & improved naming:** [@wrowlands3](https://github.com/wrowlands3) - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
  - Each zone now has its own device
  - Cleaner entity naming without "Tado CE" prefix
  - Improved zone identification in UI
  
- **API optimization & advanced features:** [@ChrisMarriott38](https://github.com/ChrisMarriott38) - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
  - Optional weather sensors toggle
  - API call tracking with detailed history
  - Enhanced reset time display
  - Customizable day/night polling intervals
  - Boiler flow temperature sensor request
  - Advanced use cases and testing feedback
  
- **Immediate refresh & AC controls:** [@StreborStrebor](https://github.com/StreborStrebor) - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
  - Dashboard updates immediately after user actions
  - Device card update issue reporting
  - AC fan mode and swing mode requests
  
- **Hot water service compatibility:** [@donnie-darko](https://github.com/donnie-darko) - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
  - Service compatibility with official Tado integration
  - Hot water timer with temperature parameter
  - Solar water heater use case requirements

### Bug Reports & Feature Requests

- **403 authentication error:** [@LorDHarA](https://github.com/LorDHarA) - [Issue #1](https://github.com/hiall-fyi/tado_ce/issues/1) *(Fixed in v1.0.1)*
  - Identified hardcoded home ID issue
  - Led to auto-fetch home ID implementation
  
- **Away mode switch:** [Issue #3](https://github.com/hiall-fyi/tado_ce/issues/3) *(Implemented in v1.1.0)*
  - Requested manual Home/Away toggle
  
- **Away mode & delay issues:** [@hapklaar](https://github.com/hapklaar) - [Issue #5](https://github.com/hiall-fyi/tado_ce/issues/5)
  - Away mode switch toggling back issue
  - 2-minute delay for temperature/mode changes
  - Both fixed with Immediate Refresh feature
  
- **Hot water operation modes:** [@ctcampbell](https://github.com/ctcampbell) - [Issue #6](https://github.com/hiall-fyi/tado_ce/issues/6)
  - Requested AUTO/HEAT/OFF modes for hot water
  - Timer-based HEAT mode support
  - Led to comprehensive hot water improvements
  
- **Climate timer duration:** [@greavous1138](https://github.com/greavous1138) - [Issue #7](https://github.com/hiall-fyi/tado_ce/issues/7)
  - Reported duration parameter error in climate service
  - Boost button feature request
  - Helped identify service parameter issues

### Engineering & Critical Fixes

- **Token refresh race condition:** Engineering review identified and fixed
- **API call tracking completeness:** Added missing home state tracking
- **Rate limiting enhancements:** Quota-aware immediate refresh with exponential backoff
- **Reset time calculation:** Fixed buggy modulo logic, implemented three-strategy approach
- **Thread safety:** Fixed async task scheduling across all platforms
- **Database performance:** Optimized API limit sensor attributes

### Community

**Special thanks to:**
- All community members who provided feedback and tested features
- Everyone who reported issues and shared their use cases
- Contributors who helped identify edge cases and improve reliability
- The Home Assistant community for their support and guidance
- All supporters on Buy Me a Coffee

Your feedback and contributions make this integration better for everyone! 🎉

See [RELEASE_CREDITS_v1.2.0.md](RELEASE_CREDITS_v1.2.0.md) for complete credits and community quotes.

---

## 🐛 Known Issues

None at this time. Please report any issues on [GitHub](https://github.com/hiall-fyi/tado_ce/issues).

---

## 📚 Additional Resources

- [CHANGELOG.md](CHANGELOG.md) - Complete change history
- [BREAKING_CHANGES_v1.2.0.md](BREAKING_CHANGES_v1.2.0.md) - Detailed migration guide
- [README.md](README.md) - Installation and configuration guide
- [GitHub Issues](https://github.com/hiall-fyi/tado_ce/issues) - Report bugs or request features

---

## 🚀 What's Next?

Check out the [ROADMAP.md](ROADMAP.md) for planned features and ideas!

We're considering:
- Air Comfort sensors (humidity comfort level)
- Boost button entity
- Multiple homes support

**Want to contribute?** Open an issue or submit a PR!

---

**Thank you for using Tado CE!** Your feedback and contributions make this integration better for everyone. 🎉
