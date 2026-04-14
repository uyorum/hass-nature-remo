"""Sensor platform for Nature Remo."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

SENSOR_TYPES = {
    "te": {
        "name": "Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "hu": {
        "name": "Humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "il": {
        "name": "Illuminance",
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "unit": LIGHT_LUX,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "mo": {
        "name": "Motion",
        # technically this should be a binary_sensor, but we represent as sensor for now if it gives numeric vals
        # or we just use it without device_class. Nature Remo motion is often a timestamp or 1/0.
    },
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nature Remo sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # 1. Remo Device Sensors
    for device in coordinator.data["devices"]:
        if "newest_events" in device:
            for sensor_id, data in device["newest_events"].items():
                if sensor_id in SENSOR_TYPES:
                    entities.append(NatureRemoDeviceSensor(coordinator, device, sensor_id))

    # 2. Remo E lite Smart Meter Sensors
    for appliance in coordinator.data["appliances"]:
        if appliance.get("type") == "EL_SMART_METER":
            # Add Instantaneous Power Sensor
            entities.append(NatureRemoSmartMeterSensor(coordinator, appliance, "measured_instantaneous"))
            # Add Cumulative Energy Sensor
            entities.append(NatureRemoSmartMeterSensor(coordinator, appliance, "normal_direction_cumulative_electric_energy"))

    async_add_entities(entities)


class NatureRemoDeviceSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a Nature Remo device sensor."""

    def __init__(self, coordinator, device, sensor_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device = device
        self._sensor_id = sensor_id
        
        sensor_info = SENSOR_TYPES[sensor_id]
        self._attr_name = f"{device['name']} {sensor_info.get('name', sensor_id)}"
        self._attr_unique_id = f"{device['id']}-{sensor_id}"
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_state_class = sensor_info.get("state_class")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device["id"])},
            name=self._device.get("name", "Nature Remo"),
            manufacturer="Nature Inc.",
            model=self._device.get("firmware_version", "Nature Remo"),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # Find device in updated data
        for device in self.coordinator.data["devices"]:
            if device["id"] == self._device["id"]:
                events = device.get("newest_events", {})
                if self._sensor_id in events:
                    if self._sensor_id == "mo":
                        from datetime import datetime, timezone
                        from .const import UPDATE_INTERVAL
                        created_at_str = events["mo"].get("created_at")
                        if created_at_str:
                            try:
                                created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                                # ネットワーク遅延等を考慮し、ポーリング間隔 + 15秒を閾値とする
                                if (datetime.now(timezone.utc) - created_at).total_seconds() <= (UPDATE_INTERVAL + 15):
                                    return 1
                                else:
                                    return 0
                            except Exception:
                                pass
                        return 0
                    
                    return events[self._sensor_id].get("val")
        return None


class NatureRemoSmartMeterSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a Nature Remo E Lite smart meter sensor."""

    def __init__(self, coordinator, appliance, property_name):
        """Initialize."""
        super().__init__(coordinator)
        self._appliance = appliance
        self._property_name = property_name

        if property_name == "measured_instantaneous":
            self._attr_name = f"{appliance['nickname']} Power"
            self._attr_unique_id = f"{appliance['id']}-power"
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif property_name == "normal_direction_cumulative_electric_energy":
            self._attr_name = f"{appliance['nickname']} Cumulative Energy"
            self._attr_unique_id = f"{appliance['id']}-cumulative_energy"
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        # Using dictionary .get() with empty dict fallback to avoid TypeError if device is not in response
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        manufacturer = "Nature Inc."
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
            name=self._appliance.get("nickname", "Nature Remo E lite"),
            manufacturer=manufacturer,
            via_device=(DOMAIN, device_id),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        for app in self.coordinator.data["appliances"]:
            if app["id"] == self._appliance["id"]:
                props = app.get("smart_meter", {}).get("echonetlite_properties", [])
                
                val_raw = None
                coef = 1.0
                unit_mult = 1.0
                
                for prop in props:
                    name = prop.get("name")
                    val_str = prop.get("val")
                    
                    if name == self._property_name:
                        val_raw = val_str
                    elif name == "coefficient":
                        try:
                            coef = float(val_str)
                        except (ValueError, TypeError):
                            pass
                    elif name == "cumulative_electric_energy_unit":
                        try:
                            unit_code = int(val_str)
                            if 0 <= unit_code <= 4:
                                unit_mult = 10 ** (-unit_code)
                            elif 10 <= unit_code <= 14:
                                unit_mult = 10 ** (unit_code - 9)
                        except (ValueError, TypeError):
                            pass

                if val_raw is None:
                    return None

                try:
                    val = float(val_raw)
                    if self._property_name == "normal_direction_cumulative_electric_energy":
                        return val * coef * unit_mult
                    return val
                except ValueError:
                    return val_raw
        return None
