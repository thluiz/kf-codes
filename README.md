# Kung Fu Codes

Static site for the Código(s) Kung Fu brand: one Hugo codebase building three independent sites, one per language.

| Language | Domain |
|---|---|
| Portuguese | [codigoskungfu.com](https://codigoskungfu.com) |
| English | [kungfu.codes](https://kungfu.codes) |
| Spanish | [codigoskungfu.eu](https://codigoskungfu.eu) |

## Project history

kungfu.codes started in 2022 as a personal blog about Kung Fu and systems thinking. The domain lapsed and got re-registered in 2026 for a career pivot: Código(s) Kung Fu, aimed at Portuguese and Spanish speaking developers. The old Portuguese articles stayed on the PT site. English is now the brand's main track, and Spanish covers the second market.

## Architecture

### Multihost, not subpaths

Each language sets its own `baseURL` and `contentDir` in `config/_default/languages.*.toml`, which turns on Hugo's multihost mode. One `hugo` build produces three output trees:

```
public/pt/   → codigoskungfu.com
public/en/   → kungfu.codes
public/es/   → codigoskungfu.eu
```

Each tree carries absolute URLs for its own domain. No `/en/` prefix, no client-side language detection.

### Content isn't mirrored

`content/pt/`, `content/en/` and `content/es/` are independent trees, and a page only needs to exist where it's actually written. Hugo links a page to its translations when a matching path shows up in another language directory, and builds the `hreflang` tags from whatever translations it finds. Most untranslated pages carry no placeholder at all; one does right now, noted below.

### Blowfish, via submodule

Same convention as the sibling projects: the theme is a submodule, untouched. Customization lives entirely at the project level, in `assets/css/schemes/mcys.css` (color scheme) and `layouts/shortcodes/` (`sifu`, `instituto`, `ipanema`, `mdbg`, `sitaigung`: small link shortcodes with no theme dependency).

### Color scheme: mcys

The Moy Chi Yau Si family palette (Ghost White, Purple, Gold, Dark Purple, Russian Violet) as Blowfish color tokens. Gold for dark mode, purple for light. Moy Chi Yau Si is a family within the Moy Jo Lei Ou clan.

## Deployment

Each `public/<lang>` folder ships to its own S3 bucket and CloudFront distribution, same as Vox.

## Local development

```sh
git submodule update --init --recursive
hugo server
```

## Current status

Real translations exist for three pages: `about`, `credits`, `3-registros-da-existencia`. The rest of the Kung Fu articles are PT-only. `2022-conhecendo-o-elefante` has EN/ES stubs marked "translation pending", there to prove the multihost and hreflang setup works before anyone writes the real text.
