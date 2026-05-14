# Changelog

## 0.1.1 - 2026-05-14

- Added `pyproject.toml` with project metadata and lint configuration.
- Bumped integration version from `0.1.0` to `0.1.1`.

## 0.1.0 - 2026-05-14

Initial custom integration release.

- Added Home Assistant custom integration structure under `custom_components/azure_dragon_tts`.
- Added UI setup via config flow and editable options flow.
- Added YAML platform setup fallback for `tts`.
- Added Azure Speech REST synthesis using SSML.
- Added support for direct Azure voice names, including `de-DE-Seraphina:DragonHDLatestNeural`.
- Added modern Home Assistant TTS streaming support via `async_stream_tts_audio`.
- Added configurable language, region, voice, output format, style, rate, and pitch.
- Added German and English config flow translations.
- Added validation for required non-empty configuration values.
- Added Home Assistant friendly error handling for Azure and network failures.
- Added output-format based audio extension detection.
