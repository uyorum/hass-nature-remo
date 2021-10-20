"""The Nature Remo integration."""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.helpers import discovery, config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_ACCESS_TOKEN

_LOGGER = logging.getLogger(__name__)
DOMAIN = "nature_remo"

_API_URL = "https://api.nature.global/1/"

CONF_COOL_TEMP = "cool_temperature"
CONF_HEAT_TEMP = "heat_temperature"
DEFAULT_COOL_TEMP = 28
DEFAULT_HEAT_TEMP = 20
# TODO See if this is too low, English API says 30 requests/minute, JP says 30/5 minutes...
UPDATE_INTERVAL = timedelta(seconds=5)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ACCESS_TOKEN): cv.string,
                vol.Optional(CONF_COOL_TEMP, default=DEFAULT_COOL_TEMP): vol.Coerce(
                    int
                ),
                vol.Optional(CONF_HEAT_TEMP, default=DEFAULT_HEAT_TEMP): vol.Coerce(
                    int
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(
    hass,
    config,
):
    """Sets up the Nature Remo integration."""
    from custom_components.nature_remo.api.nature_remo_api import NatureRemoAPI

    _LOGGER.debug("Setting up Nature Remo integration.")

    # Creating integration-global objects
    api = NatureRemoAPI(
        config[DOMAIN][CONF_ACCESS_TOKEN],
        async_get_clientsession(hass),
    )

    # This is an object that will periodically refresh its values, allowing us to read sensors and appliances states
    coordinator = hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Nature Remo update",
        update_method=api.get_appliances_and_devices,
        update_interval=UPDATE_INTERVAL,
    )

    await coordinator.async_refresh()

    hass.data[DOMAIN] = {
        "api": api,
        "coordinator": coordinator,
        # TODO Check why we need to save config, it seems unnecessary to me and unsafe
        "config": config[DOMAIN],
    }

    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
    await discovery.async_load_platform(hass, "climate", DOMAIN, {}, config)
    await discovery.async_load_platform(hass, "light", DOMAIN, {}, config)

    return True
