from homeassistant import config_entries
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN
from .snmp import discover_outlets, discover_device_info
import logging

_LOGGER = logging.getLogger(__name__)

class APCPDUConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                # Test connection and discover outlets
                host = user_input["host"]
                community = user_input["community"]
                
                _LOGGER.info("Testing connection to PDU at %s", host)
                
                # Discover outlets using executor
                outlets = await self.hass.async_add_executor_job(
                    discover_outlets, host, community
                )
                
                # Discover device information
                device_info = await self.hass.async_add_executor_job(
                    discover_device_info, host, community
                )
                
                if not outlets:
                    _LOGGER.error("No outlets discovered on PDU %s", host)
                    errors["base"] = "no_outlets_found"
                else:
                    # Store discovered outlet information
                    outlet_count = len(outlets)
                    outlet_names = {str(num): name for num, name in outlets}
                    
                    _LOGGER.info("Discovered %d outlets on PDU %s", outlet_count, host)
                    
                    config_data = {
                        "host": host,
                        "community": community,
                        "outlet_count": outlet_count,
                        "outlet_names": outlet_names,
                        "device_info": device_info,
                    }
                    
                    # Use device name for title if available, otherwise fall back to host
                    device_name = device_info.get("name", f"APC PDU ({host})")
                    
                    return self.async_create_entry(
                        title=device_name, 
                        data=config_data
                    )
                    
            except Exception as e:
                _LOGGER.exception("Failed to connect to PDU at %s: %s", user_input.get("host"), e)
                errors["base"] = "connection_failed"

        schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("community", default="public"): str,
        })
        
        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors,
            description_placeholders={
                "error_connection": "Could not connect to the PDU. Please check the host and SNMP community string.",
                "error_no_outlets": "No outlets were discovered on this PDU. Please verify this is an APC Smart PDU.",
            }
        )