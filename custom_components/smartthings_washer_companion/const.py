"""Constants for SmartThings Washer Companion."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "smartthings_washer_companion"
PLATFORMS = ["select"]

SERVICE_SCHEDULE_WASH = "schedule_wash"
ATTR_CYCLE = "cycle"
ATTR_FINISH_AT = "finish_at"

CONF_SMARTTHINGS_ENTRY_ID = "smartthings_entry_id"
CONF_DEVICE_ID = "device_id"

MAIN = "main"
CAP_WASHER_CYCLE = "samsungce.washerCycle"
ATTR_WASHER_CYCLE = "washerCycle"
ATTR_SUPPORTED_CYCLES = "supportedCycles"
COMMAND_SET_WASHER_CYCLE = "setWasherCycle"

CAP_WASHER_DELAY_END = "samsungce.washerDelayEnd"
ATTR_DELAY_REMAINING_TIME = "remainingTime"
ATTR_MINIMUM_RESERVABLE_TIME = "minimumReservableTime"
COMMAND_SET_DELAY_TIME = "setDelayTime"

CAP_SAMSUNG_WASHER_OPERATING_STATE = "samsungce.washerOperatingState"
COMMAND_START = "start"
COMMAND_CANCEL = "cancel"

CAP_SUPPORTED_OPTIONS = "custom.supportedOptions"
ATTR_REFERENCE_TABLE = "referenceTable"
CAP_REMOTE_CONTROL = "remoteControlStatus"
ATTR_REMOTE_CONTROL_ENABLED = "remoteControlEnabled"
CAP_WASHER_OPERATING_STATE = "washerOperatingState"
ATTR_MACHINE_STATE = "machineState"
ATTR_JOB_STATE = "washerJobState"
ATTR_COMPLETION_TIME = "completionTime"

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)

# Samsung cycle codes are table-specific. Unknown codes remain selectable and are
# shown as their raw Course_XX value rather than guessed.
CYCLE_NAMES: dict[str, dict[str, str]] = {
    "table_00": {
        "Course_5B": "Cotton",
        "Course_5C": "Synthetics",
        "Course_5D": "Daily Wash",
        "Course_5E": "Spin",
        "Course_5F": "Rinse-Spin",
        "Course_60": "Eco Drum Clean",
        "Course_61": "Air Refresh",
        "Course_63": "Drying",
        "Course_66": "15m Quick Wash",
        "Course_BA": "Drain-Spin",
        "Course_D0": "Cotton",
        "Course_D1": "eCotton",
        "Course_D2": "Synthetics",
        "Course_D3": "Delicates",
        "Course_D4": "Rinse-Spin",
        "Course_D5": "Eco Drum Clean",
        "Course_D6": "Bedding",
        "Course_D7": "Outdoor",
        "Course_D8": "Wool",
        "Course_D9": "Dark Garment",
        "Course_DA": "Super Eco Wash",
        "Course_DB": "Super Speed",
        "Course_DC": "15m Quick Wash",
    },
    "table_02": {
        "Course_02": "Powerbubble+",
        "Course_0F": "Clean Wash",
        "Course_10": "Spin for Dry",
        "Course_11": "Thin Bedding",
        "Course_14": "Undergarment",
        "Course_16": "Blouses",
        "Course_17": "Cloud",
        "Course_18": "Soft Bubble",
        "Course_19": "AI Optimal Wash",
        "Course_1A": "Shirts",
        "Course_1B": "Cotton",
        "Course_1C": "Eco 40-60",
        "Course_1D": "Super Speed",
        "Course_1E": "15m Quick Wash",
        "Course_1F": "Intense Cold",
        "Course_20": "Hygiene Steam",
        "Course_21": "Colours",
        "Course_22": "Wool",
        "Course_23": "Outdoor",
        "Course_24": "Bedding",
        "Course_25": "Synthetics",
        "Course_26": "Delicates",
        "Course_27": "Rinse+Spin",
        "Course_28": "Drain/Spin",
        "Course_29": "Drum Clean+",
        "Course_2A": "Denim",
        "Course_2B": "AI Wash",
        "Course_2C": "Stain Away",
        "Course_2D": "Silent Wash",
        "Course_2E": "Baby Care",
        "Course_2F": "Activewear",
        "Course_30": "Cloudy Day",
        "Course_31": "Sportswear",
        "Course_32": "Shirts",
        "Course_33": "Towels",
        "Course_34": "Daily Wash",
        "Course_35": "eCotton",
        "Course_36": "Wash+Dry",
        "Course_37": "Air Wash",
        "Course_38": "Cotton Dry",
        "Course_39": "Synthetics Dry",
        "Course_3A": "Drum Clean",
        "Course_3E": "Bubble Wash+",
        "Course_3F": "Deep Softener",
        "Course_50": "Heavy Duty+",
        "Course_52": "Eco Cold",
        "Course_53": "Heavy Duty",
        "Course_59": "Perm Press",
        "Course_5A": "Steam Sanitise",
        "Course_5B": "Small Load",
        "Course_5D": "Power Rinse",
        "Course_5F": "Spin Only",
        "Course_60": "Self Clean+",
        "Course_61": "Steam Cotton",
        "Course_62": "OptiWash",
        "Course_63": "Power Steam",
        "Course_64": "Steam Whites",
        "Course_66": "Denim",
        "Course_67": "Steam Allergen",
        "Course_68": "Steam Bulky",
        "Course_71": "Quick Wash",
        "Course_73": "Sanitise",
        "Course_7C": "Whites",
        "Course_7D": "Bedding/WaterProof",
        "Course_7E": "Self Clean",
        "Course_7F": "Wool/Delicates",
        "Course_80": "Water Saving",
        "Course_82": "Tub Clean",
        "Course_84": "Stain Wash",
        "Course_85": "Steam Normal",
        "Course_86": "Deep Wash",
        "Course_88": "Pet Care Wash",
        "Course_89": "Air Refresh",
        "Course_8C": "AI OptiWash",
        "Course_8D": "Steam Bedding",
        "Course_8E": "Super Eco Wash",
        "Course_8F": "Intense Cold",
        "Course_96": "Less Microfiber",
        "Course_A0": "Quick Wash 15m",
        "Course_A1": "Normal",
        "Course_A2": "AI Wash & Dry",
        "Course_A3": "Quick Wash+Dry",
        "Course_A4": "Less Microfiber",
        "Course_A6": "Pet Care",
        "Course_A7": "Product Care",
        "Course_A8": "Time Dry",
        "Course_A9": "Tide POD Cold",
        "Course_AA": "Air Fluff",
        "Course_AB": "Deep Clean",
        "Course_AC": "Air Sanitise",
        "Course_AD": "AI Opti Wash & Dry",
        "Course_AE": "Cool Air",
        "Course_AF": "Down Jacket Care",
        "Course_B2": "AI Wash & Dry +",
        "Course_B3": "Single Garment",
        "Course_B4": "Hand Wash",
        "Course_B5": "AI Wash+",
        "Course_B6": "AI OptiWash+",
        "Course_FB": "Care label cycle",
    },
    "table_03": {
        "Course_16": "Cotton",
        "Course_18": "Synthetics",
        "Course_19": "Delicates",
        "Course_1A": "Wool",
        "Course_1B": "Bedding",
        "Course_1C": "Shirts",
        "Course_1D": "Towels",
        "Course_1E": "Outdoor",
        "Course_20": "Iron Dry",
        "Course_23": "Quick Dry 35m",
        "Course_24": "Cool Air",
        "Course_25": "Warm Air",
        "Course_27": "Time Dry",
        "Course_29": "AI Dry",
        "Course_2B": "Self Tub Dry",
    },
}
