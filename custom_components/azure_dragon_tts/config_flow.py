"""Config flow for Azure Dragon TTS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LANGUAGE, CONF_NAME
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_OUTPUT_FORMAT,
    CONF_PITCH,
    CONF_RATE,
    CONF_REGION,
    CONF_STYLE,
    CONF_VOICE,
    DEFAULT_LANGUAGE,
    DEFAULT_NAME,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PITCH,
    DEFAULT_RATE,
    DEFAULT_REGION,
    DEFAULT_VOICE,
    DOMAIN,
)

_REQUIRED_STRING = vol.All(cv.string, vol.Strip, vol.Length(min=1))
_OPTIONAL_STRING = vol.All(cv.string, vol.Strip)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build a schema with optional defaults."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_LANGUAGE, default=defaults.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_REGION, default=defaults.get(CONF_REGION, DEFAULT_REGION)
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_VOICE, default=defaults.get(CONF_VOICE, DEFAULT_VOICE)
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_OUTPUT_FORMAT,
                default=defaults.get(CONF_OUTPUT_FORMAT, DEFAULT_OUTPUT_FORMAT),
            ): _REQUIRED_STRING,
            vol.Optional(CONF_STYLE, default=defaults.get(CONF_STYLE, "")): _OPTIONAL_STRING,
            vol.Optional(
                CONF_RATE, default=defaults.get(CONF_RATE, DEFAULT_RATE)
            ): _REQUIRED_STRING,
            vol.Optional(
                CONF_PITCH, default=defaults.get(CONF_PITCH, DEFAULT_PITCH)
            ): _REQUIRED_STRING,
        }
    )


def _clean_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Drop empty optional values."""
    cleaned = dict(user_input)
    if not cleaned.get(CONF_STYLE):
        cleaned.pop(CONF_STYLE, None)
    return cleaned


class AzureDragonTtsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Azure Dragon TTS config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            cleaned = _clean_input(user_input)
            await self.async_set_unique_id(
                f"{cleaned[CONF_REGION]}_{cleaned[CONF_VOICE]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=cleaned.get(CONF_NAME, DEFAULT_NAME), data=cleaned
            )

        return self.async_show_form(step_id="user", data_schema=_schema())

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AzureDragonTtsOptionsFlow:
        """Create the options flow."""
        return AzureDragonTtsOptionsFlow(config_entry)


class AzureDragonTtsOptionsFlow(config_entries.OptionsFlow):
    """Handle Azure Dragon TTS options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage Azure Dragon TTS options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=_clean_input(user_input))

        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))
