"""Support for Nature Remo Light."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.light import LightEntity

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

    coordinator = hass.data[DOMAIN]["coordinator"]
    appliances = coordinator.data["appliances"]

    add_entities(
        [
            NatureRemoLight(appliance, hass.data[DOMAIN]["api"])
            for appliance in appliances.values()
            if appliance["type"] == "LIGHT"
        ]
    )


class NatureRemoLight(LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(self, appliance: dict, api: NatureRemoAPI):
        self._api = api

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
    def is_on(self) -> bool | None:
        """Returns True if light is on."""
        return self._is_on

    def update(self) -> None:
        """
        Updates the light status by reading the data in the update coordinator
        """
        ...
        # TODO Cache the response and make this common to all platforms of this integration
        # appliances = self._api.get_appliances()
        # appliance = next(a for a in appliances if a.id == self.unique_id)
        # self.save_state(appliance.light.state.power)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn on.
        """
        await self._api.post(f"/appliances/{self.unique_id}/light", {"button": "on"})
        self._is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Instructs the light to turn off.
        """
        await self._api.post(f"/appliances/{self.unique_id}/light", {"button": "off"})
        self._is_on = False

    # @property
    # TODO
    # def brightness(self):
    #     """Return the brightness of the light.
    #     This method is optional. Removing it indicates to Home Assistant
    #     that brightness is not supported for this light.
    #     """
    #     return self._brightness
