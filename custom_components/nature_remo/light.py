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
    api = hass.data[DOMAIN]["api"]
    config = hass.data[DOMAIN]["config"]
    appliances = coordinator.data["appliances"]

    add_entities(
        [
            NatureRemoLight(coordinator, api, appliance, config)
            for appliance in appliances.values()
            if appliance["type"] == "LIGHT"
        ]
    )


class NatureRemoLight(NatureRemoBase, LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(self, coordinator, api, appliance, config):
        super().__init__(coordinator, appliance)

        # TODO Use the right python package instead
        self._api = api

        if appliance["state"]["power"] == "on":
            self._state = True
        elif appliance["state"]["power"] == "off":
            self._state = True
        else:
            self._state = None

        _LOGGER.error(appliance["state"])
        _LOGGER.error(config)

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
        return None
        # self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        # self._light.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        return None
        # self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        return None
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness