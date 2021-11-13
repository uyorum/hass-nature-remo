"""Support for Nature Remo E energy sensor."""
from homeassistant.components.sensor import SensorEntity

from . import DOMAIN, _LOGGER
from homeassistant.const import (
    POWER_WATT,
    DEVICE_CLASS_POWER,
)
from .common import NatureRemoBase


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Nature Remo E sensor."""
    if discovery_info is None:
        return
    _LOGGER.debug("Setting up Nature Remo E sensor platform.")
    appliances_update_coordinator = hass.data[DOMAIN]["appliances_update_coordinator"]

    async_add_entities(
        [
            NatureRemoESensor(appliances_update_coordinator, appliance)
            for appliance in appliances_update_coordinator.data.values()
            if appliance["type"] == "EL_SMART_METER"
        ]
    )


class NatureRemoESensor(NatureRemoBase, SensorEntity):
    """Implementation of a Nature Remo E sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(appliance)
        self._coordinator = coordinator
        self._unit_of_measurement = POWER_WATT

    @property
    def state(self):
        """Return the state of the sensor."""
        appliance = self._coordinator.data[self._appliance_id]
        echonetlite_properties = appliance["smart_meter"]["echonetlite_properties"]
        measured_instantaneous = next(
            # measured_instantaneous
            # it is recommended to identify by epc.
            value["val"]
            for value in echonetlite_properties
            if value["epc"] == 231
        )
        return measured_instantaneous

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_POWER

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self._coordinator.async_request_refresh()
