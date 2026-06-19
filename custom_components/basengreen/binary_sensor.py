"""Binary sensor platform for Basen Green BMS integration."""

from collections.abc import Callable
from dataclasses import dataclass

from aiobmsble import BMSSample

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BasenGreenConfigEntry
from .const import DOMAIN
from .coordinator import BasenGreenCoordinator

PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class BasenBinaryDescription(BinarySensorEntityDescription):
    """Describes a Basen Green BMS binary sensor."""

    is_on_fn: Callable[[BMSSample], bool | None]


BINARY_SENSOR_TYPES: list[BasenBinaryDescription] = [
    BasenBinaryDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=lambda d: (
            bool(d.get("battery_charging"))
            if "battery_charging" in d
            else ((c := d.get("current")) is not None and c > 0)
        ),
    ),
    BasenBinaryDescription(
        key="discharging",
        translation_key="discharging",
        is_on_fn=lambda d: ((c := d.get("current")) is not None and c < 0),
    ),
    BasenBinaryDescription(
        key="balancing",
        translation_key="balancing",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: bool(d.get("balancer")),
    ),
    BasenBinaryDescription(
        key="charge_mosfet",
        translation_key="charge_mosfet",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: bool(d.get("chrg_mosfet")),
    ),
    BasenBinaryDescription(
        key="discharge_mosfet",
        translation_key="discharge_mosfet",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: bool(d.get("dischrg_mosfet")),
    ),
    BasenBinaryDescription(
        key="problem",
        translation_key="problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: bool(d.get("problem")),
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: BasenGreenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Basen Green BMS binary sensors."""
    coordinator = config_entry.runtime_data
    mac = format_mac(config_entry.unique_id)
    async_add_entities(
        BasenGreenBinarySensor(coordinator, descr, mac) for descr in BINARY_SENSOR_TYPES
    )


class BasenGreenBinarySensor(
    CoordinatorEntity[BasenGreenCoordinator], BinarySensorEntity
):
    """Basen Green BMS binary sensor."""

    entity_description: BasenBinaryDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BasenGreenCoordinator,
        descr: BasenBinaryDescription,
        mac: str,
    ) -> None:
        """Initialize binary sensor."""
        self.entity_description = descr
        self._attr_unique_id = f"{DOMAIN}-{mac}-{descr.key}"
        self._attr_device_info = coordinator.device_info
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return binary sensor state."""
        if not self.coordinator.data:
            return None
        return self.entity_description.is_on_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return problem code if available."""
        if self.entity_description.key != "problem" or not self.coordinator.data:
            return None
        code = self.coordinator.data.get("problem_code")
        if code is None:
            return None
        return {"problem_code": hex(code)}
