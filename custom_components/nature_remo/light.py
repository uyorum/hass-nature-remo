"""Light platform for Nature Remo."""
from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .coordinator import NatureRemoDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nature Remo light platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for appliance in coordinator.data["appliances"]:
        if appliance.get("type") == "LIGHT":
            entities.append(NatureRemoLight(coordinator, appliance))

    async_add_entities(entities)


class NatureRemoLight(CoordinatorEntity, LightEntity):
    """Implementation of a Nature Remo light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, coordinator: NatureRemoDataUpdateCoordinator, appliance):
        """Initialize."""
        super().__init__(coordinator)
        self._appliance = appliance
        self._attr_unique_id = appliance.get("id")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
            name=self._appliance.get("nickname", "Light"),
            manufacturer="Nature Inc. / Unknown",
            via_device=(DOMAIN, device_id),
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        for app in self.coordinator.data["appliances"]:
            if app["id"] == self._appliance["id"]:
                light = app.get("light", {})
                status = light.get("state", {}).get("power")
                return status == "on"
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        await self.coordinator.api.post_light_button(self._appliance["id"], "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        await self.coordinator.api.post_light_button(self._appliance["id"], "off")
        await self.coordinator.async_request_refresh()
