"""Support for Nature Remo Light."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from . import DOMAIN, _LOGGER

from .api.nature_remo_api import NatureRemoAPI


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Sets up all light found in the Nature Remo API."""

    if discovery_info is None:
        return

    _LOGGER.debug("Setting up Nature Remo lights platform.")

    appliances_update_coordinator = hass.data[DOMAIN]["appliances_update_coordinator"]

    add_entities(
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
        if self.power == "on":
            return True
        elif self.power == "off":
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

    @property
    def appliance(self):
        return self.coordinator.data[self.unique_id]

    @property
    def power(self):
        return self.appliance["light"]["state"]["power"]

    @power.setter
    def power(self, value):
        # TODO Remove try/catch, here because in the test we don't have a coordinator (we should)
        try:
            self.appliance["light"]["state"]["power"] = value
        except AttributeError:
            pass

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn on.
        """
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "on"})

        # TODO Check if that is needed
        # Directly updating it in the coordinator for instant UI feedback
        self.power = "on"

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn off.
        """
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "off"})

        # Directly updating it in the coordinator for instant UI feedback
        self.power = "off"

        await self.coordinator.async_request_refresh()

    # @property
    # TODO
    # def brightness(self):
    #     """Return the brightness of the light.
    #     This method is optional. Removing it indicates to Home Assistant
    #     that brightness is not supported for this light.
    #     """
    #     return self._brightness
