"""Config flow for SmartThings Washer Companion."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_NAME

from .const import (
    CAP_WASHER_CYCLE,
    CONF_DEVICE_ID,
    CONF_SMARTTHINGS_ENTRY_ID,
    DOMAIN,
    MAIN,
)
from .logic import mapping_get


class SmartThingsWasherCompanionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a washer backed by the official SmartThings integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select a washer from a loaded SmartThings account."""
        washers: dict[str, tuple[str, str]] = {}
        for entry in self.hass.config_entries.async_entries("smartthings"):
            runtime = getattr(entry, "runtime_data", None)
            if runtime is None:
                continue
            for device_id, full_device in runtime.devices.items():
                main = mapping_get(full_device.status, MAIN)
                if mapping_get(main, CAP_WASHER_CYCLE) is None:
                    continue
                label = full_device.device.label or full_device.device.name or device_id
                washers[device_id] = (label, entry.entry_id)

        if not washers:
            return self.async_abort(reason="no_supported_washers")

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            label, smartthings_entry_id = washers[device_id]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=label,
                data={
                    CONF_DEVICE_ID: device_id,
                    CONF_SMARTTHINGS_ENTRY_ID: smartthings_entry_id,
                    CONF_NAME: label,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): vol.In(
                        {device_id: value[0] for device_id, value in washers.items()}
                    )
                }
            ),
        )
