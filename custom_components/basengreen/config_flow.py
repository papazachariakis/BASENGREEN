"""Config flow for Basen Green BMS integration."""

from dataclasses import dataclass
from typing import Any, Final

from aiobmsble.utils import bms_identify
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_ADDRESS, CONF_ID, CONF_MODEL, CONF_NAME
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import SelectOptionDict, SelectSelector, SelectSelectorConfig

from .const import DOMAIN, LOGGER

TIANPOWER_MODULE = "aiobmsble.bms.tianpwr_bms"


@dataclass
class DiscoveredDevice:
    """A discovered Basen Green Bluetooth device."""

    name: str
    discovery_info: BluetoothServiceInfoBleak

    def model(self) -> str:
        """Return BMS type label."""
        return "Tianpower BMS"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Basen Green BMS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._disc_dev: DiscoveredDevice | None = None
        self._disc_devs: dict[str, DiscoveredDevice] = {}

    async def _is_basengreen_device(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> bool:
        """Check if device is a Tianpower / Basen Green BMS."""
        name = discovery_info.name or ""
        if not name.startswith("TP_"):
            return False
        bms_class = await bms_identify(
            discovery_info.advertisement, discovery_info.address
        )
        if bms_class is None:
            return False
        module = str(bms_class.get_bms_module())
        LOGGER.debug(
            "Device %s (%s) detected as '%s'",
            discovery_info.name,
            format_mac(discovery_info.address),
            module,
        )
        return module == TIANPOWER_MODULE

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle flow initialized by Bluetooth discovery."""
        address: Final = discovery_info.address
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        if not await self._is_basengreen_device(discovery_info):
            return self.async_abort(reason="not_supported")

        self._disc_dev = DiscoveredDevice(discovery_info.name, discovery_info)
        self.context["title_placeholders"] = {
            CONF_NAME: self._disc_dev.name,
            CONF_ID: address[-9:],
            CONF_MODEL: self._disc_dev.model(),
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm bluetooth device discovery."""
        assert self._disc_dev is not None

        if user_input is not None:
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._disc_dev.name,
                data={"type": TIANPOWER_MODULE},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context.get("title_placeholders"),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual device selection."""
        if user_input is not None:
            address = str(user_input[CONF_ADDRESS])
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            self._disc_dev = self._disc_devs[address]
            return self.async_create_entry(
                title=self._disc_dev.name,
                data={"type": TIANPOWER_MODULE},
            )

        current_addresses: Final = self._async_current_ids(include_ignore=False)
        for discovery_info in list(
            async_discovered_service_info(self.hass, connectable=True)
        ):
            address = discovery_info.address
            if address in current_addresses or address in self._disc_devs:
                continue
            if not await self._is_basengreen_device(discovery_info):
                continue
            self._disc_devs[address] = DiscoveredDevice(
                discovery_info.name, discovery_info
            )

        if not self._disc_devs:
            return self.async_abort(reason="no_devices_found")

        devices: list[SelectOptionDict] = [
            SelectOptionDict(
                value=address,
                label=f"{dev.name} ({address}) - {dev.model()}",
            )
            for address, dev in self._disc_devs.items()
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): SelectSelector(
                        SelectSelectorConfig(options=devices),
                    )
                }
            ),
        )
