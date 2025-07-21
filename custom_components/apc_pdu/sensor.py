# File: custom_components/apc_pdu/sensor.py

import logging
from typing import Optional
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CURRENT_OID
from .snmp import snmp_get

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up APC PDU sensors from a config entry."""
    host = config_entry.data["host"]
    community = config_entry.data["community"]
    device_info = config_entry.data.get("device_info", {})
    
    _LOGGER.info("Setting up APC PDU current sensor for %s", host)
    
    # Create coordinator for data updates
    coordinator = APCPDUCoordinator(hass, host, community)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Create single current sensor entity
    sensors = [APCPDUCurrentSensor(coordinator, device_info)]
    
    async_add_entities(sensors)


class APCPDUCoordinator(DataUpdateCoordinator):
    """Class to manage fetching APC PDU data from SNMP."""
    
    def __init__(self, hass: HomeAssistant, host: str, community: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.host = host
        self.community = community
        
    async def _async_update_data(self):
        """Fetch data from APC PDU."""
        try:
            data = {}
            
            # Fetch total current reading from PDU
            current_value = await self.hass.async_add_executor_job(
                snmp_get, self.host, self.community, CURRENT_OID
            )
            
            if current_value is not None:
                # Convert from deciamps to amps (typical APC PDU format)
                data["total_current"] = current_value / 10.0
                _LOGGER.debug("PDU total current: %.1f A", data["total_current"])
            else:
                _LOGGER.warning("Failed to read total current from PDU")
                data["total_current"] = None
                    
            return data
            
        except Exception as err:
            _LOGGER.exception("Error communicating with APC PDU at %s", self.host)
            raise UpdateFailed(f"Error communicating with APC PDU: {err}")


class APCPDUCurrentSensor(CoordinatorEntity, SensorEntity):
    """Representation of an APC PDU total current sensor."""
    
    def __init__(self, coordinator: APCPDUCoordinator, device_info: dict):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_info = device_info
        self._attr_name = f"APC PDU Total Current"
        self._attr_unique_id = f"{coordinator.host}_total_current"
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_suggested_display_precision = 1
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to group with switches."""
        # Use discovered device info with fallbacks
        device_name = self._device_info.get("name", f"APC PDU ({self.coordinator.host})")
        device_model = self._device_info.get("model", "Smart PDU")
        device_serial = self._device_info.get("serial_number")
        
        device_info_dict = {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": device_name,
            "manufacturer": "APC",
            "model": device_model,
            "configuration_url": f"http://{self.coordinator.host}",
        }
        
        # Add serial number if available
        if device_serial:
            device_info_dict["serial_number"] = device_serial
        
        return DeviceInfo(**device_info_dict)
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "pdu_host": self.coordinator.host,
            "measurement_type": "total_current",
            "update_interval": SCAN_INTERVAL.total_seconds(),
        }
    
    @property
    def native_value(self) -> Optional[float]:
        """Return the current value."""
        return self.coordinator.data.get("total_current")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("total_current") is not None
        )
    
    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:current-ac"