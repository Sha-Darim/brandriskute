![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg?style=for-the-badge)

[![Version](https://img.shields.io/badge/version-1.1.3-green.svg?style=for-the-badge)](#) [![maintained](https://img.shields.io/maintenance/yes/2021.svg?style=for-the-badge)](#)

[![maintainer](https://img.shields.io/badge/maintainer-Fredric%20Palmgren%20%40sha--darim-blue.svg?style=for-the-badge)](#)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Brandrisk Ute
Component to get swedish outdoors fire risks for [Home Assistant](https://www.home-assistant.io/).

The custom compontnet will, while using the supplied position, get fire risks and fire prohibition information from MSB's [Brandrisk Ute API](https://www.msb.se/sv/om-msb/informationskanaler/appar/brandrisk-ute/).
The plugin supplies three different sensors:
1. Current risk
2. 3 days forecast
3. Fire prohibition

## Installation:
1. Install this component by creating a `custom_components` folder in the same folder as your configuration.yaml is, if you don't already have one.
2. Inside that folder, create another folder named `brandriskute`. Put the `sensor.py` file in there (if you copy and paste the code, make sure you do it from the [raw version](https://raw.githubusercontent.com/Sha-Darim/brandriskute/master/sensor.py) of the file).
2. Add the configuration to your `configuration.yaml` using the config options below.
3. **You will need to restart after installation for the component to start working.**

**Configuration variables:**

key | type | description
:--- | :--- | :---
**platform (Required)** | string | `brandriskute`
**latitude (Optional)** | string | The latitude of the position from which the sensor should look for fire risks messages. Default `home zone latitude`
**longitude (Optional)** | string | The longitude of the position from which the sensor should look for fire risks messages. Default `home zone longitude`
**name (Optional)** | string | Custom name for the sensor. Default `Brandrisk Ute`.
**verbose (Optional)** | boolean | Use full information or the the basics only. Default `True`
**forecast (Optional)** | boolean | Use forecast sensor. Default `True`
**prohibition (Optional)** | boolean | Use prohibition sensor. Default `True`

**Example minimal configuration.yaml**
```yaml
sensor:
  - platform: brandriskute
```

**Example configuration.yaml using latitude/longitude from [secrets](https://www.home-assistant.io/docs/configuration/secrets/)**
```yaml
sensor:
  - platform: brandriskute
    latitude: !secret lat_coord
    longitude: !secret long_coord
    forecast: false
    prohibition: true
    verbose: false
```

**Example automation using prohibition change**
```yaml
alias: 'Eldningsförbud Alert'
initial_state: 'on'
trigger:
  - platform: state
    entity_id: sensor.brandriskute_prohibition
action:
  - service: notify.mobile_app_user
    data:
      message: "{{ states('sensor.brandriskute_prohibition') }} {{ state_attr('sensor.brandriskute_prohibition', 'startDate') }} {{ state_attr('sensor.brandriskute_prohibition', 'description') }}
```
***

<a href="https://www.buymeacoffee.com/shadarim" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

