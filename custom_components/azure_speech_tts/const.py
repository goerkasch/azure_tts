"""Constants for the Azure Speech TTS integration."""

DOMAIN = "azure_speech_tts"

DEFAULT_LANGUAGE = "de-DE"
DEFAULT_NAME = "Azure Speech TTS"
DEFAULT_REGION = "westeurope"
DEFAULT_VOICE = "de-DE-Seraphina:DragonHDLatestNeural"
DEFAULT_OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3"
DEFAULT_STYLE = "none"
DEFAULT_STYLE_GROUP = "Dragon HD / Dragon HD Omni styles"
DEFAULT_RATE = "0%"
DEFAULT_PITCH = "0%"
USER_AGENT = "home-assistant-azure-speech-tts"

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

AZURE_NEURAL_STYLES = [
    "advertisement-upbeat",
    "advertisement_upbeat",
    "affectionate",
    "assistant",
    "chat",
    "cheerful",
    "customerservice",
    "depressed",
    "disgruntled",
    "documentary-narration",
    "embarrassed",
    "empathetic",
    "envious",
    "friendly",
    "gentle",
    "hopeful",
    "lyrical",
    "narration-professional",
    "narration-relaxed",
    "newscast",
    "newscast-casual",
    "newscast-formal",
    "poetry-reading",
    "sports_commentary",
    "sports_commentary_excited",
    "unfriendly",
]

DRAGON_HD_STYLES = [
    "amazed",
    "amused",
    "angry",
    "annoyed",
    "anxious",
    "appreciative",
    "calm",
    "cautious",
    "concerned",
    "confident",
    "confused",
    "curious",
    "defeated",
    "defensive",
    "defiant",
    "determined",
    "disappointed",
    "disgusted",
    "doubtful",
    "ecstatic",
    "encouraging",
    "excited",
    "fast",
    "fearful",
    "frustrated",
    "happy",
    "hesitant",
    "hurt",
    "impatient",
    "impressed",
    "intrigued",
    "joking",
    "laughing",
    "optimistic",
    "painful",
    "panicked",
    "panting",
    "pleading",
    "proud",
    "quiet",
    "reassuring",
    "reflective",
    "relieved",
    "remorseful",
    "resigned",
    "sad",
    "sarcastic",
    "secretive",
    "serious",
    "shocked",
    "shouting",
    "shy",
    "skeptical",
    "slow",
    "struggling",
    "surprised",
    "suspicious",
    "sympathetic",
    "terrified",
    "upset",
    "urgent",
    "whispering",
]

DRAGON_HD_FLASH_STYLES = [
    "assassin",
    "captain",
    "cavalier",
    "complaining",
    "comforting",
    "customer-service",
    "cute",
    "debating",
    "game-narrator",
    "geomancer",
    "guilty",
    "live-commercial",
    "lonely",
    "nervous",
    "news",
    "poet",
    "prince",
    "sentimental",
    "sorry",
    "story",
    "strict",
    "tired",
    "voice-assistant",
]

MAI_VOICE_STYLES = [
    "anger",
    "confusion",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "generalconversation",
    "happiness",
    "hope",
    "jealous",
    "joy",
    "learning",
    "media",
    "persuasive",
    "regret",
    "sadness",
    "sales",
    "surprise",
]

STYLE_GROUP_STYLES = {
    "Azure Neural / scenario styles": AZURE_NEURAL_STYLES,
    "Dragon HD / Dragon HD Omni styles": DRAGON_HD_STYLES,
    "Dragon HD Flash styles": DRAGON_HD_FLASH_STYLES,
    "MAI-Voice-1 preview styles": MAI_VOICE_STYLES,
}

SUPPORTED_STYLE_GROUPS = list(STYLE_GROUP_STYLES)

SUPPORTED_STYLES = [
    DEFAULT_STYLE,
    *AZURE_NEURAL_STYLES,
    *DRAGON_HD_STYLES,
    *DRAGON_HD_FLASH_STYLES,
    *MAI_VOICE_STYLES,
]

CONF_REGION = "region"
CONF_VOICE = "voice"
CONF_OUTPUT_FORMAT = "output_format"
CONF_STYLE = "style"
CONF_STYLE_GROUP = "style_group"
CONF_RATE = "rate"
CONF_PITCH = "pitch"
