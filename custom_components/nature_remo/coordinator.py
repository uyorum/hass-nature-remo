"""DataUpdateCoordinator for Nature Remo."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NatureRemoApiClient
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class NatureRemoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Nature Remo data."""

    def __init__(self, hass: HomeAssistant, api: NatureRemoApiClient) -> None:
        """Initialize local coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from Nature Remo api."""
        try:
            # We fetch devices and appliances concurrently.
            # - devices contain sensor values (temperature, humidity, etc.) and remote hub info.
            # - appliances contain registered appliances (AC, TV, Light, and Smart Meter for Remo E)
            devices, appliances = await asyncio.gather(
                self.api.get_devices(),
                self.api.get_appliances(),
            )
            return {
                "devices": devices,
                "appliances": appliances,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
