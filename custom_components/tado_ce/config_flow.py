"""Config flow for Tado CE - Simplified version."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class TadoCEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tado CE."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TadoCEOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        # Check for existing entries to prevent duplicates
        await self.async_set_unique_id("tado_ce_integration")
        self._abort_if_unique_id_configured()
        
        if user_input is not None:
            # Create entry directly - we use external config file
            return self.async_create_entry(
                title="Tado CE",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "info": "This integration reads data from JSON files. Run 'python3 /config/custom_components/tado_ce/tado_api.py auth' first to authenticate."
            },
        )


class TadoCEOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Tado CE."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            # Validate and convert custom intervals
            processed_input = dict(user_input)
            
            # Handle custom day interval
            day_interval_str = user_input.get('custom_day_interval', '').strip()
            if day_interval_str:
                try:
                    day_interval = int(day_interval_str)
                    if day_interval < 1 or day_interval > 1440:
                        errors['custom_day_interval'] = 'interval_out_of_range'
                    else:
                        processed_input['custom_day_interval'] = day_interval
                except ValueError:
                    errors['custom_day_interval'] = 'invalid_number'
            else:
                processed_input['custom_day_interval'] = None
            
            # Handle custom night interval
            night_interval_str = user_input.get('custom_night_interval', '').strip()
            if night_interval_str:
                try:
                    night_interval = int(night_interval_str)
                    if night_interval < 1 or night_interval > 1440:
                        errors['custom_night_interval'] = 'interval_out_of_range'
                    else:
                        processed_input['custom_night_interval'] = night_interval
                except ValueError:
                    errors['custom_night_interval'] = 'invalid_number'
            else:
                processed_input['custom_night_interval'] = None
            
            if not errors:
                return self.async_create_entry(title="", data=processed_input)

        # Get current options or defaults
        options = self.config_entry.options
        weather_enabled = options.get('weather_enabled', False)
        mobile_devices_enabled = options.get('mobile_devices_enabled', True)
        test_mode_enabled = options.get('test_mode_enabled', False)
        day_start_hour = options.get('day_start_hour', 7)
        night_start_hour = options.get('night_start_hour', 23)
        custom_day_interval = options.get('custom_day_interval')
        custom_night_interval = options.get('custom_night_interval')
        api_history_retention_days = options.get('api_history_retention_days', 14)
        hot_water_timer_duration = options.get('hot_water_timer_duration', 60)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                # API Optimization
                vol.Optional('weather_enabled', default=weather_enabled): bool,
                vol.Optional('mobile_devices_enabled', default=mobile_devices_enabled): bool,
                vol.Optional('test_mode_enabled', default=test_mode_enabled): bool,
                vol.Optional('api_history_retention_days', default=api_history_retention_days): vol.All(
                    int, vol.Range(min=0, max=365)
                ),
                # Polling Configuration
                vol.Optional('day_start_hour', default=day_start_hour): vol.All(
                    int, vol.Range(min=0, max=23)
                ),
                vol.Optional('night_start_hour', default=night_start_hour): vol.All(
                    int, vol.Range(min=0, max=23)
                ),
                vol.Optional('custom_day_interval', default=str(custom_day_interval) if custom_day_interval else ""): str,
                vol.Optional('custom_night_interval', default=str(custom_night_interval) if custom_night_interval else ""): str,
                # Hot Water Settings
                vol.Optional('hot_water_timer_duration', default=hot_water_timer_duration): vol.All(
                    int, vol.Range(min=5, max=1440)
                ),
            }),
            errors=errors,
        )
