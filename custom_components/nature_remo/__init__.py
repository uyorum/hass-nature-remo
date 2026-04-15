"""The Nature Remo integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NatureRemoApiClient
from .const import DOMAIN, CONF_ACCESS_TOKEN
from .coordinator import NatureRemoDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.LIGHT,
    Platform.BUTTON,
    Platform.MEDIA_PLAYER,
]

from homeassistant.helpers import device_registry as dr

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nature Remo from a config entry."""
    session = async_get_clientsession(hass)
    api = NatureRemoApiClient(entry.data[CONF_ACCESS_TOKEN], session)
    
    coordinator = NatureRemoDataUpdateCoordinator(hass, api)
    
    # Fetch initial data so we have state when entities are added
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register all physical devices (Hubs) explicitly into the Device Registry.
    # This ensures that devices without sensors (like Remo E lite) are still visible
    # and that appliances can correctly link to them using `via_device`.
    device_registry = dr.async_get(hass)
    for device in coordinator.data["devices"]:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device["id"])},
            name=device.get("name", "Nature Remo Device"),
            manufacturer="Nature Inc.",
            model=device.get("firmware_version", "Nature Remo"),
            sw_version=device.get("firmware_version"),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
