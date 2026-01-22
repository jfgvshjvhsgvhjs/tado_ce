# Tado CE - Credits & Acknowledgments

**All Versions** - Community contributions that made this integration possible

---

## v1.2.1 (2026-01-22) - Hotfix Release

### Bug Reports & Issue Reporters

**[@marcovn](https://github.com/marcovn)** - [Issue #10](https://github.com/hiall-fyi/tado_ce/issues/10), [Issue #11](https://github.com/hiall-fyi/tado_ce/issues/11)
- Reported duplicate hub issue after v1.1.0 → v1.2.0 upgrade
- Reported confusing entity names for multi-device zones
- Provided valuable feedback and testing
- Helped identify both critical issues in v1.2.1

**[@ChrisMarriott38](https://github.com/ChrisMarriott38)** - [Issue #10](https://github.com/hiall-fyi/tado_ce/issues/10)
- Reported duplicate hub cleanup issue
- Provided detailed testing feedback
- Helped validate the fix

**[@hapklaar](https://github.com/hapklaar)** - [Issue #10](https://github.com/hiall-fyi/tado_ce/issues/10)
- Reported duplicate hub issue
- Contributed to testing and validation

### What Was Fixed

- ✅ **Issue #10**: Duplicate hub cleanup race condition - automatic cleanup on upgrade
- ✅ **Issue #11**: Multi-device zone entity naming - clear device type + index suffixes

---

## v1.2.0 (2026-01-21) - Major Stability Release

### Feature Contributors

**[@wrowlands3](https://github.com/wrowlands3)** - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
- Requested zone-based device organization
- Suggested improved entity naming (remove "Tado CE" prefix)
- Highlighted difficulty in searching and identifying zones in UI
- Helped shape the device organization structure

**[@ChrisMarriott38](https://github.com/ChrisMarriott38)** - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
- Requested boiler flow temperature sensor integration
- Suggested optional weather sensors toggle to save API calls
- Requested API call tracking with detailed history and diagnostic codes
- Suggested enhanced reset time display (human-readable timestamp)
- Proposed customizable day/night polling intervals for shift workers
- Requested test mode with enforced API limits (100 calls) for testing
- Suggested pre-release testing mechanism for community feedback
- Provided extensive testing feedback and bug reports
- Identified API polling patterns and optimization opportunities
- Shared advanced use cases: mold risk calculations, air quality index, weather compensation for heat pumps
- Helped validate temperature and humidity sensor functionality
- Provided detailed feedback on API optimization and usage patterns

**[@donnie-darko](https://github.com/donnie-darko)** - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
- Requested `set_water_heater_timer` service with temperature parameter
- Proposed service compatibility with official Tado integration
- Shared solar water heater use case and automation requirements
- Suggested parameter naming alignment (`time_period` vs `duration`)
- Helped shape service design for seamless migration from official integration
- Provided NODE-RED workflow requirements for solar thermal systems

**[@marcovn](https://github.com/marcovn)** - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
- Participated in Issue #4 discussions
- Contributed to community feedback

**[@StreborStrebor](https://github.com/StreborStrebor)** - [Issue #4](https://github.com/hiall-fyi/tado_ce/issues/4)
- Requested immediate refresh after user actions
- Highlighted the 2-minute delay issue
- Reported device card not updating after temperature/mode changes
- Requested AC fan mode controls (Auto, Low, Medium, High)
- Requested AC swing mode controls (Off, Vertical, Horizontal, Both)
- Suggested disabling weather polling to free up API calls for more frequent updates
- Helped prioritize UX improvements

### Bug Reports & Issue Reporters

**[@LorDHarA](https://github.com/LorDHarA)** - [Issue #1](https://github.com/hiall-fyi/tado_ce/issues/1) *(Fixed in v1.0.1)*
- Identified 403 authentication error for new users
- Led to auto-fetch home ID feature
- Helped improve initial setup experience

**[Issue #3](https://github.com/hiall-fyi/tado_ce/issues/3)** - Away Mode Switch Request *(Implemented in v1.1.0)*
- Requested manual Home/Away toggle
- Improved geofencing control

**[@hapklaar](https://github.com/hapklaar)** - [Issue #5](https://github.com/hiall-fyi/tado_ce/issues/5)
- Reported away mode switch toggling back issue
- Reported 2-minute delay for temperature/mode changes
- Both issues fixed with Immediate Refresh feature
- Generous Buy Me a Coffee supporter! ☕

**[@ctcampbell](https://github.com/ctcampbell)** - [Issue #6](https://github.com/hiall-fyi/tado_ce/issues/6)
- Requested proper AUTO/HEAT/OFF operation modes for hot water
- Highlighted limitations of ON/OFF only modes (water runs forever or schedule never runs)
- Requested timer-based HEAT mode support
- Requested AUTO mode to return to schedule
- Led to comprehensive hot water operation modes implementation in v1.2.0

**[@greavous1138](https://github.com/greavous1138)** - [Issue #7](https://github.com/hiall-fyi/tado_ce/issues/7)
- Reported `duration` parameter not working in `climate.set_temperature` service
- Identified YAML configuration error with timer duration
- Requested boost button feature
- Helped identify service parameter issues
- Contributed to climate timer service improvements

### Community Quotes

> "This integration saves me from rate limit headaches!" - Community feedback

> "The immediate refresh feature is exactly what I needed!" - @hapklaar

> "Zone-based devices make organization so much better!" - @wrowlands3

> "API call tracking gives me peace of mind about my quota." - @ChrisMarriott38

> "What an incredible reply! So detailed thanks! I'm ultra novice at code things, just a dabble here and there, but have done Extensive testing for other tools/plugins/web/developers over the years for work." - @ChrisMarriott38

> "Boiler Flow would be my No1 To be included in the API pull. So i dont have to have that as a separate rest API call if possible. to save the Limit." - @ChrisMarriott38

> "This integration turns 'on' which turns the water on until I manually cancel the state (i.e. forever), or 'off' which means my schedule never runs." - @ctcampbell (Issue #6 - Fixed in v1.2.0)

> "First of all, thanks for making this integration, this morning I was actually able to use my Tado system via HA when I woke up!" - @greavous1138

---

## 🌟 Special Thanks

**Community Testers & Feedback Providers:**
- Users who shared their setup configurations
- Community members who provided detailed use cases
- All supporters on Buy Me a Coffee

**Technical Contributions:**
- Bug reports that helped identify edge cases
- Feature requests that shaped the roadmap
- Detailed feedback on API usage patterns
- Real-world testing across different Tado setups
- Advanced automation examples (mold risk, air quality, weather compensation)
- Documentation improvements for SSH setup and prerequisites

---

## 📊 Overall Impact

**Total Issues Addressed:** 11+ issues across all versions
**Features Implemented:** 20+ new features
**Bug Fixes:** 10+ critical/high-priority fixes
**API Optimization:** 60-70% reduction in API calls
**Community Engagement:** Active discussions and continuous feedback

---

## 🎯 Looking Forward

The community continues to shape Tado CE's future! Current discussions:

**Requested Features:**
- Customizable day/night hours for API polling (shift workers support) - @ChrisMarriott38
- Test mode with enforced API limits for development/testing - @ChrisMarriott38
- Pre-release testing mechanism for community validation - @ChrisMarriott38
- AC fan mode controls (Auto, Low, Medium, High) - @StreborStrebor
- AC swing mode controls (Off, Vertical, Horizontal, Both) - @StreborStrebor
- Boost button entity - @greavous1138
- Air Comfort sensors (humidity comfort level)
- Multiple homes support

**Want to contribute?** Open an issue or join the discussion on [GitHub](https://github.com/hiall-fyi/tado_ce/issues)!

---

**Made with ❤️ by the Tado CE community**

*Special thanks to everyone who uses, tests, reports issues, and supports this project. You make this integration better every day!*
