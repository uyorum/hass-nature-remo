"""The Nature Remo integration."""

from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_ACCESS_TOKEN

from custom_components.nature_remo.api.nature_remo_api import NatureRemoAPI
from custom_components.nature_remo.common import (
    _LOGGER,
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
)


async def async_setup(
    hass,
    config,
):
    """Sets up the Nature Remo integration."""

    _LOGGER.debug("Setting up Nature Remo integration.")

    access_token = config[DOMAIN][CONF_ACCESS_TOKEN]
    session = async_get_clientsession(hass)
    api = NatureRemoAPI(access_token, session)

    coordinator = hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Nature Remo update",
        update_method=api.get,
        update_interval=DEFAULT_UPDATE_INTERVAL,
    )

    await coordinator.async_refresh()

    hass.data[DOMAIN] = {
        "api": api,
        "coordinator": coordinator,
        "config": config[DOMAIN],
    }

    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
    await discovery.async_load_platform(hass, "climate", DOMAIN, {}, config)
    await discovery.async_load_platform(hass, "light", DOMAIN, {}, config)

    return True
