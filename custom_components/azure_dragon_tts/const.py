"""Constants for the Azure Dragon TTS integration."""

DOMAIN = "azure_dragon_tts"

DEFAULT_LANGUAGE = "de-DE"
DEFAULT_NAME = "Azure Dragon TTS"
DEFAULT_REGION = "westeurope"
DEFAULT_VOICE = "de-DE-Seraphina:DragonHDLatestNeural"
DEFAULT_OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3"
DEFAULT_RATE = "0%"
DEFAULT_PITCH = "0%"
USER_AGENT = "home-assistant-azure-dragon-tts"

SUPPORTED_LANGUAGES = [
    "de-DE",
    "en-US",
    "en-GB",
    "fr-FR",
    "es-ES",
    "it-IT",
    "nl-NL",
    "pl-PL",
]

SUPPORTED_REGIONS = [
    "australiaeast",
    "brazilsouth",
    "canadacentral",
    "centralindia",
    "centralus",
    "eastasia",
    "eastus",
    "eastus2",
    "francecentral",
    "germanywestcentral",
    "japaneast",
    "koreacentral",
    "northeurope",
    "southcentralus",
    "southeastasia",
    "swedencentral",
    "switzerlandnorth",
    "uksouth",
    "westeurope",
    "westus",
    "westus2",
    "westus3",
]

SUPPORTED_OUTPUT_FORMATS = [
    "audio-16khz-32kbitrate-mono-mp3",
    "audio-16khz-64kbitrate-mono-mp3",
    "audio-24khz-48kbitrate-mono-mp3",
    "audio-24khz-96kbitrate-mono-mp3",
    "audio-48khz-96kbitrate-mono-mp3",
    "audio-48khz-192kbitrate-mono-mp3",
    "ogg-24khz-16bit-mono-opus",
    "riff-16khz-16bit-mono-pcm",
    "riff-24khz-16bit-mono-pcm",
    "riff-48khz-16bit-mono-pcm",
]

CONF_REGION = "region"
CONF_VOICE = "voice"
CONF_OUTPUT_FORMAT = "output_format"
CONF_STYLE = "style"
CONF_RATE = "rate"
CONF_PITCH = "pitch"
