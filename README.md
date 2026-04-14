# hass-nature-remo

[![Validate with hassfest](https://github.com/uyorum/hass-nature-remo/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/uyorum/hass-nature-remo/actions/workflows/hassfest.yaml)
[![Validate with HACS](https://github.com/uyorum/hass-nature-remo/actions/workflows/hacs.yaml/badge.svg)](https://github.com/uyorum/hass-nature-remo/actions/workflows/hacs.yaml)

Home Assistant Custom Component for Nature Remo & Nature Remo E / E lite.

This integration uses the official Nature Remo Cloud API and utilizes a `DataUpdateCoordinator` to gracefully respect the API's tight rate limitations (polls are comfortably spaced at 60 seconds).

All devices and appliances fetched from Nature Remo are registered natively into the **Home Assistant Device Registry**. This means your Air Conditioners, Lights, TVs, and Remo Sensors are grouped into self-contained "Home Assistant Devices", keeping your entities well-organized and correctly parented to the physical Remo Hub.

## Features Supported & Implementation Details

- **Nature Remo Environmental Sensors**
  - Temperature, Humidity, Illuminance.
  - **Motion**: The API structurally reports motion events as a constant value (always 1). This component tracks the `created_at` timestamp. If a motion was detected within the current 60-second polling cycle, the sensor returns `1`. If no motion is detected over 75 seconds (including 15s network buffer), it resets to `0`.

- **Nature Remo E / E lite (Smart Meters)**
  - **Instantaneous Power (W)**
  - **Cumulative Electric Energy (kWh)**: This integration adheres strictly to the ECHONET Lite protocol. Raw energy values are securely multiplied with the hardware's internal scale factors (`coefficient` and `cumulative_electric_energy_unit`), displaying accurate kWh values out-of-the-box perfectly compatible with HA's Energy Dashboard without any manual rounding.

- **Air Conditioners (Climate)**
  - Power, Temperature settings, and HVAC Modes (Auto, Cool, Heat, Dry, Fan).

- **Lights (Light)**
  - Standard ON/OFF control compatible with all modern HA lighting cards.
  - **Additional Lighting Options**: Stepped IR commands (e.g., Brightness up/down, Color temperature up/down, Night mode button) are deployed as supplementary `Button` entities attached intuitively alongside your `Light` entity within the same Light Device space.

- **TVs (Media Player)**
  - Volume, Channel, Power.

- **Custom IR signals (Button)**
  - Any custom remote signals learned via the Nature Remo app are surfaced automatically as standard HA button entities.

## Installation

1. Copy the `custom_components/nature_remo` directory into your Home Assistant's `config/custom_components` directory.
2. Restart Home Assistant.
3. Obtain an access token from [home.nature.global](https://home.nature.global/).
4. In Home Assistant, navigate to **Settings -> Devices & Services -> Add Integration** and search for "Nature Remo".
5. Enter your access token and enjoy your natively grouped appliances!
