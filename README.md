# Home Assistant integration for Nature Remo

Yet another [Home Assistant](https://www.home-assistant.io) component for [Nature Remo](https://en.nature.global/en/).

⚠️This integration is neither Nature Remo official nor Home Assistant official. **Use at your own risk.** ⚠️

<img src="./assets/screenshot_1.png" width="600"><img src="./assets/screenshot_2.png" width="200">

# MrTolkien fork

This is a fork adding basic Lights support as well as a refactor for readability.

**AS OF 2021-10-15 THERE IS NO DOC FOR THIS INTEGRATION**

## Supported features

- [x] Air Conditioner
  - [x] Set mode (e.g. cool, warm, blow etc.)
  - [x] Set temperature
  - [x] Set fan mode
  - [x] Set swing mode
  - [x] Show current temperature
  - [x] Remember previous target temperatures when switching modes back and forth
- [x] Energy Sensor (Nature Remo E/E Lite)
  - [x] Fetch current power usage
- [ ] Switch
- [x] Light (WORK IN PROGRESS BY @MrTolkien)
- [ ] TV
- [ ] Others
  - [ ] Fetch sensor data

Tested on Home Assistant Core 2021.3.3 on Docker

## Installation

### Manual Install

Add the contents of `custom_components/nature_remo` to the `/config/custom_components/nature_remo` folder of your 
Home Assistant installation
- You can either copy the folder directly or set up a symbolic link/docker mount

Final structure:
```
{/config}
├── configuration.yaml
└── custom_components
    └── nature_remo
        ├── __init__.py
        ├── climate.py
        ├── manifest.json
        ├── light.json
        └── sensor.py
              
```

## Configuration

1. Go to https://home.nature.global and sign in/up
1. Generate access token
1. Add the token to your `configuration.yaml` file

```yaml
nature_remo:
  access_token: YOUR_ACCESS_TOKEN
```
