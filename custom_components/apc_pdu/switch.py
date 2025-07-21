# File: custom_components/apc_pdu/switch.py

import asyncio
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .snmp import snmp_get, snmp_set
from .const import DOMAIN, BASE_OID

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = config_entry.data
    host = data["host"]
    community = data["community"]
    outlet_count = int(data["outlet_count"])
    outlet_names = data.get("outlet_names", {})
    device_info = data.get("device_info", {})
    
    _LOGGER.info("Setting up %d outlet switches for PDU %s", outlet_count, host)
    
    entities = []
    for outlet in range(1, outlet_count + 1):
        outlet_name = outlet_names.get(str(outlet), f"Outlet {outlet}")
        entities.append(APCPDUSwitch(hass, host, community, outlet, outlet_name, device_info))
    
    async_add_entities(entities)

class APCPDUSwitch(SwitchEntity):
    _attr_should_poll = True

    def __init__(self, hass: HomeAssistant, host: str, community: str, outlet: int, outlet_name: str, device_info: dict) -> None:
        self._hass = hass
        self._host = host
        self._community = community
        self._outlet = outlet
        self._outlet_name = outlet_name
        self._device_info = device_info
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        return f"APC {self._outlet_name}"

    @property
    def unique_id(self) -> str:
        return f"{self._host}_{self._outlet}"

    @property
    def is_on(self) -> bool:
        return self._state == 1

    @property
    def available(self) -> bool:
        return self._available

    @property
    def device_info(self) -> DeviceInfo:
        # Use discovered device info with fallbacks
        device_name = self._device_info.get("name", f"APC PDU ({self._host})")
        device_model = self._device_info.get("model", "Smart PDU")
        device_serial = self._device_info.get("serial_number")
        
        device_info_dict = {
            "identifiers": {(DOMAIN, self._host)},
            "name": device_name,
            "manufacturer": "APC",
            "model": device_model,
            "configuration_url": f"http://{self._host}",
        }
        
        # Add serial number if available
        if device_serial:
            device_info_dict["serial_number"] = device_serial
        
        return DeviceInfo(**device_info_dict)

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "outlet_number": self._outlet,
            "outlet_name": self._outlet_name,
            "pdu_host": self._host,
        }

    async def async_update(self) -> None:
        """Fetch new state data for this switch."""
        oid = f"{BASE_OID}.{self._outlet}"
        try:
            result = await self._hass.async_add_executor_job(
                snmp_get, self._host, self._community, oid
            )
            
            if result in [1, 2]:  # 1=on, 2=off for APC PDUs
                self._state = result
                self._available = True
            else:
                _LOGGER.warning(f"Invalid state {result} for outlet {self._outlet} ({self._outlet_name})")
                self._available = False
                
        except Exception as e:
            _LOGGER.error(f"Error updating outlet {self._outlet} ({self._outlet_name}): {e}")
            self._available = False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        oid = f"{BASE_OID}.{self._outlet}"
        try:
            success = await self._hass.async_add_executor_job(
                snmp_set, self._host, self._community, oid, 1
            )
            if success:
                self._available = True
                # Wait for state change with retry
                expected_state = 1
                state_confirmed = False
                for attempt in range(5):  # Try up to 5 times
                    await asyncio.sleep(0.1 * (attempt + 1))  # 0.1, 0.2, 0.3, 0.4, 0.5
                    await self.async_update()
                    if self._state == expected_state:
                        state_confirmed = True
                        break
                
                if not state_confirmed:
                    _LOGGER.warning(f"State change not confirmed for outlet {self._outlet} ({self._outlet_name}) after 5 attempts")
                
                self.async_write_ha_state()
            else:
                _LOGGER.warning(f"Failed to turn on outlet {self._outlet} ({self._outlet_name})")
                raise HomeAssistantError(f"Failed to turn on outlet {self._outlet} ({self._outlet_name})")
        except Exception as e:
            _LOGGER.error(f"Error turning on outlet {self._outlet} ({self._outlet_name}): {e}")
            self._available = False
            raise HomeAssistantError(f"Error turning on outlet {self._outlet} ({self._outlet_name}): {e}")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        oid = f"{BASE_OID}.{self._outlet}"
        try:
            success = await self._hass.async_add_executor_job(
                snmp_set, self._host, self._community, oid, 2
            )
            if success:
                self._available = True
                # Wait for state change with retry
                expected_state = 2
                state_confirmed = False
                for attempt in range(5):  # Try up to 5 times
                    await asyncio.sleep(0.1 * (attempt + 1))  # 0.1, 0.2, 0.3, 0.4, 0.5
                    await self.async_update()
                    if self._state == expected_state:
                        state_confirmed = True
                        break
                
                if not state_confirmed:
                    _LOGGER.warning(f"State change not confirmed for outlet {self._outlet} ({self._outlet_name}) after 5 attempts")
                
                self.async_write_ha_state()
            else:
                _LOGGER.warning(f"Failed to turn off outlet {self._outlet} ({self._outlet_name})")
                raise HomeAssistantError(f"Failed to turn off outlet {self._outlet} ({self._outlet_name})")
        except Exception as e:
            _LOGGER.error(f"Error turning off outlet {self._outlet} ({self._outlet_name}): {e}")
            self._available = False
            raise HomeAssistantError(f"Error turning off outlet {self._outlet} ({self._outlet_name}): {e}")