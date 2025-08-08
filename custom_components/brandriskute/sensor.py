from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

from .const import DOMAIN, CONF_USE_FORECAST, CONF_USE_PROHIBITION, CONF_VERBOSE
from .coordinator import BrandriskCoordinator

ICON = ["mdi:fire-alert", "mdi:pine-tree-fire", "mdi:fire-off"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = BrandriskCoordinator(
        hass,
        entry.data[CONF_LATITUDE],
        entry.data[CONF_LONGITUDE],
        entry.data.get(CONF_USE_FORECAST, True),
        entry.data.get(CONF_USE_PROHIBITION, True),
        entry.data.get(CONF_VERBOSE, True),
    )
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        BrandriskSensor(coordinator, entry.data[CONF_NAME])
    ]

    if entry.data.get(CONF_USE_FORECAST, True):
        sensors.append(BrandriskForecastSensor(coordinator, entry.data[CONF_NAME]))

    if entry.data.get(CONF_USE_PROHIBITION, True):
        sensors.append(BrandriskProhibitionSensor(coordinator, entry.data[CONF_NAME]))

    async_add_entities(sensors)


class BrandriskSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: BrandriskCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_name = name + "_risk"

    @property
    def icon(self):
        if self.coordinator.data["current"]["grassIndex"] > self.coordinator.data["current"]["woodIndex"]:
            return ICON[0]
        else:
            return ICON[1]

    @property
    def native_value(self):
        return self.coordinator.data["state"]

    @property
    def extra_state_attributes(self):
        return self.coordinator.data["current"]


class BrandriskForecastSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: BrandriskCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_name = name + "_forecast"
        self._attr_icon = ICON[1]

    @property
    def native_value(self):
        if self.coordinator.data["forecast"]:
            return self.coordinator.data["forecast"][0]["riskIndex"]
        return None

    @property
    def extra_state_attributes(self):
        return {"forecast": self.coordinator.data["forecast"]}


class BrandriskProhibitionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: BrandriskCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_name = name + "_prohibition"
        self._attr_icon = ICON[2]

    @property
    def native_value(self):
        return self.coordinator.data["prohibition"].get("status")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data["prohibition"]
