"""Support for Nature Remo Light."""
from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN, NatureRemoBase

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

    _LOGGER.error(coordinator.data["appliances"])

    add_entities(
        [
            NatureRemoLight(coordinator, api, appliance, config)
            for appliance in appliances.values()
            if appliance["type"] == "light"
        ]
    )


class NatureRemoLight(NatureRemoBase, LightEntity):
    """Implementation of a Nature Remo light"""

    def __init__(self, coordinator, api, appliance, config):
        super().__init__(coordinator, appliance)
        ...
