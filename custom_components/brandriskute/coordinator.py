import logging
import json
from datetime import timedelta
from urllib.request import urlopen

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

class BrandriskCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, latitude, longitude, use_forecast, use_prohibition, verbose):
        self.hass = hass
        self.lat = latitude
        self.lon = longitude
        self.use_forecast = use_forecast
        self.use_prohibition = use_prohibition
        self.verbose = verbose

        super().__init__(
            hass,
            _LOGGER,
            name="brandrisk",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        result = {}
        base_url = "https://api.msb.se/brandrisk/v2"
        try:
            url = f"{base_url}/CurrentRisk/sv/{self.lat}/{self.lon}"
            response = await self.hass.async_add_executor_job(urlopen, url)
            data = json.loads(response.read().decode("utf-8"))
            forecast = data.get("forecast", {})
            
            result["state"] = forecast.get("riskIndex", "unknown")
            if self.verbose:
                result["current"] = forecast
            else:
                result["current"] = {
                    "date": forecast.get("date"),
                    "riskIndex": forecast.get("riskIndex"),
                    "grassIndex": forecast.get("grassIndex"),
                    "woodIndex": forecast.get("woodIndex"),
                    "riskMessage": forecast.get("riskMessage"),
                }

            if self.use_forecast:
                url = f"{base_url}/RiskDailyForecast/sv/{self.lat}/{self.lon}"
                response = await self.hass.async_add_executor_job(urlopen, url)
                forecast_data = json.loads(response.read().decode("utf-8"))
                result["forecast"] = forecast_data

            if self.use_prohibition:
                url = f"{base_url}/FireProhibition/{self.lat}/{self.lon}"
                response = await self.hass.async_add_executor_job(urlopen, url)
                prohibition_data = json.loads(response.read().decode("utf-8"))
                result["prohibition"] = prohibition_data.get("fireProhibition", {})

            return result

        except Exception as e:
            _LOGGER.error("Brandrisk: Failed to update data: %s", e)
            raise UpdateFailed from e