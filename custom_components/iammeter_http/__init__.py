"""IAMMETER HTTP integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IammeterApi, IammeterApiError
from .const import (
    DEFAULT_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .models import IammeterReading

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

type IammeterConfigEntry = ConfigEntry["IammeterData"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IammeterConfigEntry,
) -> bool:
    """Set up IAMMETER HTTP from a config entry."""
    coordinator = IammeterData(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IammeterConfigEntry,
) -> bool:
    """Unload an IAMMETER HTTP config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class IammeterData(DataUpdateCoordinator[IammeterReading]):
    """Coordinate IAMMETER local HTTP updates."""

    def __init__(self, hass: HomeAssistant, entry: IammeterConfigEntry) -> None:
        """Initialize the coordinator."""
        update_interval = entry.data.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_UPDATE_INTERVAL,
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.name = entry.title
        self.api = IammeterApi(
            async_get_clientsession(hass),
            entry.data[CONF_IP_ADDRESS],
            entry.data[CONF_PORT],
            DEFAULT_TIMEOUT,
        )

    async def _async_update_data(self) -> IammeterReading:
        """Fetch the latest IAMMETER data."""
        try:
            return await self.api.async_get_data()
        except IammeterApiError as err:
            raise UpdateFailed(str(err)) from err
