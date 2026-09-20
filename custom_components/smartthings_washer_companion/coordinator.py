"""Coordinator for SmartThings Washer Companion."""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Any

from pysmartthings import Capability, Command

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_COMPLETION_TIME,
    ATTR_DELAY_REMAINING_TIME,
    ATTR_JOB_STATE,
    ATTR_MACHINE_STATE,
    ATTR_MINIMUM_RESERVABLE_TIME,
    ATTR_REFERENCE_TABLE,
    ATTR_REMOTE_CONTROL_ENABLED,
    ATTR_SUPPORTED_CYCLES,
    ATTR_WASHER_CYCLE,
    CAP_REMOTE_CONTROL,
    CAP_SAMSUNG_WASHER_OPERATING_STATE,
    CAP_SUPPORTED_OPTIONS,
    CAP_WASHER_CYCLE,
    CAP_WASHER_DELAY_END,
    CAP_WASHER_OPERATING_STATE,
    COMMAND_SET_DELAY_TIME,
    COMMAND_SET_WASHER_CYCLE,
    COMMAND_START,
    CONF_DEVICE_ID,
    CONF_SMARTTHINGS_ENTRY_ID,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAIN,
)
from .logic import (
    WasherCycleData,
    attribute_value,
    build_labels,
    cycle_label,
    delay_minutes_for_finish,
    extract_supported_cycles,
    infer_table_id,
    integer_value,
    is_enabled,
    mapping_get,
    normalise_cycle_code,
    normalise_table_id,
)

LOGGER = logging.getLogger(__name__)


class WasherCycleCoordinator(DataUpdateCoordinator[WasherCycleData]):
    """Read and control washer cycles through the official OAuth client."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
            always_update=False,
        )
        self.device_id: str = entry.data[CONF_DEVICE_ID]
        self.smartthings_entry_id: str = entry.data[CONF_SMARTTHINGS_ENTRY_ID]

    def _smartthings_entry(self) -> ConfigEntry:
        entry = self.hass.config_entries.async_get_entry(self.smartthings_entry_id)
        if entry is None or entry.state is not ConfigEntryState.LOADED:
            raise ConfigEntryNotReady("The official SmartThings integration is not loaded")
        if getattr(entry, "runtime_data", None) is None:
            raise ConfigEntryNotReady("SmartThings runtime data is unavailable")
        return entry

    def _client(self) -> Any:
        return self._smartthings_entry().runtime_data.client

    async def _async_update_data(self) -> WasherCycleData:
        try:
            status = await self._client().get_device_status(self.device_id)
            main = mapping_get(status, MAIN)
            if main is None:
                raise UpdateFailed("SmartThings returned no main component")

            cycle_cap = mapping_get(main, CAP_WASHER_CYCLE)
            if cycle_cap is None:
                raise UpdateFailed("The washer does not expose samsungce.washerCycle")

            current_code = normalise_cycle_code(
                attribute_value(cycle_cap, ATTR_WASHER_CYCLE)
            )
            codes = extract_supported_cycles(
                attribute_value(cycle_cap, ATTR_SUPPORTED_CYCLES)
            )
            if not codes:
                raise UpdateFailed("The washer returned no supported cycles")

            # Newer Samsung profiles expose referenceTable on washerCycle;
            # older profiles expose it through custom.supportedOptions.
            table_id = normalise_table_id(
                attribute_value(cycle_cap, ATTR_REFERENCE_TABLE)
            )
            if not table_id:
                supported_cap = mapping_get(main, CAP_SUPPORTED_OPTIONS)
                table_id = normalise_table_id(
                    attribute_value(supported_cap, ATTR_REFERENCE_TABLE)
                )
            if not table_id:
                table_id = infer_table_id(codes)
            labels, code_by_label = build_labels(codes, table_id)
            current_label = None
            if current_code in codes:
                current_label = cycle_label(current_code, table_id)
            if current_code and current_label in {
                label.rsplit(" (Course_", 1)[0] for label in labels
            }:
                current_label = next(
                    (label for label, code in code_by_label.items() if code == current_code),
                    current_label,
                )

            remote_cap = mapping_get(main, CAP_REMOTE_CONTROL)
            operating_cap = mapping_get(main, CAP_WASHER_OPERATING_STATE)
            delay_cap = mapping_get(main, CAP_WASHER_DELAY_END)
            samsung_operating_cap = mapping_get(
                main, CAP_SAMSUNG_WASHER_OPERATING_STATE
            )
            return WasherCycleData(
                current_code=current_code,
                current_label=current_label,
                labels=labels,
                code_by_label=code_by_label,
                table_id=table_id,
                remote_control_enabled=is_enabled(
                    attribute_value(remote_cap, ATTR_REMOTE_CONTROL_ENABLED)
                ),
                machine_state=attribute_value(operating_cap, ATTR_MACHINE_STATE),
                job_state=attribute_value(operating_cap, ATTR_JOB_STATE),
                completion_time=attribute_value(
                    operating_cap, ATTR_COMPLETION_TIME
                ),
                delay_supported=(
                    delay_cap is not None and samsung_operating_cap is not None
                ),
                delay_remaining_minutes=integer_value(
                    attribute_value(delay_cap, ATTR_DELAY_REMAINING_TIME)
                ),
                minimum_reservable_minutes=integer_value(
                    attribute_value(delay_cap, ATTR_MINIMUM_RESERVABLE_TIME)
                ),
            )
        except (ConfigEntryNotReady, UpdateFailed):
            raise
        except Exception as err:
            raise UpdateFailed("Unable to read washer cycles") from err

    async def async_select_cycle(self, label: str) -> None:
        """Select a cycle after enforcing washer readiness."""
        await self.async_refresh()
        if not self.last_update_success:
            raise HomeAssistantError("Could not verify the washer's current state")
        if not self.data:
            raise HomeAssistantError("Washer cycle data is unavailable")
        if not self.data.remote_control_enabled:
            raise HomeAssistantError(
                "Enable Smart Control on the washer before selecting a cycle"
            )
        if self.data.machine_state != "stop":
            raise HomeAssistantError("A cycle can only be changed while the washer is stopped")
        try:
            code = self.data.code_by_label[label]
        except KeyError as err:
            raise HomeAssistantError(f"Unsupported washer cycle: {label}") from err

        try:
            await self._client().execute_device_command(
                self.device_id,
                Capability(CAP_WASHER_CYCLE),
                Command(COMMAND_SET_WASHER_CYCLE),
                MAIN,
                argument=code,
            )
        except Exception as err:
            raise HomeAssistantError("SmartThings rejected the cycle change") from err
        await self.async_request_refresh()

    def _validate_ready(self) -> WasherCycleData:
        """Return fresh data when the washer is safe to configure."""
        if not self.last_update_success or not self.data:
            raise HomeAssistantError("Could not verify the washer's current state")
        if not self.data.remote_control_enabled:
            raise HomeAssistantError(
                "Enable Smart Control on the washer before scheduling a wash"
            )
        if self.data.machine_state != "stop":
            raise HomeAssistantError("The washer must be stopped before scheduling")
        return self.data

    async def async_schedule_wash(self, label: str, finish_at: datetime) -> int:
        """Select a cycle, set Samsung Delay End, and start the schedule."""
        await self.async_refresh()
        data = self._validate_ready()
        if not data.delay_supported:
            raise HomeAssistantError(
                "This washer does not expose Samsung Delay End through SmartThings"
            )

        requested_label = next(
            (option for option in data.labels if option.casefold() == label.casefold()),
            None,
        )
        if requested_label is None:
            raise HomeAssistantError(f"Unsupported washer cycle: {label}")

        if data.current_label != requested_label:
            await self.async_select_cycle(requested_label)
            for _ in range(5):
                await asyncio.sleep(1)
                await self.async_refresh()
                data = self._validate_ready()
                if data.current_label == requested_label:
                    break
            else:
                raise HomeAssistantError(
                    "SmartThings did not confirm the requested washer cycle"
                )

        finish_at_utc = dt_util.as_utc(finish_at)
        try:
            delay_minutes = delay_minutes_for_finish(dt_util.utcnow(), finish_at_utc)
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        minimum_minutes = max(data.minimum_reservable_minutes or 0, 5)
        if delay_minutes < minimum_minutes:
            raise HomeAssistantError(
                "The requested finish time is too soon for this washer"
            )
        if delay_minutes > 1440:
            raise HomeAssistantError(
                "Samsung Delay End only supports finish times within 24 hours"
            )

        try:
            await self._client().execute_device_command(
                self.device_id,
                Capability(CAP_WASHER_DELAY_END),
                Command(COMMAND_SET_DELAY_TIME),
                MAIN,
                argument=delay_minutes,
            )
        except Exception as err:
            raise HomeAssistantError(
                "SmartThings rejected the Delay End setting"
            ) from err

        for _ in range(10):
            await asyncio.sleep(1)
            await self.async_refresh()
            data = self._validate_ready()
            if (
                data.delay_remaining_minutes is not None
                and abs(data.delay_remaining_minutes - delay_minutes) <= 5
            ):
                break
        else:
            raise HomeAssistantError(
                "SmartThings did not confirm the requested Delay End time"
            )

        try:
            await self._client().execute_device_command(
                self.device_id,
                Capability(CAP_SAMSUNG_WASHER_OPERATING_STATE),
                Command(COMMAND_START),
                MAIN,
            )
        except Exception as err:
            raise HomeAssistantError(
                "Delay End was set, but SmartThings rejected the start command"
            ) from err
        await self.async_request_refresh()
        return delay_minutes
