from custom_components.nature_remo.common import _API_URL, _LOGGER


class NatureRemoAPI:
    """Nature Remo API client"""

    def __init__(self, access_token, session):
        """Init API client"""
        self._access_token = access_token
        self._session = session

    # TODO Rename to get_appliances_and_devices and have proper type hinting
    #   SPLIT APPLIANCES (setup) AND DEVICES (sensors)
    async def get(self):
        """Get appliance and device list"""
        _LOGGER.debug("Fetching appliances and devices list from the Nature Remo API.")

        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = await self._session.get(f"{_API_URL}/appliances", headers=headers)
        appliances = {x["id"]: x for x in await response.json()}

        response = await self._session.get(f"{_API_URL}/devices", headers=headers)
        devices = {x["id"]: x for x in await response.json()}

        return {"appliances": appliances, "devices": devices}

    async def post(self, path, data):
        """Post any request"""
        _LOGGER.debug("Trying to request post:%s, data:%s", path, data)
        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = await self._session.post(
            f"{_API_URL}{path}", data=data, headers=headers
        )
        return await response.json()
