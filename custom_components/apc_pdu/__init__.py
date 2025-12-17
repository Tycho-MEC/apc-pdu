# File: custom_components/apc_pdu/__init__.py

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the APC PDU component."""
    _LOGGER.info("Setting up APC PDU component")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up APC PDU from a config entry."""
    _LOGGER.info("Setting up APC PDU config entry for %s", entry.data.get("host"))
    
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Successfully set up APC PDU platforms: %s", PLATFORMS)
        return True
    except Exception as e:
        _LOGGER.exception("Failed to forward setup to platforms: %s", e)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading APC PDU config entry for %s", entry.data.get("host"))
    
    try:
        await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        return True
    except Exception as e:
        _LOGGER.exception("Failed to unload APC PDU entry: %s", e)
        return False