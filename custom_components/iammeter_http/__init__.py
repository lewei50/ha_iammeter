"""Iammeter integration."""
import asyncio
from datetime import timedelta
import logging

from iammeter_hacs.client import IamMeter
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator

from .const import DOMAIN, DEFAULT_TIMEOUT, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for iammeter."""
    coordinator = IammeterData(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class IammeterData(update_coordinator.DataUpdateCoordinator):
    """Get and update the latest data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data object."""
        super().__init__(
            hass, 
            _LOGGER, 
            name="Iammeter", 
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL)
        )

        host_entry = entry.data[CONF_IP_ADDRESS]

        # url = urlparse(host_entry, "http")
        # netloc = url.netloc or url.path
        # path = url.path if url.netloc else ""
        # url = ParseResult("http", netloc, path, *url[3:])
        self.unique_id = entry.entry_id
        self.name = entry.title
        self.host = host_entry
        self.port = entry.data[CONF_PORT]
        self.timeout = DEFAULT_TIMEOUT
        self._consecutive_errors = 0

    async def _async_update_data(self):
        """Update the data from the Iammeter device."""
        try:
            # 使用 asyncio.wait_for 添加超时限制
            data = await asyncio.wait_for(
                self.hass.async_add_executor_job(IamMeter, self.host, self.port),
                timeout=self.timeout
            )
            
            # Connection successful, reset error counter
            if self._consecutive_errors > 0:
                self.logger.info(
                    "Successfully reconnected to IAMMETER device %s:%s (Serial: %s)",
                    self.host,
                    self.port,
                    data.serial_number
                )
                self._consecutive_errors = 0
            
            self.logger.debug(
                "Successfully retrieved data from IAMMETER device (Serial: %s)",
                data.serial_number,
            )
            
            return data
            
        except asyncio.TimeoutError:
            self._consecutive_errors += 1
            # Only log errors on first failure and every 10th failure to avoid log spam
            if self._consecutive_errors == 1 or self._consecutive_errors % 10 == 0:
                self.logger.error(
                    "Connection timeout to IAMMETER device (%s:%s) - %d consecutive failures. "
                    "Please check if the device is online and network connection is normal.",
                    self.host,
                    self.port,
                    self._consecutive_errors
                )
            else:
                self.logger.debug(
                    "Connection timeout (%s:%s) - %d consecutive failures",
                    self.host,
                    self.port,
                    self._consecutive_errors
                )
            raise update_coordinator.UpdateFailed(
                f"Connection timeout: Device {self.host}:{self.port} did not respond within {self.timeout} seconds"
            )
            
        except (ConnectionError, OSError) as err:
            self._consecutive_errors += 1
            # Only log errors on first failure and every 10th failure
            if self._consecutive_errors == 1 or self._consecutive_errors % 10 == 0:
                self.logger.error(
                    "Cannot connect to IAMMETER device (%s:%s) - %d consecutive failures. "
                    "Error: %s. Please check device IP address and network connection.",
                    self.host,
                    self.port,
                    self._consecutive_errors,
                    str(err)
                )
            else:
                self.logger.debug(
                    "Connection failed (%s:%s) - %d consecutive failures: %s",
                    self.host,
                    self.port,
                    self._consecutive_errors,
                    str(err)
                )
            raise update_coordinator.UpdateFailed(
                f"Connection failed: Unable to connect to device {self.host}:{self.port}"
            )
            
        except (Timeout, HTTPError, RequestException) as err:
            self._consecutive_errors += 1
            # Only log errors on first failure and every 10th failure
            if self._consecutive_errors == 1 or self._consecutive_errors % 10 == 0:
                self.logger.error(
                    "Failed to retrieve data from IAMMETER device (%s:%s) - %d consecutive failures. "
                    "Error: %s",
                    self.host,
                    self.port,
                    self._consecutive_errors,
                    str(err)
                )
            else:
                self.logger.debug(
                    "Data retrieval failed (%s:%s) - %d consecutive failures: %s",
                    self.host,
                    self.port,
                    self._consecutive_errors,
                    str(err)
                )
            raise update_coordinator.UpdateFailed(str(err))
