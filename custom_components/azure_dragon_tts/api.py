"""Azure Speech REST helpers."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ContentTypeError

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import USER_AGENT


class AzureTtsError(HomeAssistantError):
    """Base Azure TTS error."""


async def async_get_voices(
    hass: HomeAssistant, api_key: str, region: str
) -> list[dict[str, Any]]:
    """Fetch available Azure Speech voices for a region."""
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "User-Agent": USER_AGENT,
    }

    session = async_get_clientsession(hass)
    try:
        async with session.get(url, headers=headers) as response:
            body = await response.read()
            if response.status != 200:
                text = body.decode("utf-8", errors="ignore").strip()
                raise AzureTtsError(
                    f"Azure voices list failed with HTTP {response.status}: {text}"
                )
            try:
                voices = await response.json()
            except ContentTypeError as err:
                raise AzureTtsError("Azure voices list returned invalid JSON") from err
    except ClientError as err:
        raise AzureTtsError(f"Could not connect to Azure voices list: {err}") from err

    if not isinstance(voices, list):
        raise AzureTtsError("Azure voices list returned an unexpected response")

    return [voice for voice in voices if isinstance(voice, dict) and voice.get("ShortName")]


def voice_options(voices: list[dict[str, Any]], fallback_voice: str) -> dict[str, str]:
    """Build Home Assistant dropdown options from Azure voice metadata."""
    options: dict[str, str] = {}
    for voice in sorted(
        voices,
        key=lambda item: (
            str(item.get("Locale", "")),
            str(item.get("LocalName") or item.get("DisplayName") or item["ShortName"]),
        ),
    ):
        short_name = str(voice["ShortName"])
        locale = str(voice.get("Locale", ""))
        local_name = str(voice.get("LocalName") or voice.get("DisplayName") or short_name)
        gender = str(voice.get("Gender", ""))

        label_parts = [local_name]
        if locale:
            label_parts.append(locale)
        if gender:
            label_parts.append(gender)
        label_parts.append(short_name)
        options[short_name] = " - ".join(label_parts)

    options.setdefault(fallback_voice, fallback_voice)
    return options
