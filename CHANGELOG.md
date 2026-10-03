# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/) where applicable.

## [0.2.0] - 2026-10-03

### Added

- Hosting on S3 + CloudFront, one bucket and distribution per domain, with ACM certificates (apex + `www`), OAC and a viewer-request function that redirects `www` and rewrites `/path/` to `index.html`.
- `deploy.ps1`: Hugo build, Pagefind index per site, SHA256 manifest per language, upload only what changed (`aws s3 cp`, never `s3 sync`), delete what disappeared, CloudFront invalidation only when needed.
- Own layouts reproducing Silva's look (Astro Cactus): seal header, card mosaic, post box with TOC, tag cloud, Ctrl+K search, light/dark toggle, absolute-URL language switcher, i18n strings for PT/EN/ES.
- Pagefind search, one index per site.
- Shortcodes ported from Blowfish: `alert`, `mermaid`, `chart`, `gallery`. Libraries load only on pages that use them.
- Code highlight with Chroma classes (github in light mode, dracula in dark) and a copy button.
- `scripts/silvae.py`: republishes posts from Silva with canonical URL pointing there, records the source commit (`silvaeSlug`, `silvaeCommit`), and reports posts that changed in Silva since import. `deploy.ps1` runs the check.
- Códigos/Codes section (`content/pt/codigos`, `content/en/codes`).
- Posts from Silva: Qi Jiguang, 拳無禮讓，棍無兩響, Estamos Velhos Xavier, Confessions of a Millennial in Tech, WebRTC com Phoenix, Space shooter com Phoenix, Silent Ilha, A gentle introduction to dependency injection, Spying (on) Methods with Jest.
- ES `about` page.

### Changed

- The six existing PT articles now carry Silva's revised text, dates and images, with canonical pointing to Silva.
- Slugs aligned with Silva: `etimologia-kung-fu` → `etimologia-do-termo-kung-fu`, `2022-conhecendo-o-elefante` → `conhecendo-o-elefante`.
- Menus: Home, Kung Fu, Códigos/Codes, Sobre, Tags.

### Removed

- Blowfish as the active theme and the `mcys` Blowfish color scheme. The submodule stays as the source for porting components (see README).

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
