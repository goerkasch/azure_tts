"""Azure Speech TTS platform using direct SSML voice names."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import logging
from typing import Any
from xml.sax.saxutils import escape

import voluptuous as vol

from homeassistant.components.tts import PLATFORM_SCHEMA, TextToSpeechEntity

try:
    from homeassistant.components.tts import TTSAudioRequest, TTSAudioResponse
except ImportError:  # Older HA versions
    TTSAudioRequest = None  # type: ignore[assignment]
    TTSAudioResponse = None  # type: ignore[assignment]

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LANGUAGE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_LANGUAGES = ["de-DE", "en-US", "en-GB"]
SUPPORT_OPTIONS = [CONF_VOICE, CONF_STYLE, CONF_RATE, CONF_PITCH, CONF_OUTPUT_FORMAT]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): cv.string,
        vol.Optional(CONF_REGION, default=DEFAULT_REGION): cv.string,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): cv.string,
        vol.Optional(CONF_OUTPUT_FORMAT, default=DEFAULT_OUTPUT_FORMAT): cv.string,
        vol.Optional(CONF_STYLE): cv.string,
        vol.Optional(CONF_RATE, default=DEFAULT_RATE): cv.string,
        vol.Optional(CONF_PITCH, default=DEFAULT_PITCH): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Azure Dragon TTS from a config entry."""
    config = {**entry.data, **entry.options}
    async_add_entities([AzureDragonTtsEntity(hass, config)])


async def async_setup_platform(
    hass: HomeAssistant, config: dict[str, Any], async_add_entities, discovery_info=None
) -> None:
    """Set up the Azure Dragon TTS platform from YAML."""
    async_add_entities([AzureDragonTtsEntity(hass, config)])


class AzureDragonTtsEntity(TextToSpeechEntity):
    """Azure Speech TTS entity that sends exact SSML to Azure."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self._api_key = config[CONF_API_KEY]
        self._name = config.get(CONF_NAME, DEFAULT_NAME)
        self._language = config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        self._region = config.get(CONF_REGION, DEFAULT_REGION)
        self._voice = config.get(CONF_VOICE, DEFAULT_VOICE)
        self._output_format = config.get(CONF_OUTPUT_FORMAT, DEFAULT_OUTPUT_FORMAT)
        self._style = config.get(CONF_STYLE)
        self._rate = config.get(CONF_RATE, DEFAULT_RATE)
        self._pitch = config.get(CONF_PITCH, DEFAULT_PITCH)
        self._attr_unique_id = f"azure_dragon_tts_{self._region}_{self._voice}"
        self._attr_name = self._name

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._language

    @property
    def supported_options(self) -> list[str]:
        """Return supported options."""
        return SUPPORT_OPTIONS

    @property
    def default_options(self) -> dict[str, Any]:
        """Return default options."""
        options = {
            CONF_VOICE: self._voice,
            CONF_OUTPUT_FORMAT: self._output_format,
            CONF_RATE: self._rate,
            CONF_PITCH: self._pitch,
        }
        if self._style:
            options[CONF_STYLE] = self._style
        return options

    @callback
    def async_get_supported_voices(self, language: str) -> list[str] | None:
        """Return a small set of known voices for the selected language."""
        if language.lower().startswith("de"):
            return [
                "de-DE-Seraphina:DragonHDLatestNeural",
                "de-DE-SeraphinaMultilingualNeural",
                "de-DE-AmalaNeural",
                "de-DE-KatjaNeural",
                "de-DE-ConradNeural",
            ]
        return [self._voice]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ):
        """Generate TTS audio bytes via Azure Speech REST API."""
        audio = await self._synthesize(message, language or self._language, options or {})
        return ("mp3", audio)

    async def async_stream_tts_audio(self, request: TTSAudioRequest):
        """Generate TTS audio for modern HA voice pipelines."""
        if TTSAudioResponse is None:
            raise NotImplementedError

        parts: list[str] = []
        async for chunk in request.message_gen:
            parts.append(chunk)

        audio = await self._synthesize(
            "".join(parts), request.language or self._language, request.options or {}
        )

        async def audio_gen() -> AsyncGenerator[bytes, None]:
            yield audio

        return TTSAudioResponse(extension="mp3", data_gen=audio_gen())

    async def _synthesize(self, message: str, language: str, options: dict[str, Any]) -> bytes:
        """Send SSML to Azure and return audio bytes."""
        voice = options.get(CONF_VOICE, self._voice)
        output_format = options.get(CONF_OUTPUT_FORMAT, self._output_format)
        style = options.get(CONF_STYLE, self._style)
        rate = options.get(CONF_RATE, self._rate)
        pitch = options.get(CONF_PITCH, self._pitch)

        ssml = self._build_ssml(message, language, voice, style, rate, pitch)
        url = f"https://{self._region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Content-Type": "application/ssml+xml; charset=utf-8",
            "X-Microsoft-OutputFormat": output_format,
            "User-Agent": "home-assistant-azure-dragon-tts",
        }

        session = async_get_clientsession(self.hass)
        async with session.post(url, data=ssml.encode("utf-8"), headers=headers) as response:
            body = await response.read()
            if response.status != 200:
                text = body.decode("utf-8", errors="ignore")
                _LOGGER.error("Azure TTS failed: HTTP %s: %s", response.status, text)
                raise RuntimeError(f"Azure TTS failed: HTTP {response.status}: {text}")
            return body

    @staticmethod
    def _build_ssml(
        message: str,
        language: str,
        voice: str,
        style: str | None,
        rate: str,
        pitch: str,
    ) -> str:
        """Build SSML accepted by Azure Speech."""
        text = escape(message)
        voice_escaped = escape(voice, {'"': "&quot;"})
        lang_escaped = escape(language, {'"': "&quot;"})
        rate_escaped = escape(rate, {'"': "&quot;"})
        pitch_escaped = escape(pitch, {'"': "&quot;"})

        inner = f'<prosody rate="{rate_escaped}" pitch="{pitch_escaped}">{text}</prosody>'
        if style:
            style_escaped = escape(style, {'"': "&quot;"})
            inner = f'<mstts:express-as style="{style_escaped}">{inner}</mstts:express-as>'

        return (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            f'xml:lang="{lang_escaped}">'
            f'<voice name="{voice_escaped}">'
            f"{inner}"
            "</voice>"
            "</speak>"
        )
