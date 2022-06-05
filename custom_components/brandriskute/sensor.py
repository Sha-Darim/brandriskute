"""

Example configuration

sensor:
  - platform: brandriskute
    latitude: !secret lat_coord
    longitude: !secret long_coord
    forecast: false
    prohibition: true
    verbose: false
"""
from __future__ import annotations

import logging
import json
from datetime import timedelta
from typing import Any

from urllib.request import urlopen

import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.util import Throttle

__version__ = "1.1.3"

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Brandrisk Ute"
ICON = ["mdi:fire-alert", "mdi:pine-tree-fire", "mdi:fire-off"]
SCAN_INTERVAL = timedelta(hours=6)

CONF_USE_FORECAST = "forecast"
CONF_USE_PROHIBITION = "prohibition"
CONF_VERBOSE = "verbose"

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_USE_FORECAST, default=True): cv.boolean,
        vol.Optional(CONF_USE_PROHIBITION, default=True): cv.boolean,
        vol.Optional(CONF_VERBOSE, default=True): cv.boolean,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Brandrisk sensor."""
    name = config[CONF_NAME]
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    use_forecast = config[CONF_USE_FORECAST]
    use_prohibition = config[CONF_USE_PROHIBITION]
    verbose = config[CONF_VERBOSE]
    usage = [use_forecast, use_prohibition, verbose]

    api = BrandriskAPI(longitude, latitude, usage)

    entities: list = [BrandriskSensor(api, name, ICON)]

    if use_forecast:
        entities.append([BrandriskForecastSensor(api, name, ICON)], True)

    if use_prohibition:
        entities.append([BrandriskProhibitionSensor(api, name, ICON)], True)

    async_add_entities(entities, True)


class BrandriskSensor(SensorEntity):
    """Representation of a Brandrisk sensor."""

    def __init__(self, api: BrandriskAPI, name: str, icon: list) -> None:
        """Initialize a Brandrisk sensor."""
        self._api: BrandriskAPI = api
        self._attr_name = name
        self._icon = icon

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        if self._api.current["grassIndex"] > self._api.current["woodIndex"]:
            return self._icon[0]
        return self._icon[1]

    @property
    def native_value(self) -> StateType:
        return self._api.state

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes of the sensor."""
        data = {}
        keys = list(self._api.current.keys())
        for index, key in enumerate(keys):
            data[key] = self._api.current[key]

        return data

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self) -> None:
        """Get the latest data from the Brandrisk API."""
        self._api.update()


class BrandriskForecastSensor(SensorEntity):
    """Representation of a Brandrisk forecast sensor."""

    def __init__(self, api: BrandriskAPI, name: str, icon: list) -> None:
        """Initialize a Brandrisk forecast sensor."""
        self._api: BrandriskAPI = api
        self._attr_name = f"{name}_forecast"
        self._icon = icon

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        if self._api.current["grassIndex"] > self._api.current["woodIndex"]:
            return self._icon[0]
        return self._icon[1]

    @property
    def native_value(self) -> StateType:
        return self._api.state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        return {"forecast": self._api.forecast}

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self) -> None:
        """Get the latest data from the Brandrisk API."""
        self._api.update()


class BrandriskProhibitionSensor(SensorEntity):
    """Representation of a Brandrisk prohibition sensor."""

    def __init__(self, api: BrandriskAPI, name: str, icon: list) -> None:
        """Initialize a Brandrisk prohibition sensor."""
        self._api: BrandriskAPI = api
        self._attr_name = f"{name}_prohibition"
        self._attr_icon = icon[2]
        self._icon = icon

    @property
    def native_value(self) -> StateType:
        return self._api.prohibition["status"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        data = {}
        keys = list(self._api.prohibition.keys())
        for index, key in enumerate(keys):
            data[key] = self._api.prohibition[key]

        return data

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self) -> None:
        """Get the latest data from the Brandrisk API."""
        self._api.update()


class BrandriskAPI:
    """Get the latest data and update the states."""

    URL_BASE = "https://api.msb.se/brandrisk/v2"
    URL_CURRENT = "/CurrentRisk/sv/{lat}/{lon}"
    URL_FORECAST = "/RiskDailyForecast/sv/{lat}/{lon}"
    URL_PROHIBITION = "/FireProhibition/{lat}/{lon}"

    def __init__(self, longitude: float, latitude: float, usage: list) -> None:
        """Initialize the data object."""

        self.lat = latitude
        self.lon = longitude
        self.use_forecast = usage[0]
        self.use_prohibition = usage[1]
        self.verbose = usage[2]
        self.current = {}
        self.forecast = []
        self.prohibition = {}
        self.state = ""
        self.available = True
        self.update()

    @Throttle(SCAN_INTERVAL)
    def update(self) -> None:
        """Get the latest data from Brandrisk Ute."""
        self.current = {}
        self.forecast = []
        self.prohibition = {}

        _LOGGER.debug("Trying to update")

        try:
            # Fetch current risk
            response = urlopen(
                self.URL_BASE + self.URL_CURRENT.format(lat=self.lat, lon=self.lon)
            )
            data = response.read().decode("utf-8")
            jsondata = json.loads(data)
            self.state = jsondata["forecast"]["riskIndex"]

            if self.verbose:
                self.current = jsondata["forecast"]
            else:
                self.current["date"] = jsondata["forecast"]["date"]
                self.current["riskIndex"] = jsondata["forecast"]["riskIndex"]
                self.current["grassIndex"] = jsondata["forecast"]["grassIndex"]
                self.current["woodIndex"] = jsondata["forecast"]["woodIndex"]
                self.current["riskMessage"] = jsondata["forecast"]["riskMessage"]

        except Exception as error:
            _LOGGER.error(
                "Unable to fetch current risk from Brandrisk Ute %s", str(error)
            )
            self.available = False

        if self.use_forecast:
            try:
                # Fetch forecast
                response = urlopen(
                    self.URL_BASE + self.URL_FORECAST.format(lat=self.lat, lon=self.lon)
                )
                data = response.read().decode("utf-8")
                jsondata = json.loads(data)

                for index, element in enumerate(jsondata):
                    if self.verbose:
                        self.forecast.append(element)
                    else:
                        forecast_day = {}
                        forecast_day["date"] = element["date"]
                        forecast_day["riskIndex"] = element["riskIndex"]
                        forecast_day["grassIndex"] = element["grassIndex"]
                        forecast_day["woodIndex"] = element["woodIndex"]
                        forecast_day["riskMessage"] = element["riskMessage"]
                        self.forecast.append(forecast_day)

            except Exception as error:
                _LOGGER.error(
                    "Unable to fetch forecast from Brandrisk Ute %s", str(error)
                )
                self.available = False

        if self.use_prohibition:
            try:
                # Fetch prohibition
                response = urlopen(
                    self.URL_BASE
                    + self.URL_PROHIBITION.format(lat=self.lat, lon=self.lon)
                )
                data = response.read().decode("utf-8")
                jsondata = json.loads(data)
                self.prohibition = jsondata["fireProhibition"]
                self.available = True
            except Exception as error:
                _LOGGER.error(
                    "Unable to fetch prohibition from Brandrisk Ute %s", str(error)
                )
                self.available = False
