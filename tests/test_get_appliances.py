import custom_components.nature_remo.light


async def test_create_light(hass):
    await custom_components.nature_remo.light.async_setup_platform(hass, {}, None, None)
