"""Support for Nature Remo Light."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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


class NatureRemoLight(LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(
        self,
        appliance: dict,
        api: NatureRemoAPI,
        update_coordinator: DataUpdateCoordinator = None,
    ):
        self.api = api
        self.update_coordinator = update_coordinator

        self._name = appliance["nickname"]
        self._appliance_id = appliance["id"]

        # Defining the value in the init for linter warnings
        self._is_on = None

        power = appliance["light"]["state"]["power"]
        self.save_state(power)

    def save_state(self, power):
        if power == "on":
            self._is_on = True
        elif power == "off":
            self._is_on = False
        else:
            self._is_on = None

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
        return self.update_coordinator.data[self.unique_id]

    @property
    def power(self):
        return self.appliance["light"]["state"]["power"]

    @power.setter
    def power(self, value):
        # TODO Remove try/catch, here because test don't have a coordinator
        try:
            self.appliance["light"]["state"]["power"] = value
        except AttributeError:
            pass

    @property
    def is_on(self) -> bool | None:
        """Returns True if light is on."""
        return self._is_on

    def update(self) -> None:
        """
        Updates the light status by reading the data in the update coordinator
        """
        self.save_state(self.power)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn on.
        """
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "on"})

        # Directly updating it in the coordinator for instant UI feedback
        self.power = "on"

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn off.
        """
        await self.api.post(f"/appliances/{self.unique_id}/light", {"button": "off"})

        # Directly updating it in the coordinator for instant UI feedback
        self.power = "off"

    # @property
    # TODO
    # def brightness(self):
    #     """Return the brightness of the light.
    #     This method is optional. Removing it indicates to Home Assistant
    #     that brightness is not supported for this light.
    #     """
    #     return self._brightness
