"""Button platform for Nature Remo."""
from homeassistant.components.button import ButtonEntity
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
    """Set up Nature Remo button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = []
    for appliance in coordinator.data["appliances"]:
        # Custom IR devices often have the type "IR"
        if "signals" in appliance:
            for signal in appliance["signals"]:
                entities.append(NatureRemoSignalButton(coordinator, appliance, signal))
        
        # Expose extra buttons for Light devices (brightness, night light, etc.)
        if appliance.get("type") == "LIGHT":
            buttons = appliance.get("light", {}).get("buttons", [])
            for btn in buttons:
                btn_name = btn.get("name")
                if btn_name not in ["on", "off"]:
                    entities.append(NatureRemoApplianceButton(coordinator, appliance, btn_name))

    async_add_entities(entities)


class NatureRemoSignalButton(CoordinatorEntity[NatureRemoDataUpdateCoordinator], ButtonEntity):
    """Implementation of a Nature Remo IR signal as a button."""

    def __init__(self, coordinator: NatureRemoDataUpdateCoordinator, appliance, signal):
        """Initialize."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._appliance = appliance
        self._signal = signal
        self._attr_name = f"{appliance.get('nickname')} {signal.get('name')}"
        self._attr_unique_id = signal.get("id")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
            name=self._appliance.get("nickname", "IR Appliance"),
            manufacturer="Nature Inc. / Unknown",
            via_device=(DOMAIN, device_id),
        )

    async def async_press(self) -> None:
        """Send the IR signal."""
        await self.coordinator.api.post_signal(self._signal["id"])


class NatureRemoApplianceButton(CoordinatorEntity[NatureRemoDataUpdateCoordinator], ButtonEntity):
    """Implementation of a built-in Nature Remo appliance button (e.g. brightness, night light)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NatureRemoDataUpdateCoordinator, appliance, button_name):
        """Initialize."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._appliance = appliance
        self._button_name = button_name
        self._attr_name = button_name.replace("-", " ").title()
        self._attr_unique_id = f"{appliance.get('id')}-{button_name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_id = self._appliance.get("device", {}).get("id", "unknown_device_id")
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance["id"])},
        )

    async def async_press(self) -> None:
        """Press the button."""
        if self._appliance.get("type") == "LIGHT":
            await self.coordinator.api.post_light_button(self._appliance["id"], self._button_name)
