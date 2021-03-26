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

SCAN_INTERVAL = timedelta(hours=6)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Brandrisk sensor."""
    name = config.get(CONF_NAME) if config.get(CONF_NAME) is not None else DEFAULT_NAME
    latitude = config.get(CONF_LATITUDE) if config.get(CONF_LATITUDE) is not None else hass.config.latitude
    longitude = config.get(CONF_LONGITUDE) if config.get(CONF_LONGITUDE) is not None else hass.config.longitude

    api = BrandriskAPI(longitude, latitude)

    add_entities([BrandriskSensor(api, name)], True)

class BrandriskSensor(Entity):
    """Representation of a Brandrisk sensor."""

    def __init__(self, api, name):
        """Initialize a Brandrisk sensor."""
        self._api = api
        self._name = name
        self.attributes = {}
        self.attributes["current"] = {}
        self.attributes["forecast"] = []
        self._icon = []
        self._icon.append("mdi:fire-alert")
        self._icon.append("mdi:pine-tree-fire")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend."""
        if self._api.current['Grass'] > self._api.current['Wood']:
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
        data = {
            'current': self._api.current,
            'forecast': self._api.forecast
        }

        return data

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from the Brandrisk API."""
        self._api.update('forecast')

class BrandriskAPI:
    """Get the latest data and update the states."""

    URL_CURRENT = "https://brandriskapp.msb.se/RiskService.svc/currentrisk/sv/{lat}|{lon}"
    URL_FORECAST = "https://brandriskapp.msb.se/RiskService.svc/RiskForecast/sv/{lat}|{lon}"

    def __init__(self, longitude, latitude):
        """Initialize the data object."""
        
        self.lat = latitude
        self.lon = longitude
        self.current = {}
        self.forecast = []
        self.state = ''
        self.available = True
        self.update()

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data from Brandrisk Ute."""
        try:
            self.current = {}
            self.forecast = []

            _LOGGER.debug("Trying to update")

            # Fetch current risk
            response = urlopen(self.URL_CURRENT.format(lat=self.lat, lon=self.lon))

            data = response.read().decode('utf-8')
            jsondata = json.loads(data)
            self.current = self.make_object(jsondata)

            # Fetch forecast
            response = urlopen(self.URL_FORECAST.format(lat=self.lat, lon=self.lon))

            data = response.read().decode('utf-8')
            jsondata = json.loads(data)

            for index, element in enumerate(jsondata):
                self.forecast.append(self.make_object(element))

            if self.current['Grass'] == 6 or self.current['Wood'] == 6:
                risk = "Extermt stor risk"
            elif self.current['Grass'] == 5 or self.current['Wood'] == 5:
                risk = "Mycket stor risk"
            elif self.current['Grass'] == 4 or self.current['Wood'] == 4:
                risk = "Stor risk"
            elif self.current['Grass'] == 3 or self.current['Wood'] == 3:
                risk = "Måttlig risk"
            elif self.current['Grass'] == 2 or self.current['Wood'] == 2:
                risk = "Liten risk"
            elif self.current['Grass'] == 1 or self.current['Wood'] == 1:
                risk = "Mycket liten risk"

            self.state = risk

            self.available = True
        except Exception as e:
            _LOGGER.error("Unable to fetch data from Brandrisk Ute.")
            _LOGGER.error(str(e))
            self.available = False

    def make_object(self, element):
        risk = {}

        risk['Date'] = element['Date']
        risk['Grass'] = element['Grass']
        risk['GrassMsg'] = element['GrassMsg']
        risk['IssuedDate'] = element['IssuedDate']
        risk['Wood'] = element['Wood']
        risk['WoodMsg'] = element['WoodMsg']

        return risk
