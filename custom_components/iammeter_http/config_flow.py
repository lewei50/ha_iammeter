"""Config flow for IAMMETER HTTP."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.ssdp import ATTR_UPNP_FRIENDLY_NAME

from .api import IammeterApi, IammeterApiError
from .const import (
    DEFAULT_IP,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)
from .models import IammeterReading

SCAN_INTERVAL_SCHEMA = vol.All(
    vol.Coerce(int),
    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
)


@callback
def iammeter_entries(hass: HomeAssistant) -> set[str]:
    """Return configured IAMMETER display names."""
    return {
        entry.data[CONF_NAME]
        for entry in hass.config_entries.async_entries(DOMAIN)
        if CONF_NAME in entry.data
    }


class IammeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an IAMMETER HTTP config flow."""

    VERSION = 1
    _discovered: dict[str, Any] | None = None
    _discovered_serial: str | None = None

    async def _async_read_device(
        self,
        host: str,
        port: int,
    ) -> IammeterReading:
        """Validate a device and return its current data."""
        api = IammeterApi(
            async_get_clientsession(self.hass),
            host,
            port,
            DEFAULT_TIMEOUT,
        )
        return await api.async_get_data()

    def _schema(self, values: dict[str, Any]) -> vol.Schema:
        """Build the user configuration schema."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=values.get(CONF_NAME, DEFAULT_NAME),
                ): str,
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=values.get(CONF_IP_ADDRESS, DEFAULT_IP),
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=values.get(CONF_PORT, DEFAULT_PORT),
                ): int,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=values.get(
                        CONF_SCAN_INTERVAL,
                        DEFAULT_UPDATE_INTERVAL,
                    ),
                ): SCAN_INTERVAL_SCHEMA,
            }
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a user-initiated setup."""
        errors: dict[str, str] = {}
        values = user_input or self._discovered or {}

        if user_input is not None:
            if user_input[CONF_NAME] in iammeter_entries(self.hass):
                errors[CONF_NAME] = "already_configured"
            else:
                try:
                    reading = await self._async_read_device(
                        user_input[CONF_IP_ADDRESS],
                        user_input[CONF_PORT],
                    )
                except IammeterApiError:
                    errors["base"] = "cannot_connect"
                else:
                    serial = reading.serial_number or self._discovered_serial
                    if serial:
                        await self.async_set_unique_id(serial)
                        self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(values),
            errors=errors,
        )

    async def async_step_ssdp(
        self,
        discovery_info: Any,
    ) -> config_entries.ConfigFlowResult:
        """Handle SSDP discovery."""
        friendly_name = discovery_info.upnp.get(ATTR_UPNP_FRIENDLY_NAME) or DEFAULT_NAME
        host = urlparse(discovery_info.ssdp_location).hostname
        if host is None:
            return self.async_abort(reason="cannot_connect")

        self._discovered_serial = friendly_name.rsplit("_", 1)[-1]
        await self.async_set_unique_id(self._discovered_serial, raise_on_progress=False)
        self._abort_if_unique_id_configured(updates={CONF_IP_ADDRESS: host})

        self._discovered = {
            CONF_NAME: friendly_name,
            CONF_IP_ADDRESS: host,
            CONF_PORT: DEFAULT_PORT,
            CONF_SCAN_INTERVAL: DEFAULT_UPDATE_INTERVAL,
        }
        self.context["title_placeholders"] = self._discovered
        return await self.async_step_user()

    async def async_step_import(
        self,
        user_input: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """Import a legacy configuration."""
        return await self.async_step_user(user_input)

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Update connection settings and the polling interval."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        current = {
            CONF_NAME: entry.data[CONF_NAME],
            CONF_IP_ADDRESS: entry.data[CONF_IP_ADDRESS],
            CONF_PORT: entry.data[CONF_PORT],
            CONF_SCAN_INTERVAL: entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_UPDATE_INTERVAL,
            ),
        }

        if user_input is not None:
            try:
                reading = await self._async_read_device(
                    user_input[CONF_IP_ADDRESS],
                    user_input[CONF_PORT],
                )
            except IammeterApiError:
                errors["base"] = "cannot_connect"
            else:
                if entry.unique_id and reading.serial_number:
                    await self.async_set_unique_id(reading.serial_number)
                    self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        values = current | (user_input or {})
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=values[CONF_IP_ADDRESS],
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=values[CONF_PORT],
                    ): int,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=values[CONF_SCAN_INTERVAL],
                    ): SCAN_INTERVAL_SCHEMA,
                }
            ),
            errors=errors,
        )
