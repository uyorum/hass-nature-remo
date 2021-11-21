"""Support for Nature Remo E energy sensor."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import DOMAIN, _LOGGER
from homeassistant.const import (
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_ENERGY,
    POWER_WATT,
    ENERGY_KILO_WATT_HOUR,
)
from .common import NatureRemoBase


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Nature Remo E sensor."""

    if discovery_info is None:
        return
    _LOGGER.debug("Setting up Nature Remo E sensor platform.")
    appliances_update_coordinator = hass.data[DOMAIN]["appliances_update_coordinator"]

    sensors = []
    remo_e_sensor_types = NatureRemoESensor.SENSOR_TYPES.keys()

    for appliance in appliances_update_coordinator.data.values():
        if appliance["type"] == "EL_SMART_METER":
            sensors.extend(
                [
                    NatureRemoESensor(
                        appliances_update_coordinator,
                        appliance,
                        sensor_type,
                    )
                    for sensor_type in remo_e_sensor_types
                ]
            )

    async_add_entities(sensors)


class NatureRemoESensor(NatureRemoBase, SensorEntity):
    """Implementation of a Nature Remo E sensor."""

    SENSOR_TYPES = {
        "measured_instantaneous": {
            "device_class": DEVICE_CLASS_POWER,
            "unit": POWER_WATT,
            "state_class": "measurement",
        },
        "normal_direction_cumulative_electric_energy": {
            "device_class": DEVICE_CLASS_ENERGY,
            "unit": ENERGY_KILO_WATT_HOUR,
            "state_class": "total_increasing",
        },
        "reverse_direction_cumulative_electric_energy": {
            "device_class": DEVICE_CLASS_ENERGY,
            "unit": ENERGY_KILO_WATT_HOUR,
            "state_class": "measurement",
        },
    }

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        appliance: dict,
        sensor_type: str,
    ):
        super().__init__(appliance)

        self._name = f"{appliance['nickname']} {sensor_type}"
        self._appliance_id = appliance["id"]
        self._coordinator = coordinator
        self._device_class = self.SENSOR_TYPES[sensor_type]["device_class"]
        self._unit_of_measurement = self.SENSOR_TYPES[sensor_type]["unit"]
        self._state_class = self.SENSOR_TYPES[sensor_type]["state_class"]
        self._sensor_type = sensor_type

    @property
    def unique_id(self):
        return f"{self._appliance_id}-{self._sensor_type}"

    @property
    def state(self):
        """
        Return the state of the sensor.
        Call the method with same name as sensor type.
        """

        return eval("self." + self._sensor_type)()

    @property
    def device_class(self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state_class(self):
        return self._state_class

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

    def measured_instantaneous(self):
        """Return instantaneous energy power"""

        return self.__echonetlite_properties()[231]["val"]

    def normal_direction_cumulative_electric_energy(self):
        """Return normal direction energy with cumulative value"""

        normal_direction_cumulative_electric_energy = int(
            self.__echonetlite_properties()[224]["val"]
        )

        return (
            normal_direction_cumulative_electric_energy
            * self.__coefficianet()
            * self.__cumulative_electric_energy_unit()
        )

    def reverse_direction_cumulative_electric_energy(self):
        """Return reverse direction energy with cumulative value"""

        reverse_direction_cumulative_electric_energy = int(
            self.__echonetlite_properties()[227]["val"]
        )

        return (
            reverse_direction_cumulative_electric_energy
            * self.__coefficianet()
            * self.__cumulative_electric_energy_unit()
        )

    def __echonetlite_properties(self):
        """Return echonetlite properties"""

        appliance = self._coordinator.data[self._appliance_id]
        echonetlite_properties = appliance["smart_meter"]["echonetlite_properties"]
        return {x["epc"]: x for x in echonetlite_properties}

    def __coefficianet(self):
        """Return coefficient for cumulative electric energy"""

        return int(self.__echonetlite_properties()[211]["val"])

    def __cumulative_electric_energy_unit(self):
        """Return cumulative energy unit"""

        value = self.__echonetlite_properties()[225]["val"]

        return {
            "0": 1,
            "1": 0.1,
            "2": 0.01,
            "3": 0.001,
            "4": 0.0001,
            "A": 10,
            "B": 100,
            "C": 1000,
            "D": 10000,
        }[value]
