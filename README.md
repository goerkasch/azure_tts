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

## HACS

If you install this repository as a HACS custom repository, add it as type `Integration`:

```text
https://github.com/goerkasch/azure_tts
```

For updates, use GitHub releases such as `v0.2.4`. HACS can install the default branch, but without a GitHub release it may show the latest commit hash as the version, for example `de0cac5`, instead of a valid release version.

To prepare this repository for the HACS default repository list, keep the HACS and Hassfest GitHub Actions passing, publish a GitHub release for each version, and add the integration domain `azure_dragon_tts` to the Home Assistant Brands repository.

The GitHub repository also needs a description and topics in the repository settings. Suggested description:

```text
Home Assistant custom integration for Azure Speech text-to-speech.
```

Suggested topics:

```text
home-assistant, hacs, custom-integration, tts, azure, azure-speech
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

When you configure the integration through the UI, the integration loads the available voices from Azure and shows them in a dropdown. The list depends on the Azure Speech region and key you enter.

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

## Troubleshooting

### `Secret azure_speech_key not defined`

If you use the YAML example with:

```yaml
api_key: !secret azure_speech_key
```

Home Assistant expects this entry in your `secrets.yaml` file:

```yaml
azure_speech_key: your_azure_speech_key_here
```

Make sure `secrets.yaml` is in the same config directory as `configuration.yaml`, then restart Home Assistant or reload YAML.

You can also avoid YAML secrets entirely by adding the integration through the UI:

```text
Settings > Devices & services > Add integration > Azure Dragon TTS
```
