"""API client for Nature Remo."""
import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)

class NatureRemoApiClient:
    """API client for Nature Remo."""

    def __init__(self, access_token: str, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._access_token = access_token
        self._session = session

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make a request to the API."""
        url = f"{API_BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise Exception("Invalid access token")
                elif response.status == 429:
                    raise Exception("Rate limit exceeded")
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise err

    async def get_user_me(self) -> dict:
        """Get user info."""
        return await self._request("GET", "/1/users/me")

    async def get_devices(self) -> list:
        """Get all devices."""
        return await self._request("GET", "/1/devices")

    async def get_appliances(self) -> list:
        """Get all appliances."""
        return await self._request("GET", "/1/appliances")

    async def post_signal(self, signal_id: str) -> dict:
        """Send an IR signal."""
        return await self._request("POST", f"/1/signals/{signal_id}/send")

    async def post_tv_button(self, appliance_id: str, button: str) -> dict:
        """Send TV button command."""
        return await self._request("POST", f"/1/appliances/{appliance_id}/tv", data={"button": button})

    async def post_light_button(self, appliance_id: str, button: str) -> dict:
        """Send Light button command."""
        return await self._request("POST", f"/1/appliances/{appliance_id}/light", data={"button": button})

    async def post_ac_settings(self, appliance_id: str, settings: dict) -> dict:
        """Send AC settings."""
        return await self._request("POST", f"/1/appliances/{appliance_id}/aircon_settings", data=settings)
