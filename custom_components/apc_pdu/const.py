# File: custom_components/apc_pdu/const.py

DOMAIN = "apc_pdu"

# Base OIDs for APC Smart PDUs
BASE_OID = "1.3.6.1.4.1.318.1.1.4.4.2.1.3"  # Outlet control
CURRENT_OID = "1.3.6.1.4.1.318.1.1.12.2.3.1.1.2.1"  # Total current reading

# Discovery OIDs for outlet information
OUTLET_INDEX_OID = "1.3.6.1.4.1.318.1.1.12.3.3.1.1.1"  # Outlet indices
OUTLET_NAME_OID = "1.3.6.1.4.1.318.1.1.12.3.3.1.1.2"   # Outlet names

# Device information OIDs
DEVICE_NAME_OID = "1.3.6.1.4.1.318.1.1.12.1.1.0"       # Device name
DEVICE_MODEL_OID = "1.3.6.1.4.1.318.1.1.12.1.5.0"      # Device model
DEVICE_SERIAL_OID = "1.3.6.1.4.1.318.1.1.12.1.6.0"     # Serial number

DEFAULT_PORT = 161
DEFAULT_COMMUNITY = "public"
DEFAULT_NUM_OUTLETS = 8

# Update intervals
SWITCH_UPDATE_INTERVAL = 30  # seconds
SENSOR_UPDATE_INTERVAL = 30  # seconds