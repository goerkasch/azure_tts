"""Azure Speech TTS platform using direct SSML voice names."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import logging
from typing import Any
from xml.sax.saxutils import escape

from aiohttp import ClientError
import voluptuous as vol

from homeassistant.components.tts import PLATFORM_SCHEMA, TextToSpeechEntity

try:
    from homeassistant.components.tts import Voice
except ImportError:  # Older HA versions
    Voice = None  # type: ignore[assignment]

try:
    from homeassistant.components.tts import TTSAudioRequest, TTSAudioResponse
except ImportError:  # Older HA versions
    TTSAudioRequest = None  # type: ignore[assignment]
    TTSAudioResponse = None  # type: ignore[assignment]

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LANGUAGE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import AzureTtsError, async_get_voices
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
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_LANGUAGES = ["de-DE", "en-US", "en-GB"]
SUPPORT_OPTIONS = [CONF_VOICE, CONF_STYLE, CONF_RATE, CONF_PITCH, CONF_OUTPUT_FORMAT]
OUTPUT_FORMAT_EXTENSIONS = {
    "mp3": "mp3",
    "opus": "opus",
    "webm": "webm",
    "ogg": "ogg",
    "riff": "wav",
    "wav": "wav",
}

_REQUIRED_STRING = vol.All(cv.string, vol.Strip, vol.Length(min=1))
_OPTIONAL_STRING = vol.All(cv.string, vol.Strip)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): _REQUIRED_STRING,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): _REQUIRED_STRING,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): _REQUIRED_STRING,
        vol.Optional(CONF_REGION, default=DEFAULT_REGION): _REQUIRED_STRING,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): _REQUIRED_STRING,
        vol.Optional(CONF_OUTPUT_FORMAT, default=DEFAULT_OUTPUT_FORMAT): _REQUIRED_STRING,
        vol.Optional(CONF_STYLE): _OPTIONAL_STRING,
        vol.Optional(CONF_RATE, default=DEFAULT_RATE): _REQUIRED_STRING,
        vol.Optional(CONF_PITCH, default=DEFAULT_PITCH): _REQUIRED_STRING,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Azure Dragon TTS from a config entry."""
    config = {**entry.data, **entry.options}
    entity = AzureDragonTtsEntity(hass, config)
    await entity.async_load_voices()
    async_add_entities([entity])


async def async_setup_platform(
    hass: HomeAssistant, config: dict[str, Any], async_add_entities, discovery_info=None
) -> None:
    """Set up the Azure Dragon TTS platform from YAML."""
    entity = AzureDragonTtsEntity(hass, config)
    await entity.async_load_voices()
    async_add_entities([entity])


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
        self._style = config.get(CONF_STYLE) or None
        self._rate = config.get(CONF_RATE, DEFAULT_RATE)
        self._pitch = config.get(CONF_PITCH, DEFAULT_PITCH)
        self._voices: list[dict[str, Any]] = []
        self._languages = SUPPORT_LANGUAGES
        self._attr_unique_id = f"azure_dragon_tts_{self._region}_{self._voice}"
        self._attr_name = self._name

    async def async_load_voices(self) -> None:
        """Load available voices from Azure for Home Assistant voice dropdowns."""
        try:
            self._voices = await async_get_voices(self.hass, self._api_key, self._region)
        except AzureTtsError as err:
            _LOGGER.warning("Could not load Azure voice list: %s", err)
            return

        languages = {
            str(voice["Locale"])
            for voice in self._voices
            if voice.get("Locale")
        }
        languages.add(self._language)
        self._languages = sorted(languages)

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return self._languages

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
    def async_get_supported_voices(self, language: str):
        """Return Azure voices for the selected language."""
        if not self._voices:
            return [_voice_item(self._voice, self._voice)]

        language = (language or "").lower()
        voices = [
            _voice_item(str(voice["ShortName"]), _voice_label(voice))
            for voice in self._voices
            if _voice_matches_language(voice, language)
        ]
        return voices or [_voice_item(self._voice, self._voice)]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ):
        """Generate TTS audio bytes via Azure Speech REST API."""
        options = options or {}
        output_format = options.get(CONF_OUTPUT_FORMAT, self._output_format)
        audio = await self._synthesize(message, language or self._language, options)
        return (_audio_extension(output_format), audio)

    async def async_stream_tts_audio(self, request: TTSAudioRequest):
        """Generate TTS audio for modern HA voice pipelines."""
        if TTSAudioResponse is None:
            raise NotImplementedError

        parts: list[str] = []
        async for chunk in request.message_gen:
            parts.append(chunk)

        options = request.options or {}
        output_format = options.get(CONF_OUTPUT_FORMAT, self._output_format)
        audio = await self._synthesize("".join(parts), request.language or self._language, options)

        async def audio_gen() -> AsyncGenerator[bytes, None]:
            yield audio

        return TTSAudioResponse(extension=_audio_extension(output_format), data_gen=audio_gen())

    async def _synthesize(self, message: str, language: str, options: dict[str, Any]) -> bytes:
        """Send SSML to Azure and return audio bytes."""
        voice = options.get(CONF_VOICE, self._voice)
        output_format = options.get(CONF_OUTPUT_FORMAT, self._output_format)
        style = options.get(CONF_STYLE, self._style)
        rate = options.get(CONF_RATE, self._rate)
        pitch = options.get(CONF_PITCH, self._pitch)

        message = message.strip()
        if not message:
            raise HomeAssistantError("Azure TTS received an empty message")

        ssml = self._build_ssml(message, language, voice, style, rate, pitch)
        url = f"https://{self._region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Content-Type": "application/ssml+xml; charset=utf-8",
            "X-Microsoft-OutputFormat": output_format,
            "User-Agent": USER_AGENT,
        }

        session = async_get_clientsession(self.hass)
        try:
            async with session.post(
                url, data=ssml.encode("utf-8"), headers=headers
            ) as response:
                body = await response.read()
                if response.status != 200:
                    text = body.decode("utf-8", errors="ignore").strip()
                    _LOGGER.error("Azure TTS failed: HTTP %s: %s", response.status, text)
                    raise HomeAssistantError(
                        f"Azure TTS failed with HTTP {response.status}: {text}"
                    )
                if not body:
                    raise HomeAssistantError("Azure TTS returned an empty audio response")
                return body
        except ClientError as err:
            raise HomeAssistantError(f"Could not connect to Azure TTS: {err}") from err

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


def _audio_extension(output_format: str) -> str:
    """Return the Home Assistant audio extension for an Azure output format."""
    output_format = output_format.lower()
    for marker, extension in OUTPUT_FORMAT_EXTENSIONS.items():
        if marker in output_format:
            return extension
    return "mp3"


def _voice_matches_language(voice: dict[str, Any], language: str) -> bool:
    """Return if an Azure voice matches a Home Assistant language tag."""
    if not language:
        return True

    locale = str(voice.get("Locale", "")).lower()
    if locale == language:
        return True

    return locale.split("-", 1)[0] == language.split("-", 1)[0]


def _voice_label(voice: dict[str, Any]) -> str:
    """Return a readable voice label for Home Assistant Assist."""
    short_name = str(voice["ShortName"])
    locale = str(voice.get("Locale", ""))
    local_name = str(voice.get("LocalName") or voice.get("DisplayName") or short_name)
    gender = str(voice.get("Gender", ""))

    parts = [short_name]
    if locale:
        parts.append(locale)
    if gender:
        parts.append(gender)
    if local_name != short_name:
        parts.append(local_name)
    return " - ".join(parts)


def _voice_item(voice_id: str, name: str):
    """Return a modern HA Voice object, or a string for older HA versions."""
    if Voice is None:
        return voice_id
    return Voice(voice_id=voice_id, name=name)
