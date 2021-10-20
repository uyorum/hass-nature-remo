from typing import Dict
import aiohttp

from custom_components.nature_remo import _API_URL, _LOGGER


class NatureRemoAPI:
    """
    Nature Remo API client
    """

    def __init__(
        self,
        access_token: str,
        session: aiohttp.ClientSession,
    ):
        """
        Init API client
        """
        self._access_token = access_token
        self._session = session

    async def get_appliances_and_devices(self) -> Dict[str, Dict[str, Dict]]:
        """
        Gets new appliances and devices list and states from the API
            - Device = a Nature device, which holds sensor information
            - Appliance = a device controlled by IR through a Nature Remo device

        They are the only two GET endpoints in the API
        """
        _LOGGER.debug("Fetching appliances and devices list from the Nature Remo API.")

        headers = {"Authorization": f"Bearer {self._access_token}"}

        appliances_query = self._session.get(f"{_API_URL}/appliances", headers=headers)
        devices_query = self._session.get(f"{_API_URL}/devices", headers=headers)

        appliances_response = await appliances_query
        devices_response = await devices_query

        return {
            "appliances": {x["id"]: x for x in await appliances_response.json()},
            "devices": {x["id"]: x for x in await devices_response.json()},
        }

    async def post(
        self,
        path: str,
        data: dict,
    ) -> dict:
        """Emits a POST request to the API and returns it serialized."""
        _LOGGER.debug("Trying to request post:%s, data:%s", path, data)

        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = await self._session.post(
            f"{_API_URL}{path}", data=data, headers=headers
        )

        return await response.json()
