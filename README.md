# Azure Dragon TTS for Home Assistant

Custom integration to use Azure Speech text-to-speech voices, including direct SSML voice names such as `de-DE-Seraphina:DragonHDLatestNeural`, in Home Assistant.

## Installation

Copy the folder `custom_components/azure_dragon_tts` into your Home Assistant config directory:

```text
<home-assistant-config>/custom_components/azure_dragon_tts
```

Restart Home Assistant, then add the integration from:

```text
Settings > Devices & services > Add integration > Azure Dragon TTS
```

## Configuration

Required:

- Azure Speech key

Useful defaults:

- Region: `westeurope`
- Language: `de-DE`
- Voice: `de-DE-Seraphina:DragonHDLatestNeural`
- Output format: `audio-24khz-48kbitrate-mono-mp3`
- Rate: `0%`
- Pitch: `0%`

## YAML fallback

The integration also keeps YAML platform setup available:

```yaml
tts:
  - platform: azure_dragon_tts
    api_key: !secret azure_speech_key
    region: westeurope
    language: de-DE
    voice: de-DE-Seraphina:DragonHDLatestNeural
    output_format: audio-24khz-48kbitrate-mono-mp3
    rate: 0%
    pitch: 0%
```

After setup, Home Assistant creates a TTS entity that can be used by the regular TTS speak action and Assist pipelines.
