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
1. Use [HACS](https://hacs.xyz/docs/setup/download), in `HACS > Integrations > Explore & Add Repositories` search for "Brandrisk Ute". After adding this `https://github.com/alandtse/tesla` as a custom repository. Skip to 7.
2. If you do not have HACS, use the tool of choice to open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
3. If you do not have a `custom_components` directory (folder) there, you need to create it.
4. In the `custom_components` directory (folder) create a new folder called `brandriskut`.
5. Download _all_ the files from the `custom_components/brandriskut/` folder in this repository.
6. Place the files you downloaded in the new directory (folder) you created.
7. Inside that folder, create another folder named `brandriskute`.
8. Restart Home Assistant.
9. Add the integration: [![Add Integration][add-integration-badge]][add-integration] or in the HA UI go to "Settings" -> "Devices & Services" then click "+" and search for Brandrisk

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

[add-integration]: https://my.home-assistant.io/redirect/config_flow_start?domain=brandriskute
[add-integration-badge]: https://my.home-assistant.io/badges/config_flow_start.svg

