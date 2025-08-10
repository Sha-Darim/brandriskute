from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (DOMAIN, CONF_USE_FORECAST, CONF_USE_PROHIBITION,CONF_VERBOSE)
from .coordinator import BrandriskCoordinator
PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    coordinator = BrandriskCoordinator(
        hass,
        latitude=entry.data["latitude"],
        longitude=entry.data["longitude"],
        use_forecast=entry.data.get(CONF_USE_FORECAST, True),
        use_prohibition=entry.data.get(CONF_USE_PROHIBITION, True),
        verbose=entry.data.get(CONF_VERBOSE, True),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
