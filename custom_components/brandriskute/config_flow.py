import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from .const import DOMAIN, CONF_USE_FORECAST, CONF_USE_PROHIBITION, CONF_VERBOSE

class BrandriskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if not user_input[CONF_NAME].strip():
                errors[CONF_NAME] = "invalid_name"
            else:
                existing_names = [
                    entry.data[CONF_NAME]
                    for entry in self._async_current_entries()
                ]
                if user_input[CONF_NAME] in existing_names:
                    errors[CONF_NAME] = "name_exists"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required("latitude"): float,
                vol.Required("longitude"): float,
                vol.Optional("use_forecast", default=True): bool,
                vol.Optional("use_prohibition", default=True): bool,
                vol.Optional("verbose", default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
