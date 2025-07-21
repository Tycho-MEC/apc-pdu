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

def discover_outlets(ip: str, community: str) -> List[Tuple[int, str]]:
    """Discover outlets and their names from the PDU."""
    try:
        from .const import OUTLET_INDEX_OID, OUTLET_NAME_OID
        
        # Walk the outlet index OID to get all outlet numbers
        index_results = snmp_walk(ip, community, OUTLET_INDEX_OID)
        name_results = snmp_walk(ip, community, OUTLET_NAME_OID)
        
        outlets = []
        
        # Process index results to get outlet numbers
        for oid, value in index_results.items():
            try:
                # Extract the outlet index from the OID
                # OID format: 1.3.6.1.4.1.318.1.1.12.3.3.1.1.1.X where X is outlet number
                outlet_num = int(oid.split('.')[-1])
                outlet_index = int(value)
                
                # Find corresponding name
                name_oid = None
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
        _LOGGER.info("Discovered %d outlets on PDU %s", len(outlets), ip)
        return outlets
        
    except Exception as e:
        _LOGGER.exception("Failed to discover outlets on %s: %s", ip, e)
        return []

def discover_device_info(ip: str, community: str) -> Dict[str, str]:
    """Discover device information from the PDU."""
    try:
        from .const import DEVICE_NAME_OID, DEVICE_MODEL_OID, DEVICE_SERIAL_OID
        
        device_info = {}
        
        # Get device name
        device_name = snmp_get_string(ip, community, DEVICE_NAME_OID)
        if device_name:
            device_info["name"] = _clean_snmp_string(device_name)
        
        # Get device model
        device_model = snmp_get_string(ip, community, DEVICE_MODEL_OID)
        if device_model:
            device_info["model"] = _clean_snmp_string(device_model)
        
        # Get serial number
        device_serial = snmp_get_string(ip, community, DEVICE_SERIAL_OID)
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