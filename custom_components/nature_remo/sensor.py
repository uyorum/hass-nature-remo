from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from homeassistant.components.sensor import SensorEntity


from . import DOMAIN, _LOGGER

# TODO BinarySensor for motion

# TODO Use the values from Home Assistant
#   Move the data out in its own class too
sensor_class = {
    "hu": "humidity",
    "il": "illuminance",
    # "mo": "motion", # TODO
    "te": "temperature",
}

sensor_units = {
    "hu": "%",
    "il": "lm",  # TODO Check
    "mo": "?",
    "te": "°C",
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    """Sets up sensors found in the Nature Remo API"""
    if discovery_info is None:
        # TODO What even is that
        return

    _LOGGER.debug("Setting up Nature Remo sensors")

    devices_update_coordinator = hass.data[DOMAIN]["devices_update_coordinator"]

    async_add_entities(
        [
            NatureRemoSensor(
                devices_update_coordinator,
                device,
                sensor_type,
            )
            for device in devices_update_coordinator.data.values()
            for sensor_type in device["newest_events"]
            if sensor_type in sensor_class
        ]
    )


class NatureRemoSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a Nature Remo sensor"""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: dict,
        sensor_type: str,
    ):
        # We don't need to have an API object in that one as the updating is fully done through the coordinator

        # Calling the CoordinatorEntity constructor which adds listeners and self.coordinator
        super(NatureRemoSensor, self).__init__(coordinator)

        # Concatenating the device name and sensor type
        self._name = f"{device['name']} - {sensor_class[sensor_type]}"

        # device.id cannot unique id in itself as there are multiple sensors per device
        self._device_id = device["id"]
        self._sensor_type = sensor_type

        # TODO Add offsets for temp and humidity

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self) -> str | None:
        return f"{self._device_id}-{self._sensor_type}"

    @property
    def device_class(self) -> str | None:
        return sensor_class[self._sensor_type]

    @property
    def native_unit_of_measurement(self):
        return sensor_units[self._sensor_type]

    @property
    def state_class(self) -> str | None:
        return "measurement"

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data[self._device_id]["newest_events"][
            self._sensor_type
        ]
