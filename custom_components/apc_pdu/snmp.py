# File: custom_components/apc_pdu/snmp.py

import logging
from typing import Optional, Dict, List, Tuple

from puresnmp import Client, V2C, PyWrapper
from puresnmp.types import Integer 

_LOGGER = logging.getLogger(__name__)

def _clean_snmp_string(value) -> str:
    """Clean SNMP string values that may be bytes or byte string representations."""
    if value is None:
        return ""
    
    # Handle actual bytes
    if isinstance(value, bytes):
        return value.decode('utf-8').strip('"')
    
    # Convert to string first
    str_value = str(value)
    
    # Handle string representations of bytes like "b'value'"
    if str_value.startswith("b'") and str_value.endswith("'"):
        return str_value[2:-1]  # Remove b' and '
    elif str_value.startswith('b"') and str_value.endswith('"'):
        return str_value[2:-1]  # Remove b" and "
    
    # Regular string, just strip quotes
    return str_value.strip('"')

def snmp_get(ip: str, community: str, oid: str) -> Optional[int]:
    """Synchronous SNMP GET operation for executor."""
    try:
        client = PyWrapper(Client(ip, V2C(community)))
        # This is now sync and will be run in executor
        import asyncio
        value = asyncio.run(client.get(oid))
        return int(value)
    except Exception as e:
        _LOGGER.exception("SNMP GET failed on %s (%s): %s", ip, oid, e)
        return None

def snmp_get_string(ip: str, community: str, oid: str) -> Optional[str]:
    """Synchronous SNMP GET operation for string values."""
    try:
        client = PyWrapper(Client(ip, V2C(community)))
        import asyncio
        value = asyncio.run(client.get(oid))
        return str(value)
    except Exception as e:
        _LOGGER.exception("SNMP GET string failed on %s (%s): %s", ip, oid, e)
        return None

def snmp_walk(ip: str, community: str, base_oid: str) -> Dict[str, any]:
    """Synchronous SNMP WALK operation for executor."""
    try:
        client = PyWrapper(Client(ip, V2C(community)))
        import asyncio
        results = {}
        
        # Perform SNMP walk
        async def _walk():
            async for oid, value in client.walk(base_oid):
                results[str(oid)] = value
            return results
        
        return asyncio.run(_walk())
    except Exception as e:
        _LOGGER.exception("SNMP WALK failed on %s (%s): %s", ip, base_oid, e)
        return {}





# ---------------------------------------------------------------------------
# Profile-based detection
# ---------------------------------------------------------------------------

def detect_pdu_profile(ip: str, community: str) -> Optional[Dict]:
    """Probe each PDU profile in order and return the first one whose
    base_oid.1 responds with a valid outlet state (1 = on, 2 = off).

    Returns the matching profile dict from PDU_PROFILES, or None if no
    profile matched.  
    """
    from .const import PDU_PROFILES

    for profile in PDU_PROFILES:
        probe_oid = f"{profile['base_oid']}.1"
        _LOGGER.debug(
            "Probing %s — profile '%s' (base OID: %s)",
            ip, profile["label"], profile["base_oid"],
        )
        value = snmp_get(ip, community, probe_oid)
        if value in (1, 2):
            _LOGGER.info(
                "PDU %s matched profile '%s' — outlet 1 is %s",
                ip, profile["label"], "on" if value == 1 else "off",
            )
            return profile
        _LOGGER.debug(
            "PDU %s: profile '%s' returned %s — skipping",
            ip, profile["label"], value,
        )

    _LOGGER.warning(
        "PDU %s: no profile matched. Outlet control may not work.", ip
    )
    return None


# ---------------------------------------------------------------------------
# Discovery helpers 
# ---------------------------------------------------------------------------

def discover_outlets(ip: str, community: str) -> Tuple[List[Tuple[int, str]], Optional[Dict]]:
    """Detect PDU profile, walk outlet index/name tables, and return both.

    Returns:
        (outlets, profile)
        - outlets: sorted list of (outlet_number, outlet_name)
        - profile: the matched PDU profile dict (or DEFAULT_PROFILE on failure)
    """
    try:
        from .const import DEFAULT_PROFILE

        profile = detect_pdu_profile(ip, community)
        if profile is None:
            _LOGGER.warning(
                "Using default profile for %s — outlet control may not work", ip
            )
            profile = DEFAULT_PROFILE

        index_results = snmp_walk(ip, community, profile["outlet_index_oid"])
        name_results = snmp_walk(ip, community, profile["outlet_name_oid"])
        
        outlets = []
        
        # Process index results to get outlet numbers
        for oid, value in index_results.items():
            try:
                # Extract the outlet index from the OID
                # OID format: base_oid.X where X is outlet number
                outlet_num = int(oid.split('.')[-1])
                outlet_index = int(value)
                
                # Find corresponding name
                outlet_name = f"Outlet {outlet_index}"  # Default name
                
                # Look for matching name OID
                for name_oid_key, name_value in name_results.items():
                    if name_oid_key.endswith(f".{outlet_num}"):
                        outlet_name = _clean_snmp_string(name_value)
                        break
                
                outlets.append((outlet_index, outlet_name))
                _LOGGER.debug("Discovered outlet %d: %s", outlet_index, outlet_name)
                
            except (ValueError, IndexError) as e:
                _LOGGER.warning("Failed to parse outlet from OID %s: %s", oid, e)
                continue
       
        # Sort by outlet number
        outlets.sort(key=lambda x: x[0])
        _LOGGER.info("Discovered %d outlets on PDU %s (profile: %s)", len(outlets), ip, profile["label"],)
        return outlets, profile
        
    except Exception as e:
        _LOGGER.exception("Failed to discover outlets on %s: %s", ip, e)
        return ([], None)

def discover_device_info(ip: str, community: str, profile: Dict) -> Dict[str, str]:
    """Discover device information from the PDU."""
    try:
        
        device_info = {}
        
        # Get device name
        device_name = snmp_get_string(ip, community, profile["device_name_oid"])
        if device_name:
            device_info["name"] = _clean_snmp_string(device_name)
        
        # Get device model
        device_model = snmp_get_string(ip, community, profile["device_model_oid"])
        if device_model:
            device_info["model"] = _clean_snmp_string(device_model)
        
        # Get serial number
        device_serial = snmp_get_string(ip, community, profile["device_serial_oid"])
        if device_serial:
            device_info["serial_number"] = _clean_snmp_string(device_serial)
        
        _LOGGER.info(
            "Discovered device info for %s: %s (Model: %s, S/N: %s)", 
            ip, 
            device_info.get("name", "Unknown"), 
            device_info.get("model", "Unknown"),
            device_info.get("serial_number", "Unknown")
        )
        
        return device_info
        
    except Exception as e:
        _LOGGER.exception("Failed to discover device info on %s: %s", ip, e)
        return {}

def snmp_set(ip: str, community: str, oid: str, value: int) -> bool:
    """Synchronous SNMP SET operation for executor."""
    try:
        client = PyWrapper(Client(ip, V2C(community)))
        # This is now sync and will be run in executor
        import asyncio
        asyncio.run(client.set(oid, Integer(value)))
        _LOGGER.debug("SNMP SET successful on %s (%s) = %s", ip, oid, value)
        return True
    except Exception as e:
        _LOGGER.exception("SNMP SET failed on %s (%s): %s", ip, oid, e)
        return False