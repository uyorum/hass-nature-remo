import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity


_LOGGER = logging.getLogger(__name__)
_API_URL = "https://api.nature.global/1/"
DOMAIN = "nature_remo"

CONF_COOL_TEMP = "cool_temperature"
CONF_HEAT_TEMP = "heat_temperature"
DEFAULT_COOL_TEMP = 28
DEFAULT_HEAT_TEMP = 20
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=60)
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


class NatureRemoBase(Entity):
    """Nature Remo entity base class."""

    def __init__(self, coordinator, appliance):
        self._coordinator = coordinator
        self._name = f"Nature Remo {appliance['nickname']}"
        self._appliance_id = appliance["id"]
        self._device = appliance["device"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._appliance_id

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def device_info(self):
        """Return the device info for the sensor."""
        # TODO Since device registration requires Config Entries, this doesn't work for now
        return {
            "identifiers": {(DOMAIN, self._device["id"])},
            "name": self._device["name"],
            "manufacturer": "Nature Remo",
            "model": self._device["serial_number"],
            "sw_version": self._device["firmware_version"],
        }
