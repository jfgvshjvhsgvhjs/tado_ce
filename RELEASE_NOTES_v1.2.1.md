# Release Notes - v1.2.1 (Hotfix)

**Release Date**: 2026-01-22  
**Type**: Hotfix  
**Priority**: HIGH - Fixes critical upgrade issues from v1.1.0

---

## 🚨 Critical Fixes

### Fixed: Duplicate Hub Cleanup Race Condition (Issue #10)

**Problem**: Users upgrading from v1.1.0 to v1.2.0 ended up with two Tado CE Hubs that couldn't be deleted.

**Root Cause**: The duplicate cleanup logic in v1.2.0 used non-blocking removal (`async_create_task`), causing a race condition where both old and new entries would set up simultaneously.

**Fix**: v1.2.1 uses blocking removal (`await`) to ensure old entries are fully removed before the new one continues setup.

**Impact**: 
- ✅ Automatic cleanup on upgrade from v1.1.0 → v1.2.1
- ✅ No manual intervention needed
- ✅ Only one hub will appear after upgrade

### Fixed: Confusing Entity Names for Multi-Device Zones (Issue #11)

**Problem**: Zones with multiple devices (e.g., 1 sensor + 2 valves) had duplicate entity names:
- "Living Room Battery" (which device?)
- "Living Room Battery" (which device?)
- "Living Room Child Lock" (which valve?)

**Root Cause**: Entity naming didn't account for multiple devices per zone.

**Fix**: v1.2.1 now adds device type + index suffix when a zone has multiple devices:
- ✅ Single device zones: Keep simple names (e.g., "Living Room Battery")
- ✅ Multiple devices, different types: Add device type (e.g., "Living Room VA02 Battery", "Living Room RU01 Battery")
- ✅ Multiple devices, same type: Add device type + index (e.g., "Living Room VA02 (1) Battery", "Living Room VA02 (2) Battery")
- ✅ Applies to: Battery sensors, Connection sensors, Child Lock switches

**Example**:
```
Before (confusing):
- Living Room Battery
- Living Room Battery
- Living Room Child Lock
- Living Room Child Lock

After (clear):
- Living Room VA02 (1) Battery
- Living Room VA02 (2) Battery
- Living Room RU01 Battery
- Living Room VA02 (1) Child Lock
- Living Room VA02 (2) Child Lock
```

---

## 📋 What's Changed

### Migration Improvements

1. **Automatic Migration** (v1 → v2)
   - Detects v1.1.0 config entries and migrates to v1.2.0 format
   - Creates missing data directory if needed
   - Handles missing `zones_info.json` gracefully (will be created on first sync)
   - Logs migration progress for troubleshooting

2. **Duplicate Cleanup** (FIXED)
   - Uses blocking removal to prevent race conditions
   - Automatically removes old v1.1.0 entries on startup
   - Logs each removal step for verification

3. **Better Error Handling**
   - Missing `zones_info.json` no longer blocks setup
   - File is created automatically on first full sync
   - Clearer log messages for debugging

---

## 🔧 Upgrade Instructions

### If You're Already on v1.2.0 (No Issues)

Simply update via HACS:
1. HACS → Integrations → Tado CE → Update
2. Restart Home Assistant

No action needed - this is a preventive fix.

---

### If You're on v1.2.0 with Duplicate Hubs

**Symptoms:**
- Two Tado CE hubs in Devices & Services
- One hub has fewer entities than the other
- Missing zones or entities
- Old hub with unavailable entities (e.g., "Gang" with 7 unavailable entities)

**Solution (Automatic - Recommended):**

1. **Update to v1.2.1**:
   - HACS → Integrations → Tado CE → Update

2. **Restart Home Assistant**
   - v1.2.1 will automatically detect and remove duplicate entries
   - Keeps the newest entry, removes old v1.1.0 leftovers

3. **Verify**:
   - Settings → Devices & Services
   - Should only see ONE Tado CE entry
   - All zones should be visible

**Solution (Manual - If automatic doesn't work):**

1. **Remove ALL Tado CE entries**:
   - Settings → Devices & Services
   - Find all "Tado CE" entries
   - Click "..." → Delete for each one

2. **Update to v1.2.1**:
   - HACS → Integrations → Tado CE → Update

3. **Restart Home Assistant**

4. **Re-add the integration**:
   - Settings → Devices & Services → Add Integration
   - Search "Tado CE"
   - Click to add

**Good news**: Your entity IDs will be preserved, so automations continue to work!

---

### If You're Still on v1.1.0

**Recommended: Clean Install**

1. **Backup your configuration** (optional)
   - Export automations
   - Take screenshots of dashboards

2. **Remove old integration**:
   - Settings → Devices & Services → Tado CE → Delete

3. **Update to v1.2.1**:
   - HACS → Integrations → Tado CE → Update

4. **Restart Home Assistant**

5. **Re-add integration**:
   - Settings → Devices & Services → Add Integration → Tado CE

6. **Update automations** (if needed):
   - `tado_ce.set_temperature_offset` → `tado_ce.set_climate_temperature_offset`
   - Hot water: `operation_mode: "on"` → `operation_mode: "heat"`

**Alternative: Update in Place**

1. **Update automations first** (see above)

2. **Update via HACS**:
   - HACS → Integrations → Tado CE → Update to v1.2.1

3. **Restart Home Assistant**
   - Migration will run automatically

4. **Verify**:
   - Check you only have ONE Tado CE hub
   - Verify all zones are visible
   - Test controls

---

## 🐛 Troubleshooting

### Problem: Still See Two Hubs After Update

**Solution:**
1. Remove ALL Tado CE integration entries
2. Restart Home Assistant
3. Re-add the integration

### Problem: Missing zones_info.json Error

```
Failed to load zone names: [Errno 2] No such file or directory
```

**Solution:**
- This file is created automatically on first sync
- Wait 1-2 minutes after adding the integration
- If error persists, restart Home Assistant

### Problem: All Entities Still Have "Tado CE" Prefix

**Expected behavior:**
- Zone entities: NO prefix (e.g., "Living Room Temperature")
- Hub entities: WITH prefix (e.g., "Tado CE API Usage")

**If all entities have prefix:**
- Old integration entry is still active
- Remove all entries and re-add

---

## 🧪 Testing & Validation

### Integration Tests

v1.2.1 includes comprehensive integration tests for the duplicate cleanup logic:

**Test Suite**: `tests/test_duplicate_cleanup_simple.py`  
**Status**: ✅ **ALL 7 TESTS PASSED**

| Test | Status | Description |
|------|--------|-------------|
| Single Entry No Cleanup | ✅ | Verifies no cleanup when only one entry exists |
| Duplicate Keeps Newest | ✅ | Confirms v2 kept, v1 removed |
| Old Entry Aborts | ✅ | Verifies v1 aborts setup when v2 exists |
| Concurrent Setup | ✅ | Tests race condition protection |
| Three Entries | ✅ | Validates cleanup with 3+ entries |
| Entry Without Version | ✅ | Tests graceful handling of missing version |
| Flag Prevents Multiple Cleanups | ✅ | Confirms flag mechanism works |

**Confidence Level**: 🟢 **95%** (up from 75% before testing)

See [DEV/V1.2.1_TEST_RESULTS.md](DEV/V1.2.1_TEST_RESULTS.md) for detailed test results.

---

## 📝 Technical Details

### Changes in This Release

**File: `custom_components/tado_ce/__init__.py`**
- Enhanced `async_migrate_entry()` function
- Added data directory creation
- Added graceful handling of missing `zones_info.json`
- Improved logging

**File: `custom_components/tado_ce/config_flow.py`**
- Added unique ID: `tado_ce_integration`
- Added duplicate check: `_abort_if_unique_id_configured()`

**File: `custom_components/tado_ce/manifest.json`**
- Version bump: `1.2.0` → `1.2.1`

**File: `README.md`**
- Added comprehensive troubleshooting section
- Added upgrade instructions for v1.1.0 users
- Added known issues and solutions

---

## 🙏 Credits

**Issue #10** (Duplicate Hub): [@marcovn](https://github.com/marcovn), [@ChrisMarriott38](https://github.com/ChrisMarriott38), [@hapklaar](https://github.com/hapklaar) - Thank you for reporting the duplicate hub issue and providing detailed testing feedback!

**Issue #11** (Multi-Device Naming): [@marcovn](https://github.com/marcovn) - Thank you for reporting the multi-device naming issue and providing valuable feedback!

---

## 📚 Related Documentation

- [CHANGELOG.md](CHANGELOG.md) - Full changelog
- [README.md](README.md) - Installation and usage guide
- [DEV/ISSUE_8_MIGRATION_PROBLEM.md](DEV/ISSUE_8_MIGRATION_PROBLEM.md) - Detailed technical analysis

---

## ⚠️ Important Notes

1. **Entity IDs are preserved** during clean reinstall - your automations will continue to work
2. **Backup is optional** but recommended for peace of mind
3. **This is a hotfix** - no new features, only bug fixes
4. **v1.2.0 users without issues** can update without any action needed

---

## 🔜 What's Next

v1.2.2 will focus on:
- Further migration improvements
- Better error messages
- Enhanced documentation

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/hiall-fyi/tado_ce/issues)
