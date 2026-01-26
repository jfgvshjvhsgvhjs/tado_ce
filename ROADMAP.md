# Roadmap

Feature requests and planned improvements for Tado CE.

For completed features, see [CHANGELOG.md](CHANGELOG.md).

---

## v1.8.0 - Data Files Migration + Schedule Calendar ✅ RELEASED

Per-home data files plus heating schedule visualization.

**Multi-Home Migration:**
- [x] **Per-home data files** - `config_{home_id}.json`, `zones_{home_id}.json`, etc.
- [x] **Auto-migration** - Existing files renamed with home_id suffix
- [x] **Backwards compatible** - Falls back to legacy filenames if needed

**Schedule Calendar:**
- [x] **Heating Schedule Calendar** - Per-zone calendar entities showing heating schedules
- [x] **Read-only** - Displays Tado app schedules, fetched once on startup
- [x] **Optional feature** - Enable in Options (~1 API call per heating zone on startup)
- [x] **Stored locally** - Schedules cached in `schedules.json`, no repeated API calls
- [x] **Per-zone Refresh Schedule button** - Refresh individual zone schedules on demand
- [x] **Instant calendar update** - Calendar refreshes immediately when Refresh Schedule button pressed

**Other:**
- [x] **Home State Sync default OFF** - Consistent with Weather/Mobile Devices ([#55](https://github.com/hiall-fyi/tado_ce/issues/55) - @ChrisMarriott38)
- [x] **API Reset sensor attributes** - Added `reset_at` and `last_reset` showing actual times ([#54](https://github.com/hiall-fyi/tado_ce/issues/54) - @ChrisMarriott38)

---

## v1.9.0 - Hub Device Migration + Smart Heating

Hub device identifier migration plus intelligent heating features.

**Multi-Home Migration:**
- [ ] **Change hub device identifier** - From `tado_ce_hub` to `tado_ce_hub_{home_id}`
- [ ] **Device registry migration** - Existing hub device updated automatically
- [ ] **Entity IDs stable** - No entity ID changes for existing users

**Smart Heating:**
- [ ] **Room-aware Early Start** - Consider room thermal characteristics, not just outside temperature ([Discussion #33](https://github.com/hiall-fyi/tado_ce/discussions/33))
- [ ] **Predictive Heating** - Use weather forecast to optimize heating schedule
- [ ] **Heating Analytics** - Track heating patterns, efficiency metrics, cost estimates
- [ ] **Smart Boost** - One-tap boost with intelligent duration based on current vs target temperature

---

## v2.0.0 - Multiple Homes Enabled + Polish

Major release enabling full multi-home support.

**Multi-Home Support:**
- [ ] **Allow multiple integration entries** - Each entry for a different home
- [ ] **Multi-home setup guide** - Documentation for users with multiple properties

**Setup & Polish:**
- [ ] **Auto-assign Areas** - Suggest HA Areas based on zone names during setup ([#14](https://github.com/hiall-fyi/tado_ce/issues/14))
- [ ] **Setup wizard improvements** - Streamlined flow with better error messages
- [ ] **Delete tado_api.py** - File deprecated in v1.6.0, now fully removed

**Local API (Experimental):**
- [ ] **Local-first, cloud-fallback** - Use local API when available, fall back to cloud
- [ ] **Hybrid mode** - Configurable per-feature (e.g., local for reads, cloud for writes)
- [ ] **Community testing program** - Beta channel for local API testing

**Note**: Local API requires community help to test across different Tado hardware versions. See [Discussion #29](https://github.com/hiall-fyi/tado_ce/discussions/29).

---

## Considering (Need More Feedback)

- Air Comfort sensors (humidity comfort level)
- Boost button entity
- Apply for HACS default repository inclusion
- Max Flow Temperature control (requires OpenTherm, [#15](https://github.com/hiall-fyi/tado_ce/issues/15))
- Combi boiler mode - hide timers/schedules for on-demand hot water ([#15](https://github.com/hiall-fyi/tado_ce/issues/15))

---

## Migration Design

All migrations are cumulative - users can upgrade directly from any version (e.g., v1.6.0 → v2.0.0) and all intermediate migrations will be applied automatically. Each migration step is idempotent (safe to run multiple times).

Entity IDs remain stable throughout migration if entity `unique_id` is unchanged.
