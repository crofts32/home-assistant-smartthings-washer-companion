"""Cycle selector for SmartThings Washer Companion."""

from __future__ import annotations

from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WasherCompanionConfigEntry
from .const import CONF_DEVICE_ID
from .coordinator import WasherCycleCoordinator


async def async_setup_entry(
    hass,
    entry: WasherCompanionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the washer cycle selector."""
    async_add_entities([WasherCycleSelect(entry.runtime_data, entry)])


class WasherCycleSelect(CoordinatorEntity[WasherCycleCoordinator], SelectEntity):
    """Select the programme used by the washer's next run command."""

    _attr_has_entity_name = True
    _attr_name = "Cycle"
    _attr_icon = "mdi:washing-machine"

    def __init__(self, coordinator: WasherCycleCoordinator, entry) -> None:
        super().__init__(coordinator)
        device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}_washer_cycle"
        self._attr_device_info = DeviceInfo(identifiers={("smartthings", device_id)})

    @property
    @override
    def options(self) -> list[str]:
        return self.coordinator.data.labels

    @property
    @override
    def current_option(self) -> str | None:
        return self.coordinator.data.current_label

    @override
    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_select_cycle(option)
