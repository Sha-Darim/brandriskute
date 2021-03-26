![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg?style=for-the-badge)

[![Version](https://img.shields.io/badge/version-1.0.0-green.svg?style=for-the-badge)](#) [![maintained](https://img.shields.io/maintenance/yes/2021.svg?style=for-the-badge)](#)

[![maintainer](https://img.shields.io/badge/maintainer-Fredric%20Palmgren%20%40sha--darim-blue.svg?style=for-the-badge)](#)


# Brandrisk Ute
Component to get swedish outdoors fire risks for [Home Assistant](https://www.home-assistant.io/).

The plugin will get fire risks from the Brandrisk Ute API for the supplied position.
There are two different kind of risks:
1. Current risk
2. 3 days forecast

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

**Example minimal configuration.yaml**
```yaml
sensor:
  - platform: brandriskute
```

**Example configuration.yaml using latitude/longitude from [secrets](https://www.home-assistant.io/docs/configuration/secrets/)**
```yaml
sensor:
  - platform: brandriskute
    latitude: !secret latitude
    longitude: !secret longitude
```
***
