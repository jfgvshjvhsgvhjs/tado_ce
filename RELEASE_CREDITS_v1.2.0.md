# Tado CE v1.2.0 - Credits & Acknowledgments

**Release Date:** 2026-01-21

---

## 🙏 Community Contributors

This release wouldn't be possible without the valuable feedback, feature requests, and bug reports from our amazing community!

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

---

## 🐛 Bug Reports & Issue Reporters

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

## 📊 Impact Summary

**Issues Addressed:** 7 major issues
**Features Implemented:** 18 new features
**Bug Fixes:** 8 critical/high-priority fixes
**API Optimization:** 60-70% reduction in API calls
**Community Engagement:** Active discussions and feedback

---

## 🚀 What This Community Built Together

### v1.2.0 Features (Community-Driven)

- ✅ Zone-based device organization (@wrowlands3)
- ✅ Improved entity naming (@wrowlands3)
- ✅ Optional weather sensors (@ChrisMarriott38, @StreborStrebor)
- ✅ Optional mobile device tracking (@ChrisMarriott38)
- ✅ API call history tracking (@ChrisMarriott38)
- ✅ Enhanced reset time display (@ChrisMarriott38)
- ✅ Customizable polling intervals (@ChrisMarriott38)
- ✅ Immediate refresh (@StreborStrebor, @hapklaar)
- ✅ Hot water operation modes (@ctcampbell - Issue #6)
- ✅ Hot water timer presets (@ctcampbell - Issue #6)
- ✅ Hot water timer service with temperature support (@donnie-darko)
- ✅ Service compatibility with official Tado integration (@donnie-darko)
- ✅ Boiler flow temperature sensor (@ChrisMarriott38 - Issue #4)
- ✅ Away mode switch (Issue #3 - Implemented in v1.1.0)
- ✅ Separate temperature & humidity sensors for advanced calculations (@ChrisMarriott38)
- ✅ Climate timer duration parameter fixes (@greavous1138 - Issue #7)

### Bug Fixes (Community-Reported)

- ✅ 403 authentication error (@LorDHarA - Fixed in v1.0.1)
- ✅ Away mode switch toggling back (@hapklaar - Issue #5)
- ✅ 2-minute delay for updates (@hapklaar - Issue #5)
- ✅ Climate timer duration parameter error (@greavous1138 - Issue #7)
- ✅ Token refresh race condition (Engineering review)
- ✅ Incomplete API call tracking (Engineering review)
- ✅ Rate limit reset time calculation (Engineering review)

---

## 💬 Community Quotes

> "This integration saves me from rate limit headaches!" - Community feedback

> "The immediate refresh feature is exactly what I needed!" - @hapklaar

> "Zone-based devices make organization so much better!" - @wrowlands3

> "API call tracking gives me peace of mind about my quota." - @ChrisMarriott38

> "What an incredible reply! So detailed thanks! I'm ultra novice at code things, just a dabble here and there, but have done Extensive testing for other tools/plugins/web/developers over the years for work." - @ChrisMarriott38

> "Boiler Flow would be my No1 To be included in the API pull. So i dont have to have that as a separate rest API call if possible. to save the Limit." - @ChrisMarriott38

> "This integration turns 'on' which turns the water on until I manually cancel the state (i.e. forever), or 'off' which means my schedule never runs." - @ctcampbell (Issue #6 - Fixed in v1.2.0)

> "First of all, thanks for making this integration, this morning I was actually able to use my Tado system via HA when I woke up!" - @greavous1138

---

## 🎯 Looking Forward

The community continues to shape Tado CE's future! Current discussions:

**From Issue #4:**
- Customizable day/night hours for API polling (shift workers support) - @ChrisMarriott38
- Test mode with enforced API limits for development/testing - @ChrisMarriott38
- Pre-release testing mechanism for community validation - @ChrisMarriott38
- AC fan mode controls (Auto, Low, Medium, High) - @StreborStrebor
- AC swing mode controls (Off, Vertical, Horizontal, Both) - @StreborStrebor
- Service compatibility with official Tado integration - @donnie-darko
- Enhanced API diagnostic codes for tracking specific call types

**From Issue #7:**
- Boost button entity - @greavous1138

**Other Community Requests:**
- Air Comfort sensors (humidity comfort level)
- Multiple homes support

**Want to contribute?** Open an issue or join the discussion on GitHub!

---

**Made with ❤️ by the Tado CE community**

*Special thanks to everyone who uses, tests, reports issues, and supports this project. You make this integration better every day!*

