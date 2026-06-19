"""Constants for the Basen Green BMS integration."""

import logging
from typing import Final

DOMAIN: Final = "basengreen"
LOGGER: Final[logging.Logger] = logging.getLogger(__package__)

LOW_RSSI: Final[int] = -75
UPDATE_INTERVAL: Final[int] = 30
MAX_CELLS: Final[int] = 16
MAX_TEMP_SENSORS: Final[int] = 8

CONF_KEEP_ALIVE: Final[str] = "keep_alive"
CONF_ADVANCED_OPTIONS: Final[str] = "advanced_options"

ATTR_CELL_VOLTAGES: Final[str] = "cell_voltages"
ATTR_TEMP_VALUES: Final[str] = "temp_values"
ATTR_CELL_COUNT: Final[str] = "cell_count"
ATTR_TEMP_SENSORS: Final[str] = "temp_sensors"
