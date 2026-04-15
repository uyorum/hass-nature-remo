"""Climate platform for Nature Remo."""
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .coordinator import NatureRemoDataUpdateCoordinator

HA_TO_REMO_MODE = {
    HVACMode.AUTO: "auto",
    HVACMode.COOL: "cool",
    HVACMode.HEAT: "heat",
    HVACMode.DRY: "dry",
    HVACMode.FAN_ONLY: "blow",
}
REMO_TO_HA_MODE = {v: k for k, v in HA_TO_REMO_MODE.items()}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nature Remo climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for appliance in coordinator.data["appliances"]:
        if appliance.get("type") == "AC":
            entities.append(NatureRemoClimate(coordinator, appliance))

    async_add_entities(entities)


class NatureRemoClimate(CoordinatorEntity, ClimateEntity):
    """Implementation of a Nature Remo climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )

    def __init__(self, coordinator: NatureRemoDataUpdateCoordinator, appliance):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._appliance = appliance
        self._attr_name = appliance.get("nickname", "Air Conditioner")
        self._attr_unique_id = appliance.get("id")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        model = self._appliance.get("model", {}) or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
            name=self._appliance.get("nickname", "Air Conditioner"),
            manufacturer=model.get("manufacturer", "Unknown"),
            model=model.get("name", "Unknown Model"),
            via_device=(DOMAIN, device_id),
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        for app in self.coordinator.data["appliances"]:
            if app["id"] == self._appliance["id"]:
                settings = app.get("settings", {})
                if settings.get("button") == "power-off":
                    return HVACMode.OFF
                mode = settings.get("mode")
                return REMO_TO_HA_MODE.get(mode, HVACMode.OFF)
        return HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        modes = [HVACMode.OFF]
        # Depending on Remo AC configuration we might need to parse `aircon.range.modes`
        # For simplicity, we expose the standard ones.
        return modes + list(HA_TO_REMO_MODE.keys())

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        for app in self.coordinator.data["appliances"]:
            if app["id"] == self._appliance["id"]:
                temp = app.get("settings", {}).get("temp")
                if temp:
                    try:
                        return float(temp)
                    except ValueError:
                        pass
        return None

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            settings = {"temperature": str(int(temp))}  # Remo API expects temperature, not temp
            await self.coordinator.api.post_ac_settings(self._appliance["id"], settings)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.api.post_ac_settings(self._appliance["id"], {"button": "power-off"})
        else:
            mode = HA_TO_REMO_MODE.get(hvac_mode)
            if mode:
                await self.coordinator.api.post_ac_settings(self._appliance["id"], {"button": "", "operation_mode": mode})
        await self.coordinator.async_request_refresh()
