"""Config flow for Azure Dragon TTS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LANGUAGE, CONF_NAME
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
import homeassistant.helpers.config_validation as cv

from .api import AzureTtsError, async_get_voices, voice_options
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


def _base_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the schema for connection and synthesis defaults."""
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


def _voice_schema(options: dict[str, str], default_voice: str) -> vol.Schema:
    """Build a voice selection schema."""
    select_options = [
        SelectOptionDict(value=value, label=label) for value, label in options.items()
    ]
    return vol.Schema(
        {
            vol.Required(CONF_VOICE, default=default_voice): SelectSelector(
                SelectSelectorConfig(options=select_options, mode="dropdown")
            ),
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
    _config: dict[str, Any]
    _voice_options: dict[str, str]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._config = _clean_input(user_input)
            try:
                voices = await async_get_voices(
                    self.hass, self._config[CONF_API_KEY], self._config[CONF_REGION]
                )
            except AzureTtsError:
                return self.async_show_form(
                    step_id="user",
                    data_schema=_base_schema(user_input),
                    errors={"base": "cannot_connect"},
                )

            self._voice_options = voice_options(voices, DEFAULT_VOICE)
            return await self.async_step_voice()

        return self.async_show_form(step_id="user", data_schema=_base_schema())

    async def async_step_voice(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle voice selection."""
        if user_input is not None:
            cleaned = {**self._config, **_clean_input(user_input)}
            await self.async_set_unique_id(
                f"{cleaned[CONF_REGION]}_{cleaned[CONF_VOICE]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=cleaned.get(CONF_NAME, DEFAULT_NAME), data=cleaned
            )

        return self.async_show_form(
            step_id="voice",
            data_schema=_voice_schema(self._voice_options, DEFAULT_VOICE),
        )

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
        self._config: dict[str, Any] = {}
        self._voice_options: dict[str, str] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage Azure Dragon TTS options."""
        if user_input is not None:
            self._config = _clean_input(user_input)
            try:
                voices = await async_get_voices(
                    self.hass, self._config[CONF_API_KEY], self._config[CONF_REGION]
                )
            except AzureTtsError:
                return self.async_show_form(
                    step_id="init",
                    data_schema=_base_schema(user_input),
                    errors={"base": "cannot_connect"},
                )

            default_voice = self._config_entry.options.get(
                CONF_VOICE, self._config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
            )
            self._voice_options = voice_options(voices, default_voice)
            return await self.async_step_voice()

        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_base_schema(defaults))

    async def async_step_voice(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage Azure Dragon TTS voice selection."""
        if user_input is not None:
            return self.async_create_entry(
                title="", data={**self._config, **_clean_input(user_input)}
            )

        default_voice = self._config_entry.options.get(
            CONF_VOICE, self._config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
        )
        return self.async_show_form(
            step_id="voice",
            data_schema=_voice_schema(self._voice_options, default_voice),
        )
