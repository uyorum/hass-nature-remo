"""Remote platform for Nature Remo hubs."""
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nature Remo remote platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    # Register the main hub itself as a remote
    for device in coordinator.data["devices"]:
        entities.append(NatureRemoHub(coordinator, device))

    async_add_entities(entities)


class NatureRemoHub(CoordinatorEntity, RemoteEntity):
    """Implementation of a Nature Remo hub as a Remote."""

    def __init__(self, coordinator, device):
        """Initialize."""
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{device.get('name', 'Nature Remo')} Hub"
        self._attr_unique_id = f"hub-{device.get('id')}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device["id"])},
            name=self._device.get("name", "Nature Remo Hub"),
            manufacturer="Nature Inc.",
            model=self._device.get("firmware_version", "Nature Remo"),
        )

    @property
    def is_on(self) -> bool:
        """Return true if remote is on."""
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the remote on."""
        pass

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the remote off."""
        pass

    async def async_send_command(self, command: list[str], **kwargs: Any) -> None:
        """Send commands to a device."""
        # Here we allow passing a raw signal UUID as a command
        for cmd in command:
            try:
                await self.coordinator.api.post_signal(cmd)
            except Exception:
                pass
