import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from .const import DOMAIN, CONF_USE_FORECAST, CONF_USE_PROHIBITION, CONF_VERBOSE

class BrandriskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_LATITUDE): float,
                vol.Required(CONF_LONGITUDE): float,
                vol.Optional(CONF_USE_FORECAST, default=True): bool,
                vol.Optional(CONF_USE_PROHIBITION, default=True): bool,
                vol.Optional(CONF_VERBOSE, default=True): bool,
            })
        )
