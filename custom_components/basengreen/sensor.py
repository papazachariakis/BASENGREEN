"""Sensor platform for Basen Green BMS integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from aiobmsble import BMSSample

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BasenGreenConfigEntry
from .const import DOMAIN, MAX_CELLS, MAX_TEMP_SENSORS
from .coordinator import BasenGreenCoordinator

PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class BasenSensorDescription(SensorEntityDescription):
    """Describes a Basen Green BMS sensor entity."""

    value_fn: Callable[[BMSSample], float | int | None]


SENSOR_TYPES: Final[list[BasenSensorDescription]] = [
    BasenSensorDescription(
        key="state_of_charge",
        translation_key="state_of_charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("battery_level"),
    ),
    BasenSensorDescription(
        key="total_voltage",
        translation_key="total_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda d: d.get("voltage"),
    ),
    BasenSensorDescription(
        key="current",
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda d: d.get("current"),
    ),
    BasenSensorDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: d.get("power"),
    ),
    BasenSensorDescription(
        key="state_of_health",
        translation_key="state_of_health",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("battery_health"),
    ),
    BasenSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda d: d.get("temperature"),
    ),
    BasenSensorDescription(
        key="design_capacity",
        translation_key="design_capacity",
        native_unit_of_measurement="Ah",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda d: d.get("design_capacity"),
    ),
    BasenSensorDescription(
        key="capacity_remaining",
        translation_key="capacity_remaining",
        native_unit_of_measurement="Ah",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda d: d.get("cycle_charge"),
    ),
    BasenSensorDescription(
        key="charge_cycles",
        translation_key="charge_cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.get("cycles"),
    ),
    BasenSensorDescription(
        key="stored_energy",
        translation_key="stored_energy",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: d.get("cycle_capacity"),
    ),
    BasenSensorDescription(
        key="delta_cell_voltage",
        translation_key="delta_cell_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("delta_voltage"),
    ),
    BasenSensorDescription(
        key="min_cell_voltage",
        translation_key="min_cell_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            min(cells) if (cells := d.get("cell_voltages", [])) else None
        ),
    ),
    BasenSensorDescription(
        key="max_cell_voltage",
        translation_key="max_cell_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            max(cells) if (cells := d.get("cell_voltages", [])) else None
        ),
    ),
    BasenSensorDescription(
        key="cell_count",
        translation_key="cell_count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("cell_count"),
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: BasenGreenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Basen Green BMS sensors."""
    coordinator = config_entry.runtime_data
    mac = format_mac(config_entry.unique_id)
    entities: list[SensorEntity] = []

    for descr in SENSOR_TYPES:
        entities.append(BasenGreenSensor(coordinator, descr, mac))

    for cell_idx in range(MAX_CELLS):
        entities.append(CellVoltageSensor(coordinator, mac, cell_idx))

    for temp_idx in range(MAX_TEMP_SENSORS):
        entities.append(TemperatureSensor(coordinator, mac, temp_idx))

    entities.append(RSSISensor(coordinator, mac))
    entities.append(LinkQualitySensor(coordinator, mac))

    async_add_entities(entities)


class BasenGreenSensor(CoordinatorEntity[BasenGreenCoordinator], SensorEntity):
    """Generic Basen Green BMS sensor."""

    entity_description: BasenSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BasenGreenCoordinator,
        descr: BasenSensorDescription,
        mac: str,
    ) -> None:
        """Initialize sensor."""
        self.entity_description = descr
        self._attr_unique_id = f"{DOMAIN}-{mac}-{descr.key}"
        self._attr_device_info = coordinator.device_info
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | int | None:
        """Return sensor value."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


class CellVoltageSensor(CoordinatorEntity[BasenGreenCoordinator], SensorEntity):
    """Individual cell voltage sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 3

    def __init__(
        self,
        coordinator: BasenGreenCoordinator,
        mac: str,
        cell_index: int,
    ) -> None:
        """Initialize cell voltage sensor (0-based index)."""
        self._cell_index = cell_index
        cell_num = cell_index + 1
        self._attr_translation_key = "cell_voltage"
        self._attr_translation_placeholders = {"cell": str(cell_num)}
        self._attr_unique_id = f"{DOMAIN}-{mac}-cell_voltage_{cell_num}"
        self._attr_device_info = coordinator.device_info
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return cell voltage."""
        if not self.coordinator.data:
            return None
        cells = self.coordinator.data.get("cell_voltages", [])
        if self._cell_index >= len(cells):
            return None
        return cells[self._cell_index]


class TemperatureSensor(CoordinatorEntity[BasenGreenCoordinator], SensorEntity):
    """Individual temperature probe sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: BasenGreenCoordinator,
        mac: str,
        temp_index: int,
    ) -> None:
        """Initialize temperature sensor (0-based index)."""
        self._temp_index = temp_index
        probe_num = temp_index + 1
        self._attr_translation_key = "temperature_probe"
        self._attr_translation_placeholders = {"probe": str(probe_num)}
        self._attr_unique_id = f"{DOMAIN}-{mac}-temperature_{probe_num}"
        self._attr_device_info = coordinator.device_info
        super().__init__(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return probe temperature."""
        if not self.coordinator.data:
            return None
        temps = self.coordinator.data.get("temp_values", [])
        if self._temp_index >= len(temps):
            return None
        return temps[self._temp_index]


class RSSISensor(SensorEntity):
    """Bluetooth RSSI diagnostic sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "rssi"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: BasenGreenCoordinator, mac: str) -> None:
        """Initialize RSSI sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}-{mac}-rssi"
        self._attr_device_info = coordinator.device_info

    async def async_update(self) -> None:
        """Update RSSI."""
        rssi = self._coordinator.rssi
        self._attr_native_value = rssi
        self._attr_available = rssi is not None


class LinkQualitySensor(SensorEntity):
    """BMS link quality diagnostic sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "link_quality"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: BasenGreenCoordinator, mac: str) -> None:
        """Initialize link quality sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}-{mac}-link_quality"
        self._attr_device_info = coordinator.device_info

    async def async_update(self) -> None:
        """Update link quality."""
        self._attr_native_value = self._coordinator.link_quality
        self._attr_available = True
