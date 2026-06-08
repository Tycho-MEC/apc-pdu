# File: custom_components/apc_pdu/const.py

DOMAIN = "apc_pdu"

# ---------------------------------------------------------------------------
# PDU profiles
#
# Each profile bundles every OID needed for a PDU family into one place.
# Detection probes base_oid.1 (outlet 1); the first profile that returns a
# valid outlet state (1 = on, 2 = off) is selected for the whole integration.
#
# Adding a new family = adding one entry here.  No other file needs changing.
# ---------------------------------------------------------------------------

PDU_PROFILES = [
    {
        # sPDU / MasterSwitch family — older switched rack PDUs (AP7920, AP7930 …)
        # Also probed first so existing sPDU installs keep working without migration.
        "family":           "rpdu",   # shares rPDU outlet/device OIDs
        "label":            "sPDU (masterswitch)",
        "base_oid":         "1.3.6.1.4.1.318.1.1.4.4.2.1.3",      # sPDUOutletControlOutletCommand
        "current_oid":      "1.3.6.1.4.1.318.1.1.12.2.3.1.1.2.1", # rPDULoadStatusLoad (tenths of A)
        "current_divisor":  10.0,                                 # Divide by 10
        "outlet_index_oid": "1.3.6.1.4.1.318.1.1.12.3.3.1.1.1",   # rPDUOutletControlIndex
        "outlet_name_oid":  "1.3.6.1.4.1.318.1.1.12.3.3.1.1.2",   # rPDUOutletControlOutletName
        "device_name_oid":  "1.3.6.1.4.1.318.1.1.12.1.1.0",       # rPDUIdentName
        "device_model_oid": "1.3.6.1.4.1.318.1.1.12.1.5.0",       # rPDUIdentModelNumber
        "device_serial_oid":"1.3.6.1.4.1.318.1.1.12.1.6.0",       # rPDUIdentSerialNumber
    },
    {
        # rPDU Switched Rack PDU family — newer rPDU (AP7911, AP7921 …)
        "family":           "rpdu",
        "label":            "rPDU (switched rack)",
        "base_oid":         "1.3.6.1.4.1.318.1.1.12.3.3.1.1.4",   # rPDUOutletControlOutletCommand
        "current_oid":      "1.3.6.1.4.1.318.1.1.12.2.3.1.1.2.1", # rPDULoadStatusLoad (tenths of A)
        "current_divisor":  10.0,                                 # Divide by 10
        "outlet_index_oid": "1.3.6.1.4.1.318.1.1.12.3.3.1.1.1",   # rPDUOutletControlIndex
        "outlet_name_oid":  "1.3.6.1.4.1.318.1.1.12.3.3.1.1.2",   # rPDUOutletControlOutletName
        "device_name_oid":  "1.3.6.1.4.1.318.1.1.12.1.1.0",       # rPDUIdentName
        "device_model_oid": "1.3.6.1.4.1.318.1.1.12.1.5.0",       # rPDUIdentModelNumber
        "device_serial_oid":"1.3.6.1.4.1.318.1.1.12.1.6.0",       # rPDUIdentSerialNumber
    },
    {
        # rPDU2 Switched Rack PDU family (AP84xx, AP86xx, AP89xx …)
        "family":           "rpdu2",
        "label":            "rPDU2 (switched rack v2)",
        "base_oid":         "1.3.6.1.4.1.318.1.1.26.9.2.4.1.5",   # rPDU2OutletSwitchedControlCommand
        "current_oid":      "1.3.6.1.4.1.318.1.1.26.6.3.1.5.1",   # rPDU2PhaseStatusCurrent (tenths of A)
        "current_divisor":  10.0,                                 # Divide by 10
        "outlet_index_oid": "1.3.6.1.4.1.318.1.1.26.9.2.3.1.1",   # rPDU2OutletSwitchedStatusIndex
        "outlet_name_oid":  "1.3.6.1.4.1.318.1.1.26.9.2.3.1.3",   # rPDU2OutletSwitchedStatusName
        "device_name_oid":  "1.3.6.1.4.1.318.1.1.26.2.1.1.3.1",   # rPDU2IdentName
        "device_model_oid": "1.3.6.1.4.1.318.1.1.26.2.1.1.8.1",   # rPDU2IdentModelNumber
        "device_serial_oid":"1.3.6.1.4.1.318.1.1.26.2.1.1.9.1",   # rPDU2IdentSerialNumber
    },
]

# Fallback profile used when detection fails or for pre-profile config entries
DEFAULT_PROFILE = PDU_PROFILES[0]

DEFAULT_PORT = 161
DEFAULT_COMMUNITY = "public"

# Update intervals
SWITCH_UPDATE_INTERVAL = 30  # seconds
SENSOR_UPDATE_INTERVAL = 30  # seconds
