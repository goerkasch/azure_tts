# Azure Dragon TTS for Home Assistant

Custom integration to use Azure Speech text-to-speech voices, including direct SSML voice names such as `de-DE-Seraphina:DragonHDLatestNeural`, in Home Assistant.

## HACS

If you install this repository as a HACS custom repository, add it as type `Integration`:

```text
https://github.com/goerkasch/azure_tts
```

After installation, restart Home Assistant and add the integration from:

```text
Settings > Devices & services > Add integration > Azure Dragon TTS
```

For updates, use GitHub releases such as `v0.4.2`. HACS can install the default branch, but without a GitHub release it may show the latest commit hash as the version, for example `de0cac5`, instead of a valid release version.

## Manual installation

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

When you configure the integration through the UI, the integration loads the available voices from Azure and shows them in a dropdown. The list depends on the Azure Speech region and key you enter.
The UI also provides dropdowns for language, Azure region, and output format. The voice list is filtered by the selected language.

Supported UI language presets:

```text
de-DE, en-US, en-GB, fr-FR, es-ES, it-IT, nl-NL, pl-PL
```

Supported UI output format presets include MP3, Opus, and RIFF PCM formats. Existing custom YAML values are still accepted.

### Voice tuning

The integration supports three optional voice tuning fields:

- `style`: Azure speaking style, for example cheerful, sad, friendly, or newscast.
- `rate`: Speaking speed. Use values such as `0%`, `+10%`, `-10%`, `+25%`, or `-25%`.
- `pitch`: Speaking pitch. Use values such as `0%`, `+5%`, `-5%`, `+10%`, or `-10%`.

In the UI, `style` is available as a dropdown. Choose `none` to disable Azure speaking styles.

Recommended stable defaults:

```text
style: none
rate: 0%
pitch: 0%
```

Available style values:

```text
amazed
amused
angry
annoyed
anxious
appreciative
calm
cautious
concerned
confident
confused
curious
defeated
defensive
defiant
determined
disappointed
disgusted
doubtful
ecstatic
encouraging
excited
fast
fearful
frustrated
happy
hesitant
hurt
impatient
impressed
intrigued
joking
laughing
optimistic
painful
panicked
panting
pleading
proud
quiet
reassuring
reflective
relieved
remorseful
resigned
sad
sarcastic
secretive
serious
shocked
shouting
shy
skeptical
slow
struggling
surprised
suspicious
sympathetic
terrified
upset
urgent
whispering
```

Not every Azure voice supports every style. If Azure rejects a request, choose `none` first and test again. `rate` and `pitch` are applied with SSML prosody and are generally safer to adjust.

## Assist

The integration exposes Azure voices to Home Assistant Assist. In your voice assistant settings, select:

```text
Text-to-speech: Azure Dragon TTS
Language: your language, for example Deutsch (Deutschland)
Voice: one of the Azure voices for that language
```

If the voice dropdown is empty after an update, restart Home Assistant and reopen the voice assistant settings.

## Testing

You can test the integration from:

```text
Developer tools > Actions
```

Example action:

```yaml
action: tts.speak
target:
  entity_id: tts.azure_dragon_tts
data:
  media_player_entity_id: media_player.your_player
  message: "Hallo, dies ist ein Test mit Azure Dragon TTS."
  language: de-DE
```

## Performance

Azure Speech is a cloud service, so speech output is not instant. Home Assistant has to send the text to Azure, wait for the synthesized audio, and then hand it to the selected media player.

Typical causes of delay:

- Long or dynamic messages, such as full morning briefings.
- Slow response from Azure Speech or the selected Azure region.
- Media players that need a moment before playback starts.
- First playback after a Home Assistant restart.

Tips:

- Use the Azure region closest to your Home Assistant instance.
- Keep frequently used announcements short.
- Prefer MP3 output formats for broad media player compatibility.
- For repeated identical messages, Home Assistant's TTS cache may make later playback faster.

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

### HACS default repository preparation

To prepare this repository for the HACS default repository list, keep the HACS and Hassfest GitHub Actions passing, publish a GitHub release for each version, and add the integration domain `azure_dragon_tts` to the Home Assistant Brands repository.

The GitHub repository also needs a description and topics in the repository settings. Suggested description:

```text
Home Assistant custom integration for Azure Speech text-to-speech.
```

Suggested topics:

```text
home-assistant, hacs, custom-integration, tts, azure, azure-speech
```

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Notes

This integration sends text to the configured Azure Speech resource to generate audio. Azure usage may create costs depending on your Azure subscription and Speech service quota.

Parts of this project were created with AI assistance and reviewed during development.

This project is not affiliated with or endorsed by Microsoft, Azure, or Home Assistant. Azure and Home Assistant names are used only to describe compatibility.
