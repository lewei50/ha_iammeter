"""Config flow for iammeter integration."""
import logging
from urllib.parse import urlparse

from iammeter_hacs.client import IamMeter
from requests.exceptions import HTTPError, Timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import ssdp
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import slugify

from .const import DEFAULT_IP, DEFAULT_NAME, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


@callback
def iammeter_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return {
        entry.data[CONF_NAME]
        for entry in hass.config_entries.async_entries(DOMAIN)
    }


class IammeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iammeter."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors: dict = {}

    def _host_in_configuration_exists(self, name) -> bool:
        """Return True if host exists in configuration."""
        if name in iammeter_entries(self.hass):
            return True
        return False

    async def _test_connection(self, host, port):
        """Check if we can connect to the Iammeter device."""
        try:
            await self.hass.async_add_executor_job(IamMeter, host, port)
            return True
        except (OSError, HTTPError, Timeout):
            self._errors[CONF_IP_ADDRESS] = "cannot_connect"
            _LOGGER.error(
                "Could not connect to Iammeter device at %s, check host ip address",
                host,
            )
        return False

    async def async_step_user(self, user_input=None):
        """Step when user initializes a integration."""
        self._errors = {}
        if user_input is not None:
            # set some defaults in case we need to return to the form
            name = slugify(user_input.get(CONF_NAME, DEFAULT_NAME))
            host = user_input.get(CONF_IP_ADDRESS, DEFAULT_IP)
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            if self._host_in_configuration_exists(name):
                self._errors[CONF_NAME] = "already_configured"
            else:
                if await self._test_connection(host, port):
                    return self.async_create_entry(
                        title=name,
                        data={CONF_NAME:name, CONF_IP_ADDRESS: host, CONF_PORT: port},
                    )
        else:
            user_input = {}
            user_input[CONF_NAME] = DEFAULT_NAME
            user_input[CONF_IP_ADDRESS] = DEFAULT_IP
            user_input[CONF_PORT] = DEFAULT_PORT
            if hasattr(self, 'discovered_conf'):
                user_input[CONF_NAME] = self.discovered_conf[CONF_NAME]
                user_input[CONF_IP_ADDRESS] = self.discovered_conf[CONF_IP_ADDRESS]
                user_input[CONF_PORT] = DEFAULT_PORT

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_NAME)
                    ): str,
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=user_input.get(CONF_IP_ADDRESS, DEFAULT_IP),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=user_input.get(CONF_PORT, DEFAULT_PORT),
                    ): int,
                }
            ),
            errors=self._errors,
        )

    async def async_step_ssdp(self, discovery_info):
        """Handle a discovered Heos device."""
        friendly_name = discovery_info.upnp[ssdp.ATTR_UPNP_FRIENDLY_NAME]
        host = urlparse(discovery_info.ssdp_location).hostname
        port = DEFAULT_PORT
        dev_sn = friendly_name[-8:]
        self.host = host
        self.discovered_conf = {
            CONF_NAME: friendly_name,
            CONF_IP_ADDRESS: host,
            CONF_PORT: port,
        }
        # pylint: disable=no-member # https://github.com/PyCQA/pylint/issues/3167
        self.context["title_placeholders"] = self.discovered_conf
        if self._host_in_configuration_exists(friendly_name):
            return self.async_abort(reason="already_configured")

        # unique_id should be serial for services purpose
        await self.async_set_unique_id(dev_sn, raise_on_progress=False)

        # Check if already configured
        self._abort_if_unique_id_configured()
        return await self.async_step_user()

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        name = user_input.get(CONF_NAME, DEFAULT_NAME)

        if self._host_in_configuration_exists(name):
            return self.async_abort(reason="already_configured")
        return await self.async_step_user(user_input)
