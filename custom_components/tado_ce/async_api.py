"""Async API Client for Tado CE Integration.

This module provides async HTTP client functionality using aiohttp,
replacing the blocking urllib-based calls for better Home Assistant integration.

v1.6.0: Added async_sync() to replace subprocess-based tado_api.py sync.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any

import aiohttp
import asyncio

from .const import (
    DOMAIN, DATA_DIR, CONFIG_FILE, ZONES_FILE, ZONES_INFO_FILE,
    RATELIMIT_FILE, WEATHER_FILE, MOBILE_DEVICES_FILE, HOME_STATE_FILE,
    OFFSETS_FILE, AC_CAPABILITIES_FILE, TADO_API_BASE, TADO_AUTH_URL, 
    CLIENT_ID, API_ENDPOINT_DEVICES
)

_LOGGER = logging.getLogger(__name__)


class TadoAsyncClient:
    """Async Tado API client with automatic token management."""
    
    # Token cache duration (5 minutes to be safe, Tado tokens valid for ~10 minutes)
    TOKEN_CACHE_DURATION = 300
    
    def __init__(self, session: aiohttp.ClientSession):
        """Initialize async client.
        
        Args:
            session: aiohttp ClientSession (should be from Home Assistant)
        """
        self._session = session
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._refresh_lock = asyncio.Lock()
        self._rate_limit: dict = {}
    
    async def _load_config(self) -> dict:
        """Load config from file."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._load_config_sync)
        except Exception as e:
            _LOGGER.error(f"Failed to load config: {e}")
            return {"home_id": None, "refresh_token": None}
    
    def _load_config_sync(self) -> dict:
        """Load config synchronously (for executor)."""
        if not CONFIG_FILE.exists():
            return {"home_id": None, "refresh_token": None}
        with open(CONFIG_FILE) as f:
            return json.load(f)
    
    async def _save_config(self, config: dict):
        """Save config to file atomically."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_config_sync, config)
    
    def _save_config_sync(self, config: dict):
        """Save config synchronously (for executor)."""
        import tempfile
        import shutil
        
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode='w', dir=CONFIG_FILE.parent, delete=False, suffix='.tmp'
        ) as tmp:
            json.dump(config, tmp, indent=2)
            temp_path = tmp.name
        
        shutil.move(temp_path, CONFIG_FILE)
    
    def _parse_ratelimit_headers(self, headers: dict):
        """Parse Tado rate limit headers."""
        policy = headers.get("ratelimit-policy", "")
        ratelimit = headers.get("ratelimit", "")
        
        if "q=" in policy:
            try:
                self._rate_limit["limit"] = int(policy.split("q=")[1].split(";")[0])
            except (ValueError, IndexError):
                pass
        
        if "r=" in ratelimit:
            try:
                self._rate_limit["remaining"] = int(ratelimit.split("r=")[1].split(";")[0])
            except (ValueError, IndexError):
                pass
        
        if "t=" in ratelimit:
            try:
                self._rate_limit["reset_seconds"] = int(ratelimit.split("t=")[1].split(";")[0])
            except (ValueError, IndexError):
                pass
    
    async def save_ratelimit(self, status: str = "ok"):
        """Save current rate limit info to file for sensor updates.
        
        Args:
            status: Status string ("ok", "rate_limited", "error")
        """
        if not self._rate_limit:
            return
        
        limit = self._rate_limit.get("limit", 5000)
        remaining = self._rate_limit.get("remaining", limit)
        reset_seconds = self._rate_limit.get("reset_seconds", 0)
        
        used = limit - remaining
        percentage_used = round((used / limit) * 100, 1) if limit > 0 else 0
        
        # Calculate reset time
        reset_at = None
        reset_human = None
        if reset_seconds > 0:
            reset_dt = datetime.now() + timedelta(seconds=reset_seconds)
            reset_at = reset_dt.isoformat()
            hours = reset_seconds // 3600
            minutes = (reset_seconds % 3600) // 60
            if hours > 0:
                reset_human = f"{hours}h {minutes}m"
            else:
                reset_human = f"{minutes}m"
        
        data = {
            "limit": limit,
            "remaining": remaining,
            "used": used,
            "percentage_used": percentage_used,
            "reset_seconds": reset_seconds,
            "reset_at": reset_at,
            "reset_human": reset_human,
            "last_updated": datetime.now().isoformat(),
            "status": status
        }
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._save_ratelimit_sync, data)
            _LOGGER.debug(f"Rate limit saved: {used}/{limit} ({percentage_used}%)")
        except Exception as e:
            _LOGGER.debug(f"Failed to save rate limit: {e}")
    
    def _save_ratelimit_sync(self, data: dict):
        """Save rate limit synchronously (for executor)."""
        import tempfile
        import shutil
        
        RATELIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode='w', dir=RATELIMIT_FILE.parent, delete=False, suffix='.tmp'
        ) as tmp:
            json.dump(data, tmp, indent=2)
            temp_path = tmp.name
        
        shutil.move(temp_path, RATELIMIT_FILE)
    
    async def get_access_token(self) -> Optional[str]:
        """Get valid access token with automatic refresh.
        
        Uses lock to prevent concurrent token refreshes which would
        waste API calls and potentially cause race conditions.
        
        Returns:
            Valid access token, or None if refresh failed
        """
        # CRITICAL FIX: All token checks must be inside lock to prevent race condition
        # Previously, check outside lock could allow multiple coroutines to pass
        # the initial check simultaneously, then both would refresh.
        async with self._refresh_lock:
            # Check if cached token still valid (with 10s buffer for clock skew)
            if self._access_token and self._token_expiry:
                if datetime.now() < (self._token_expiry - timedelta(seconds=10)):
                    return self._access_token
            
            # Token expired or missing, refresh it
            return await self._refresh_token()
    
    async def _refresh_token(self) -> Optional[str]:
        """Refresh access token using refresh token."""
        config = await self._load_config()
        refresh_token = config.get("refresh_token")
        
        if not refresh_token:
            _LOGGER.error("No refresh token available")
            return None
        
        _LOGGER.debug("Refreshing access token...")
        
        try:
            async with self._session.post(
                f"{TADO_AUTH_URL}/token",
                data={
                    "client_id": CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                }
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    _LOGGER.error(f"Token refresh failed: {resp.status} - {error_text}")
                    if "invalid_grant" in error_text:
                        _LOGGER.error("Refresh token expired - user must re-authenticate")
                        config["refresh_token"] = None
                        await self._save_config(config)
                    return None
                
                data = await resp.json()
                self._access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")
                
                if not self._access_token:
                    _LOGGER.error("No access token in response")
                    return None
                
                # Save new refresh token if rotated
                if new_refresh_token and new_refresh_token != refresh_token:
                    config["refresh_token"] = new_refresh_token
                    await self._save_config(config)
                    _LOGGER.debug("Refresh token rotated and saved")
                
                self._token_expiry = datetime.now() + timedelta(seconds=self.TOKEN_CACHE_DURATION)
                _LOGGER.debug("Access token refreshed successfully")
                return self._access_token
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error during token refresh: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error during token refresh: {e}")
            return None
    
    async def api_call(self, endpoint: str, method: str = "GET", 
                       data: dict = None, parse_ratelimit: bool = True) -> Optional[dict]:
        """Make authenticated API call.
        
        Args:
            endpoint: API endpoint (e.g., "zoneStates", "weather")
            method: HTTP method
            data: Request body data
            parse_ratelimit: Whether to parse rate limit headers
            
        Returns:
            Response data, or None if failed
        """
        token = await self.get_access_token()
        if not token:
            _LOGGER.error("Failed to get access token")
            return None
        
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            _LOGGER.error("No home_id configured")
            return None
        
        url = f"{TADO_API_BASE}/homes/{home_id}/{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            if method == "GET":
                async with self._session.get(url, headers=headers) as resp:
                    if parse_ratelimit:
                        self._parse_ratelimit_headers(dict(resp.headers))
                    
                    if resp.status == 401:
                        _LOGGER.warning("Token expired, invalidating cache")
                        self._access_token = None
                        self._token_expiry = None
                        return None
                    
                    if resp.status == 429:
                        _LOGGER.error("Rate limit exceeded")
                        return None
                    
                    if resp.status != 200:
                        _LOGGER.error(f"API call failed: {resp.status}")
                        return None
                    
                    return await resp.json()
            
            elif method in ("PUT", "POST"):
                json_data = data if data else None
                async with self._session.request(
                    method, url, headers=headers, json=json_data
                ) as resp:
                    if parse_ratelimit:
                        self._parse_ratelimit_headers(dict(resp.headers))
                    
                    if resp.status in (200, 201, 204):
                        if resp.content_length and resp.content_length > 0:
                            return await resp.json()
                        return {}
                    
                    _LOGGER.error(f"API call failed: {resp.status}")
                    return None
            
            elif method == "DELETE":
                async with self._session.delete(url, headers=headers) as resp:
                    if parse_ratelimit:
                        self._parse_ratelimit_headers(dict(resp.headers))
                    
                    if resp.status in (200, 204):
                        return {}
                    
                    _LOGGER.error(f"API call failed: {resp.status}")
                    return None
                    
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error: {e}")
            return None
    
    async def get_device_offset(self, serial: str) -> Optional[float]:
        """Get temperature offset for a specific device."""
        token = await self.get_access_token()
        if not token:
            return None
        
        url = f"{API_ENDPOINT_DEVICES}/{serial}/temperatureOffset"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    _LOGGER.warning(f"Failed to get offset for {serial}: {resp.status}")
                    return None
                
                data = await resp.json()
                return data.get("celsius")
                
        except Exception as e:
            _LOGGER.warning(f"Error getting offset for {serial}: {e}")
            return None
    
    async def set_device_offset(self, serial: str, offset: float) -> bool:
        """Set temperature offset for a specific device."""
        token = await self.get_access_token()
        if not token:
            return False
        
        url = f"{API_ENDPOINT_DEVICES}/{serial}/temperatureOffset"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self._session.put(
                url, headers=headers, json={"celsius": offset}
            ) as resp:
                if resp.status in (200, 204):
                    _LOGGER.info(f"Set offset {offset}°C for device {serial}")
                    return True
                
                _LOGGER.error(f"Failed to set offset: {resp.status}")
                return False
                
        except Exception as e:
            _LOGGER.error(f"Error setting offset: {e}")
            return False
    
    async def set_zone_overlay(self, zone_id: str, setting: dict, 
                               termination: dict) -> bool:
        """Set zone overlay (manual control)."""
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            return False
        
        token = await self.get_access_token()
        if not token:
            return False
        
        url = f"{TADO_API_BASE}/homes/{home_id}/zones/{zone_id}/overlay"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {"setting": setting, "termination": termination}
        
        try:
            async with self._session.put(url, headers=headers, json=payload) as resp:
                self._parse_ratelimit_headers(dict(resp.headers))
                
                if resp.status in (200, 201):
                    return True
                
                # Log detailed error for debugging
                error_text = await resp.text()
                _LOGGER.error(f"Failed to set overlay: {resp.status} - {error_text}")
                _LOGGER.debug(f"Overlay payload was: {payload}")
                return False
                
        except Exception as e:
            _LOGGER.error(f"Error setting overlay: {e}")
            return False
    
    async def delete_zone_overlay(self, zone_id: str) -> bool:
        """Delete zone overlay (return to schedule)."""
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            return False
        
        token = await self.get_access_token()
        if not token:
            return False
        
        url = f"{TADO_API_BASE}/homes/{home_id}/zones/{zone_id}/overlay"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self._session.delete(url, headers=headers) as resp:
                self._parse_ratelimit_headers(dict(resp.headers))
                
                if resp.status in (200, 204):
                    return True
                
                _LOGGER.error(f"Failed to delete overlay: {resp.status}")
                return False
                
        except Exception as e:
            _LOGGER.error(f"Error deleting overlay: {e}")
            return False
    
    async def set_presence_lock(self, state: str) -> bool:
        """Set home presence lock (HOME/AWAY)."""
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            return False
        
        token = await self.get_access_token()
        if not token:
            return False
        
        url = f"{TADO_API_BASE}/homes/{home_id}/presenceLock"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self._session.put(
                url, headers=headers, json={"homePresence": state}
            ) as resp:
                self._parse_ratelimit_headers(dict(resp.headers))
                
                if resp.status in (200, 204):
                    _LOGGER.info(f"Presence lock set to {state}")
                    return True
                
                _LOGGER.error(f"Failed to set presence lock: {resp.status}")
                return False
                
        except Exception as e:
            _LOGGER.error(f"Error setting presence lock: {e}")
            return False
    
    def get_rate_limit(self) -> dict:
        """Get current rate limit info."""
        return self._rate_limit.copy()
    
    # =========================================================================
    # Sync Functions (v1.6.0) - Replace subprocess-based tado_api.py sync
    # =========================================================================
    
    async def async_sync(
        self,
        quick: bool = False,
        weather_enabled: bool = True,
        mobile_devices_enabled: bool = True,
        mobile_devices_frequent_sync: bool = False,
        offset_enabled: bool = False
    ) -> bool:
        """Perform async data sync from Tado API.
        
        Replaces the subprocess-based tado_api.py sync with native async calls.
        
        Args:
            quick: If True, only sync zoneStates (and weather if enabled).
                   If False, also sync zones_info, mobile_devices, offsets, AC caps.
            weather_enabled: Whether to fetch weather data.
            mobile_devices_enabled: Whether to fetch mobile devices.
            mobile_devices_frequent_sync: If True, fetch mobile devices on quick sync too.
            offset_enabled: Whether to fetch temperature offsets.
            
        Returns:
            True if sync succeeded, False otherwise.
        """
        sync_type = "quick" if quick else "full"
        _LOGGER.info(f"Tado CE async sync starting ({sync_type})")
        
        try:
            # Always fetch zone states (most important)
            zones_data = await self.api_call("zoneStates")
            if zones_data is None:
                _LOGGER.error("Failed to fetch zone states")
                await self.save_ratelimit("error")
                return False
            
            await self._save_json_file(ZONES_FILE, zones_data)
            zone_count = len((zones_data.get('zoneStates') or {}).keys())
            _LOGGER.debug(f"Zone states saved ({zone_count} zones)")
            
            # Fetch weather if enabled
            if weather_enabled:
                weather_data = await self.api_call("weather")
                if weather_data:
                    await self._save_json_file(WEATHER_FILE, weather_data)
                    _LOGGER.debug("Weather data saved")
            
            # Always fetch home state (needed for away mode)
            home_state = await self.api_call("state")
            if home_state:
                await self._save_json_file(HOME_STATE_FILE, home_state)
                _LOGGER.debug(f"Home state saved (presence: {home_state.get('presence')})")
            
            # Fetch mobile devices on quick sync if frequent sync enabled
            if quick and mobile_devices_enabled and mobile_devices_frequent_sync:
                mobile_data = await self.api_call("mobileDevices")
                if mobile_data:
                    await self._save_json_file(MOBILE_DEVICES_FILE, mobile_data)
                    _LOGGER.debug(f"Mobile devices saved (frequent sync, {len(mobile_data)} devices)")
            
            # Full sync: also fetch zone info, mobile devices, offsets, AC caps
            if not quick:
                # Fetch zone info
                zones_info = await self.api_call("zones")
                if zones_info:
                    await self._save_json_file(ZONES_INFO_FILE, zones_info)
                    _LOGGER.debug(f"Zone info saved ({len(zones_info)} zones)")
                    
                    # Fetch mobile devices if enabled
                    if mobile_devices_enabled:
                        mobile_data = await self.api_call("mobileDevices")
                        if mobile_data:
                            await self._save_json_file(MOBILE_DEVICES_FILE, mobile_data)
                            _LOGGER.debug(f"Mobile devices saved ({len(mobile_data)} devices)")
                    
                    # Fetch temperature offsets if enabled
                    if offset_enabled:
                        await self._sync_offsets(zones_info)
                    
                    # Fetch AC zone capabilities
                    await self._sync_ac_capabilities(zones_info)
            
            # Save rate limit info
            await self.save_ratelimit("ok")
            
            rl = self._rate_limit
            used = rl.get('limit', 0) - rl.get('remaining', 0) if rl.get('limit') else 0
            _LOGGER.info(
                f"Tado CE async sync SUCCESS ({sync_type}): "
                f"{used}/{rl.get('limit', '?')} API calls used"
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Tado CE async sync failed: {e}")
            await self.save_ratelimit("error")
            return False
    
    async def _save_json_file(self, file_path: Path, data: Any):
        """Save data to JSON file atomically.
        
        Args:
            file_path: Path to save to.
            data: Data to serialize as JSON.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_json_file_sync, file_path, data)
    
    def _save_json_file_sync(self, file_path: Path, data: Any):
        """Save JSON file synchronously (for executor)."""
        import tempfile
        import shutil
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode='w', dir=file_path.parent, delete=False, suffix='.tmp'
        ) as tmp:
            json.dump(data, tmp, indent=2)
            temp_path = tmp.name
        
        shutil.move(temp_path, file_path)
    
    async def _sync_offsets(self, zones_info: list):
        """Sync temperature offsets for all devices.
        
        Args:
            zones_info: List of zone info dicts from API.
        """
        offsets = {}
        
        for zone in zones_info:
            zone_id = str(zone.get('id'))
            zone_type = zone.get('type')
            
            # Only fetch offsets for heating/AC zones (not hot water)
            if zone_type not in ('HEATING', 'AIR_CONDITIONING'):
                continue
            
            devices = zone.get('devices') or []
            for device in devices:
                serial = device.get('shortSerialNo')
                if serial:
                    try:
                        offset = await self.get_device_offset(serial)
                        if offset is not None:
                            offsets[zone_id] = offset
                            _LOGGER.debug(f"Offset for zone {zone_id}: {offset}°C")
                        break  # Only need first device per zone
                    except Exception as e:
                        _LOGGER.warning(f"Failed to fetch offset for device {serial}: {e}")
        
        if offsets:
            await self._save_json_file(OFFSETS_FILE, offsets)
            _LOGGER.debug(f"Offsets saved ({len(offsets)} zones)")
    
    async def _sync_ac_capabilities(self, zones_info: list):
        """Sync AC zone capabilities.
        
        Args:
            zones_info: List of zone info dicts from API.
        """
        ac_capabilities = {}
        
        for zone in zones_info:
            zone_id = str(zone.get('id'))
            zone_type = zone.get('type')
            
            # Only fetch capabilities for AC zones
            if zone_type != 'AIR_CONDITIONING':
                continue
            
            try:
                caps = await self.api_call(f"zones/{zone_id}/capabilities")
                if caps:
                    ac_capabilities[zone_id] = caps
                    modes = [m for m in ['COOL', 'HEAT', 'DRY', 'FAN', 'AUTO'] if m in caps]
                    _LOGGER.debug(f"AC capabilities for zone {zone_id}: modes={modes}")
            except Exception as e:
                _LOGGER.warning(f"Failed to fetch AC capabilities for zone {zone_id}: {e}")
        
        if ac_capabilities:
            await self._save_json_file(AC_CAPABILITIES_FILE, ac_capabilities)
            _LOGGER.debug(f"AC capabilities saved ({len(ac_capabilities)} zones)")

    async def add_meter_reading(self, reading: int, date: str = None) -> bool:
        """Add energy meter reading.
        
        Args:
            reading: Meter reading value
            date: Date string in YYYY-MM-DD format (defaults to today)
            
        Returns:
            True if successful, False otherwise
        """
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            _LOGGER.error("No home_id configured")
            return False
        
        token = await self.get_access_token()
        if not token:
            return False
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{TADO_API_BASE}/homes/{home_id}/meterReadings"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"date": date, "reading": reading}
        
        try:
            async with self._session.post(url, headers=headers, json=payload) as resp:
                self._parse_ratelimit_headers(dict(resp.headers))
                
                if resp.status in (200, 201):
                    _LOGGER.info(f"Added meter reading: {reading} on {date}")
                    return True
                
                _LOGGER.error(f"Failed to add meter reading: {resp.status}")
                return False
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error adding meter reading: {e}")
            return False
        except Exception as e:
            _LOGGER.error(f"Error adding meter reading: {e}")
            return False

    async def identify_device(self, device_serial: str) -> bool:
        """Make a device flash its LED to identify it.
        
        Args:
            device_serial: Device serial number
            
        Returns:
            True if successful, False otherwise
        """
        token = await self.get_access_token()
        if not token:
            _LOGGER.error("Failed to get access token")
            return False
        
        url = f"{API_ENDPOINT_DEVICES}/{device_serial}/identify"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self._session.post(url, headers=headers) as resp:
                if resp.status in (200, 204):
                    _LOGGER.info(f"Identify command sent to device {device_serial}")
                    return True
                
                _LOGGER.error(f"Failed to identify device: {resp.status}")
                return False
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error identifying device: {e}")
            return False
        except Exception as e:
            _LOGGER.error(f"Error identifying device: {e}")
            return False

    async def set_away_configuration(
        self, zone_id: str, mode: str, 
        temperature: float = None, comfort_level: int = 50
    ) -> bool:
        """Set away configuration for a zone.
        
        Args:
            zone_id: Zone ID
            mode: Away mode ('auto', 'manual', or 'off')
            temperature: Target temperature for manual mode
            comfort_level: Comfort level for auto mode (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        config = await self._load_config()
        home_id = config.get("home_id")
        if not home_id:
            _LOGGER.error("No home_id configured")
            return False
        
        token = await self.get_access_token()
        if not token:
            return False
        
        url = f"{TADO_API_BASE}/homes/{home_id}/zones/{zone_id}/schedule/awayConfiguration"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Build payload based on mode
        if mode == "auto":
            payload = {
                "type": "HEATING",
                "autoAdjust": True,
                "comfortLevel": comfort_level,
                "setting": {"type": "HEATING", "power": "OFF"}
            }
        elif mode == "manual" and temperature is not None:
            payload = {
                "type": "HEATING",
                "autoAdjust": False,
                "setting": {
                    "type": "HEATING",
                    "power": "ON",
                    "temperature": {"celsius": temperature}
                }
            }
        else:  # off
            payload = {
                "type": "HEATING",
                "autoAdjust": False,
                "setting": {"type": "HEATING", "power": "OFF"}
            }
        
        try:
            async with self._session.put(url, headers=headers, json=payload) as resp:
                self._parse_ratelimit_headers(dict(resp.headers))
                
                if resp.status in (200, 204):
                    _LOGGER.info(f"Set away configuration for zone {zone_id}: {mode}")
                    return True
                
                _LOGGER.error(f"Failed to set away configuration: {resp.status}")
                return False
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error setting away configuration: {e}")
            return False
        except Exception as e:
            _LOGGER.error(f"Error setting away configuration: {e}")
            return False


# Global client instance (per Home Assistant instance)
# CRITICAL: Must be cleaned up in async_unload_entry() to prevent memory leak
_async_clients: dict = {}


def get_async_client(hass) -> TadoAsyncClient:
    """Get or create async client for Home Assistant instance.
    
    Args:
        hass: Home Assistant instance
        
    Returns:
        TadoAsyncClient instance for this hass instance
        
    Note:
        Client is cached per hass instance. Call cleanup_async_client()
        in async_unload_entry() to prevent memory leaks.
    """
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    
    hass_id = id(hass)
    if hass_id not in _async_clients:
        session = async_get_clientsession(hass)
        _async_clients[hass_id] = TadoAsyncClient(session)
        _LOGGER.debug("Created new TadoAsyncClient")
    
    return _async_clients[hass_id]


def cleanup_async_client(hass) -> bool:
    """Clean up async client for Home Assistant instance.
    
    MUST be called in async_unload_entry() to prevent memory leaks
    when integration is reloaded or removed.
    
    Args:
        hass: Home Assistant instance
        
    Returns:
        True if client was cleaned up, False if no client existed
    """
    hass_id = id(hass)
    if hass_id in _async_clients:
        # Clear token cache to ensure clean state on reload
        client = _async_clients[hass_id]
        client._access_token = None
        client._token_expiry = None
        del _async_clients[hass_id]
        _LOGGER.debug("Cleaned up TadoAsyncClient")
        return True
    return False
