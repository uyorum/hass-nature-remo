"""Support for Nature Remo Light."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import DOMAIN, _LOGGER

from .api.nature_remo_api import NatureRemoAPI


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Sets up all light found in the Nature Remo API."""

    if discovery_info is None:
        # TODO What even is that
        return

    _LOGGER.debug("Setting up Nature Remo lights platform.")

    appliances_update_coordinator = hass.data[DOMAIN]["appliances_update_coordinator"]

    async_add_entities(
        [
            NatureRemoLight(
                appliance,
                hass.data[DOMAIN]["api"],
                appliances_update_coordinator,
            )
            for appliance in appliances_update_coordinator.data.values()
            if appliance["type"] == "LIGHT"
        ]
    )


class NatureRemoLight(CoordinatorEntity, LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(
        self,
        appliance: dict,
        api: NatureRemoAPI,
        appliances_update_coordinator: DataUpdateCoordinator = None,
    ):
        # This will call the CoordinatorEntity constructor
        super().__init__(appliances_update_coordinator)

        self.api = api

        self._name = appliance["nickname"]
        self._appliance_id = appliance["id"]

    @property
    def is_on(self) -> bool | None:
        """Returns True if light is on."""
        power = self.coordinator.data[self.unique_id]["light"]["state"]["power"]

        if power == "on":
            return True
        elif power == "off":
            return False
        else:
            return None

    @property
    def name(self):
        """Returns the name of the light."""
        return self._name

    @property
    def unique_id(self):
        """Returns a unique ID."""
        return self._appliance_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn on.
        """
        # TODO Take that code out and in the API
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "on"})

        # TODO Check if that is needed
        #   Also see if we can directly update the value without a query?
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn off.
        """
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "off"})

        await self.coordinator.async_request_refresh()

    # @property
    # TODO
    # def brightness(self):
    #     """Return the brightness of the light.
    #     This method is optional. Removing it indicates to Home Assistant
    #     that brightness is not supported for this light.
    #     """
    #     return self._brightness
