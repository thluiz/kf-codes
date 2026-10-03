# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/) where applicable.

## [0.1.0] - 2026-10-03

### Added

- Multihost config: each language file sets its own `baseURL` and `contentDir`, so one build produces `public/pt`, `public/en` and `public/es`, one per domain. hreflang alternates and self-referencing canonical tags come free from this.
- Blowfish theme as a submodule, replacing `hugo-refresh`.
- `mcys` color scheme (`assets/css/schemes/mcys.css`): the Moy Chi Yau Si family palette, gold for dark mode, purple for light.
- EN/ES placeholder for `2022-conhecendo-o-elefante`, to check the language switcher and hreflang before translating anything for real.
- README and this changelog.

### Changed

- Content split from one tree using Hugo's `.en.md` suffix into three separate trees (`content/pt`, `content/en`, `content/es`). `about`, `credits` and `3-registros-da-existencia` already had English text and moved into both. The rest (Elefante, Fuscas, Etimologia, Como Conseguir Mais Tempo, Inversão de Valores) stayed PT-only since no translation exists yet.
- Project-level shortcodes (`sifu`, `instituto`, `ipanema`, `mdbg`, `sitaigung`) didn't need any change; they're plain link shortcodes, no theme dependency.
- Config moved from `config.yaml` to `config/_default/` (hugo.toml, per-language files, params.toml, menus).

### Removed

- `hugo-refresh` and its `layouts/_default/baseof.html` override, incompatible with Blowfish.
- `example_content/` theme boilerplate, including the stray `.ru.md` example.

### Infrastructure

- Hugo upgraded to 0.167.0 (extended) for Blowfish compatibility.
