"""API Call Tracker for Tado CE integration."""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from threading import Lock

_LOGGER = logging.getLogger(__name__)

# Call type codes
CALL_TYPE_ZONE_STATES = 1
CALL_TYPE_WEATHER = 2
CALL_TYPE_ZONES = 3
CALL_TYPE_MOBILE_DEVICES = 4
CALL_TYPE_OVERLAY = 5
CALL_TYPE_PRESENCE_LOCK = 6
CALL_TYPE_HOME_STATE = 7

CALL_TYPE_NAMES = {
    CALL_TYPE_ZONE_STATES: "zoneStates",
    CALL_TYPE_WEATHER: "weather",
    CALL_TYPE_ZONES: "zones",
    CALL_TYPE_MOBILE_DEVICES: "mobileDevices",
    CALL_TYPE_OVERLAY: "overlay",
    CALL_TYPE_PRESENCE_LOCK: "presenceLock",
    CALL_TYPE_HOME_STATE: "homeState",
}


class APICallTracker:
    """Track API calls with persistent storage."""
    
    def __init__(self, data_dir: Path, retention_days: int = 14):
        """Initialize API call tracker.
        
        Args:
            data_dir: Directory for storing call history
            retention_days: Number of days to retain history (0 = forever)
        """
        self.data_dir = data_dir
        self.retention_days = retention_days
        self.history_file = data_dir / "api_call_history.json"
        self._lock = Lock()
        self._call_history: Dict[str, List[Dict]] = {}
        self._last_cleanup_date = None  # Track last cleanup date
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
        
        # Cleanup old records
        self.cleanup_old_records()
        self._last_cleanup_date = datetime.now().date()
    
    def _load_history(self):
        """Load call history from disk."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self._call_history = json.load(f)
                _LOGGER.debug(f"Loaded API call history: {len(self._call_history)} dates")
        except Exception as e:
            _LOGGER.error(f"Failed to load API call history: {e}")
            self._call_history = {}
    
    def _save_history(self):
        """Save call history to disk."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self._call_history, f, indent=2)
        except Exception as e:
            _LOGGER.error(f"Failed to save API call history: {e}")
    
    def record_call(self, call_type: int, status_code: int, timestamp: Optional[datetime] = None):
        """Record an API call.
        
        Args:
            call_type: Type of API call (1-6)
            status_code: HTTP status code
            timestamp: Call timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        date_key = timestamp.strftime("%Y-%m-%d")
        today = timestamp.date()
        should_cleanup = False
        
        call_record = {
            "type": call_type,
            "type_name": CALL_TYPE_NAMES.get(call_type, "unknown"),
            "status": status_code,
            "timestamp": timestamp.isoformat()
        }
        
        with self._lock:
            if date_key not in self._call_history:
                self._call_history[date_key] = []
            
            self._call_history[date_key].append(call_record)
            self._save_history()
            
            # Check if we need to cleanup (once per day)
            if self._last_cleanup_date is None or self._last_cleanup_date < today:
                self._last_cleanup_date = today
                should_cleanup = True
        
        # Cleanup outside of lock to avoid deadlock
        if should_cleanup:
            self.cleanup_old_records()
        
        _LOGGER.debug(f"Recorded API call: {CALL_TYPE_NAMES.get(call_type)} (status {status_code})")
    
    def get_call_history(self, days: int = 1) -> List[Dict]:
        """Get list of API calls from the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of call records sorted by timestamp (newest first)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        calls = []
        
        with self._lock:
            for date_key, date_calls in self._call_history.items():
                try:
                    date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                    if date_obj >= cutoff_date:
                        calls.extend(date_calls)
                except ValueError:
                    continue
        
        # Sort by timestamp (newest first)
        calls.sort(key=lambda x: x["timestamp"], reverse=True)
        return calls
    
    def get_recent_calls(self, limit: int = 50) -> List[Dict]:
        """Get the most recent N calls for sensor attributes.
        
        Args:
            limit: Maximum number of calls to return
            
        Returns:
            List of recent call records (newest first)
        """
        all_calls = []
        
        with self._lock:
            for date_calls in self._call_history.values():
                all_calls.extend(date_calls)
        
        # Sort by timestamp (newest first)
        all_calls.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return all_calls[:limit]
    
    def get_call_counts(self, days: int = 1) -> Dict[str, int]:
        """Get counts by call type for the last N days.
        
        Args:
            days: Number of days to count
            
        Returns:
            Dictionary mapping call type names to counts
        """
        calls = self.get_call_history(days)
        counts = {}
        
        for call in calls:
            type_name = call.get("type_name", "unknown")
            counts[type_name] = counts.get(type_name, 0) + 1
        
        return counts
    
    def cleanup_old_records(self):
        """Remove records older than retention period."""
        if self.retention_days == 0:
            # Keep forever
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        with self._lock:
            dates_to_remove = []
            for date_key in self._call_history.keys():
                if date_key < cutoff_str:
                    dates_to_remove.append(date_key)
            
            for date_key in dates_to_remove:
                del self._call_history[date_key]
            
            if dates_to_remove:
                self._save_history()
                _LOGGER.info(f"Cleaned up {len(dates_to_remove)} days of old API call records")
    
    def get_daily_usage(self, date: datetime.date) -> Dict:
        """Get API usage statistics for a specific date.
        
        Args:
            date: Date to get statistics for
            
        Returns:
            Dictionary with usage statistics
        """
        date_key = date.strftime("%Y-%m-%d")
        
        with self._lock:
            date_calls = self._call_history.get(date_key, [])
        
        total_calls = len(date_calls)
        by_type = {}
        
        for call in date_calls:
            type_name = call.get("type_name", "unknown")
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        return {
            "date": date_key,
            "total_calls": total_calls,
            "by_type": by_type
        }
