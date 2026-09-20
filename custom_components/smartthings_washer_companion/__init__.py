"""SmartThings Washer Companion integration."""

from __future__ import annotations

from datetime import datetime

import voluptuous as vol

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, service
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CYCLE,
    ATTR_FINISH_AT,
    DOMAIN,
    PLATFORMS,
    SERVICE_SCHEDULE_WASH,
)
from .coordinator import WasherCycleCoordinator

type WasherCompanionConfigEntry = ConfigEntry[WasherCycleCoordinator]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register integration-wide entity services."""

    async def async_schedule_wash_service(entity, call: ServiceCall) -> None:
        finish_at = _parse_finish_at(hass, call.data[ATTR_FINISH_AT])
        await entity.async_schedule_wash(call.data[ATTR_CYCLE], finish_at)

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_SCHEDULE_WASH,
        entity_domain=SELECT_DOMAIN,
        schema={
            vol.Required(ATTR_CYCLE): cv.string,
            vol.Required(ATTR_FINISH_AT): cv.string,
        },
        func=async_schedule_wash_service,
    )
    return True


def _parse_finish_at(hass: HomeAssistant, value: str) -> datetime:
    """Parse an ISO timestamp and apply Home Assistant's timezone if omitted."""
    finish_at = dt_util.parse_datetime(value)
    if finish_at is None:
        raise ServiceValidationError("finish_at must be a valid ISO date and time")
    if finish_at.tzinfo is None:
        timezone = dt_util.get_time_zone(hass.config.time_zone)
        if timezone is None:
            raise ServiceValidationError("Home Assistant's timezone is invalid")
        finish_at = finish_at.replace(tzinfo=timezone)
    return finish_at


async def async_setup_entry(
    hass: HomeAssistant, entry: WasherCompanionConfigEntry
) -> bool:
    """Set up SmartThings Washer Companion."""
    coordinator = WasherCycleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: WasherCompanionConfigEntry
) -> bool:
    """Unload SmartThings Washer Companion."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
