"""

Example configuration

sensor:
  - platform: brandriskute
    latitude: !secret lat_coord
    longitude: !secret long_coord
"""
import logging
import json
from datetime import timedelta
from math import radians, sin, cos, acos
import requests

from urllib.request import urlopen
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_RADIUS)
from homeassistant.util import Throttle
import homeassistant.util.dt as dt_util

__version__ = '1.0.0'

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Brandrisk Ute'
ICON = ["mdi:fire-alert", "mdi:pine-tree-fire"]

SCAN_INTERVAL = timedelta(hours=6)
CONF_VERBOSE = "verbose"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_VERBOSE): cv.boolean
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Brandrisk sensor."""
    name = config.get(CONF_NAME) if config.get(CONF_NAME) is not None else DEFAULT_NAME
    latitude = config.get(CONF_LATITUDE) if config.get(CONF_LATITUDE) is not None else hass.config.latitude
    longitude = config.get(CONF_LONGITUDE) if config.get(CONF_LONGITUDE) is not None else hass.config.longitude
    verbose = config.get(CONF_VERBOSE) if config.get(CONF_VERBOSE) is not None else False

    api = BrandriskAPI(longitude, latitude, verbose)

    add_entities([BrandriskSensor(api, name, ICON)], True)

    # Separate sensor for forecast
    add_entities([BrandriskForecast(api, name, ICON)], True)

class BrandriskSensor(Entity):
    """Representation of a Brandrisk sensor."""

    def __init__(self, api, name, icon):
        """Initialize a Brandrisk sensor."""
        self._api = api
        self._name = name
        self._icon = icon
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend."""
        if self._api.current['grassIndex'] > self._api.current['woodIndex']:
            return self._icon[0]
        else:
            return self._icon[1]

    @property
    def state(self):
        """Return the state of the device."""
        return self._api.state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        data = {}
        keys = list(self._api.current.keys())
        for index, key in enumerate(keys):
            data[key] = self._api.current[key]
        data['prohibition'] = self._api.prohibition

        return data

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from the Brandrisk API."""
        self._api.update()

class BrandriskForecast(Entity):
    """Representation of a Brandrisk forecast sensor."""

    def __init__(self, api, name, icon):
        """Initialize a Brandrisk forecast sensor."""
        self._api = api
        self._name = name
        self._icon = icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name + "_forecast"

    @property
    def icon(self):
        """Icon to use in the frontend."""
        if self._api.current['grassIndex'] > self._api.current['woodIndex']:
            return self._icon[0]
        else:
            return self._icon[1]

    @property
    def state(self):
        """Return the state of the device."""
        return self._api.state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""

        return {
            'forecast': self._api.forecast
        }

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from the Brandrisk API."""
        self._api.update()

class BrandriskAPI:
    """Get the latest data and update the states."""

    URL_BASE = "https://api.msb.se/brandrisk/v2"
    URL_CURRENT = "/CurrentRisk/sv/{lat}/{lon}"
    URL_FORECAST = "/RiskDailyForecast/sv/{lat}/{lon}"
    URL_PROHIBITION = "/FireProhibition/{lat}/{lon}"

    def __init__(self, longitude, latitude, verbose):
        """Initialize the data object."""

        self.lat = latitude
        self.lon = longitude
        self.verbose = verbose
        self.current = {}
        self.forecast = []
        self.prohibition = {}
        self.state = ''
        self.available = True
        self.update()

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data from Brandrisk Ute."""
        self.current = {}
        self.forecast = []
        self.prohibition = {}

        _LOGGER.debug("Trying to update")

        try:
            # Fetch current risk
            response = urlopen(self.URL_BASE + self.URL_CURRENT.format(lat=self.lat, lon=self.lon))
            data = response.read().decode('utf-8')
            jsondata = json.loads(data)
            self.state = jsondata['forecast']['riskIndex']

            if self.verbose:
                self.current = jsondata['forecast']
            else:
                self.current['date'] = jsondata['forecast']['date']
                self.current['riskIndex'] = jsondata['forecast']['riskIndex']
                self.current['grassIndex'] = jsondata['forecast']['grassIndex']
                self.current['woodIndex'] = jsondata['forecast']['woodIndex']
                self.current['riskMessage'] = jsondata['forecast']['riskMessage']

        except Exception as e:
            _LOGGER.error("Unable to fetch current risk from Brandrisk Ute.")
            _LOGGER.error(str(e))
            self.available = False

        try:
            # Fetch forecast
            response = urlopen(self.URL_BASE + self.URL_FORECAST.format(lat=self.lat, lon=self.lon))
            data = response.read().decode('utf-8')
            jsondata = json.loads(data)

            for index, element in enumerate(jsondata):
                if self.verbose:
                    self.forecast.append(element)
                else:
                    forecast_day = {}
                    forecast_day['date'] = element['date']
                    forecast_day['riskIndex'] = element['riskIndex']
                    forecast_day['grassIndex'] = element['grassIndex']
                    forecast_day['woodIndex'] = element['woodIndex']
                    forecast_day['riskMessage'] = element['riskMessage']
                    self.forecast.append(forecast_day)

        except Exception as e:
            _LOGGER.error("Unable to fetch forecast from Brandrisk Ute.")
            _LOGGER.error(str(e))
            self.available = False

        try:
            # Fetch prohibition
            response = urlopen(self.URL_BASE + self.URL_PROHIBITION.format(lat=self.lat, lon=self.lon))
            data = response.read().decode('utf-8')
            jsondata = json.loads(data)
            self.prohibition = jsondata['fireProhibition']['status']

            self.available = True
        except Exception as e:
            _LOGGER.error("Unable to fetch prohibition from Brandrisk Ute.")
            _LOGGER.error(str(e))
            self.available = False