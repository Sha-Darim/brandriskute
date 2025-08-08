![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg?style=for-the-badge)

[![Version](https://img.shields.io/badge/version-2.0-green.svg?style=for-the-badge)](#) [![maintained](https://img.shields.io/maintenance/yes/2025.svg?style=for-the-badge)](#)

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
2. Inside that folder, create another folder named `brandriskute`. 
3. Use intewgrations to add yor datta

**Configuration variables:**

key | type | description
:--- | :--- | :---
**latitude (required)** | string | The latitude of the position from which the sensor should look for fire risks messages. Default `home zone latitude`
**longitude (required)** | string | The longitude of the position from which the sensor should look for fire risks messages. Default `home zone longitude`
**name (required)** | string | Custom name for the sensor. Default `Brandrisk Ute`.
**verbose (Optional)** | boolean | Use full information or the the basics only. Default `True`
**forecast (Optional)** | boolean | Use forecast sensor. Default `True`
**prohibition (Optional)** | boolean | Use prohibition sensor. Default `True`


**Example automation using prohibition change**
```yaml
alias: 'Eldningsförbud Alert'
initial_state: 'on'
trigger:
  - platform: state
    entity_id: sensor.brandrisk_orebro_prohibition
action:
  - service: notify.mobile_app_user
    data:
      message: "{{ states('sensor.brandrisk_orebro_prohibition') }} {{ state_attr('sensor.brandrisk_orebro_prohibition', 'startDate') }} {{ state_attr('sensor.brandrisk_orebro_prohibition', 'description') }}
```
***

<a href="https://www.buymeacoffee.com/shadarim" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

