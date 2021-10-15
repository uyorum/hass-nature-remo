"""Support for Nature Remo Light."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import LightEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN, NatureRemoBase

import remo

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Nature Remo AC."""

    if discovery_info is None:
        return

    _LOGGER.debug("Setting up lights platform.")

    coordinator = hass.data[DOMAIN]["coordinator"]
    config = hass.data[DOMAIN]["config"]
    appliances = coordinator.data["appliances"]

    add_entities(
        [
            NatureRemoLight(coordinator, appliance, config)
            for appliance in appliances.values()
            if appliance["type"] == "LIGHT"
        ]
    )


class NatureRemoLight(NatureRemoBase, LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(self, coordinator, appliance, config):
        super().__init__(coordinator, appliance)

        self._api = remo.NatureRemoAPI(config["access_token"])

        power = appliance["light"]["state"]["power"]

        if power == "on":
            self._state = True
        elif power == "off":
            self._state = True
        else:
            self._state = None

    # @property
    # def brightness(self):
    #     """Return the brightness of the light.
    #     This method is optional. Removing it indicates to Home Assistant
    #     that brightness is not supported for this light.
    #     """
    #     return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._api.send_light_infrared_signal(self.unique_id, "on")
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._api.send_light_infrared_signal(self.unique_id, "off")
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        # TODO (Need to look into the API)
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
