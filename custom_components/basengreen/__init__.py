"""The Basen Green BMS integration."""

from dataclasses import dataclass
from types import ModuleType
from typing import Any, Final

from bleak.backends.device import BLEDevice

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.importlib import async_import_module

from .const import CONF_ADVANCED_OPTIONS, CONF_KEEP_ALIVE, DOMAIN, LOGGER
from .coordinator import BasenGreenCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

type BasenGreenConfigEntry = ConfigEntry[BasenGreenCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: BasenGreenConfigEntry) -> bool:
    """Set up Basen Green BMS from a config entry."""
    LOGGER.debug("Setup of %r", entry)

    if entry.unique_id is None:
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="missing_unique_id",
        )

    ble_device: BLEDevice | None = async_ble_device_from_address(
        hass, entry.unique_id, True
    )

    if ble_device is None:
        LOGGER.debug("Failed to discover device %s via Bluetooth", entry.unique_id)
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="device_not_found",
            translation_placeholders={"mac": entry.unique_id},
        )

    plugin: ModuleType = await async_import_module(hass, entry.data["type"])
    advanced_options: dict[str, Any] = entry.options.get(CONF_ADVANCED_OPTIONS, {})
    coordinator = BasenGreenCoordinator(
        hass,
        ble_device,
        plugin.BMS(
            ble_device,
            keep_alive=advanced_options.get(CONF_KEEP_ALIVE, True),
            secret=entry.options.get(CONF_PASSWORD, ""),
        ),
        entry,
    )

    started = False
    try:
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        started = True
    finally:
        if not started:
            await coordinator.async_shutdown()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BasenGreenConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: Final = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok and getattr(entry, "runtime_data", None) is not None:
        await entry.runtime_data.async_shutdown()
    return unload_ok
