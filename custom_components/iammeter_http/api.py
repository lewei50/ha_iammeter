"""Asynchronous client for the IAMMETER local HTTP API."""

from __future__ import annotations

import asyncio

import aiohttp
from yarl import URL

from .models import IammeterDataError, IammeterReading, parse_monitor_payload


class IammeterApiError(Exception):
    """Raised when local IAMMETER data cannot be retrieved."""


class IammeterApi:
    """Read IAMMETER data from the local monitor endpoint."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        timeout: int,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self.host = host
        self.port = port
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def configuration_url(self) -> str:
        """Return the device's local web interface URL."""
        return str(URL.build(scheme="http", host=self.host, port=self.port)).rstrip("/")

    @property
    def monitor_url(self) -> URL:
        """Return the compatibility monitor endpoint URL."""
        return URL.build(
            scheme="http",
            host=self.host,
            port=self.port,
            path="/monitorjson",
        )

    async def async_get_data(self) -> IammeterReading:
        """Retrieve and parse one local monitor response."""
        try:
            async with self._session.get(
                self.monitor_url,
                timeout=self._timeout,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise IammeterApiError(f"Unable to read {self.monitor_url}: {err}") from err

        try:
            return parse_monitor_payload(payload)
        except IammeterDataError as err:
            raise IammeterApiError(
                f"Invalid data from {self.monitor_url}: {err}"
            ) from err
