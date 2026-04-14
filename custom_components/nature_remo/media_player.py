"""Media Player platform for Nature Remo TV appliances."""
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nature Remo media player platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for appliance in coordinator.data["appliances"]:
        if appliance.get("type") == "TV":
            entities.append(NatureRemoTV(coordinator, appliance))

    async_add_entities(entities)


class NatureRemoTV(CoordinatorEntity, MediaPlayerEntity):
    """Implementation of a Nature Remo TV."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
    )

    def __init__(self, coordinator, appliance):
        """Initialize."""
        super().__init__(coordinator)
        self._appliance = appliance
        self._attr_name = appliance.get("nickname", "TV")
        self._attr_unique_id = appliance.get("id")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
            name=self._appliance.get("nickname", "TV"),
            manufacturer="Nature Inc. / Unknown",
            via_device=(DOMAIN, device_id),
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        for app in self.coordinator.data["appliances"]:
            if app["id"] == self._appliance["id"]:
                power = app.get("tv", {}).get("state", {}).get("power")
                return MediaPlayerState.ON if power == "on" else MediaPlayerState.OFF
        return MediaPlayerState.OFF

    async def async_turn_on(self) -> None:
        """Turn on."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "power")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "power")
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Volume up."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "vol-up")

    async def async_volume_down(self) -> None:
        """Volume down."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "vol-down")

    async def async_media_next_track(self) -> None:
        """Channel up."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "ch-up")

    async def async_media_previous_track(self) -> None:
        """Channel down."""
        await self.coordinator.api.post_tv_button(self._appliance["id"], "ch-down")
