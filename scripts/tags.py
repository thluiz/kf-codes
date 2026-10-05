"""Tags traduzidas entre os três sites, a partir de data/tags.toml.

  python scripts/tags.py check   # tags fora do dicionário e páginas de tag fora de sincronia (exit 1 se houver)
  python scripts/tags.py sync    # gera/atualiza content/<lang>/tags/<slug>/_index.md com translationKey
  python scripts/tags.py fix     # reescreve as tags dos posts para o nome do dicionário no idioma do post

O translationKey "tag-<chave>" é o que liga /tags/carreira/ (PT) a /tags/career/ (EN) e /tags/carrera/ (ES).
Só se geram páginas para tags usadas em posts publicados (não draft) daquele idioma.
"""
import glob, json, os, re, sys, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
LANGS = ["pt", "en", "es"]
MARK = "generatedBy: scripts/tags.py"


def load():
    with open(os.path.join(ROOT, "data", "tags.toml"), "rb") as f:
        return tomllib.load(f)


def slug(name):
    """Mesmo resultado do urlize do Hugo para os nomes do dicionário (minúsculas, espaço vira hífen, acentos e ideogramas ficam)."""
    s = name.strip().lower().replace(" ", "-")
    return re.sub(r"[^\w\-.]", "", s)


def index(tags, lang):
    """{nome em lang (casefold): chave}"""
    return {v[lang].casefold(): k for k, v in tags.items()}


def translate(name, frm, to, tags=None):
    """Nome da tag em `to`, a partir do nome em `frm`; None se não estiver no dicionário."""
    tags = tags or load()
    key = index(tags, frm).get(name.casefold())
    # O Silva às vezes já escreve a tag em outro idioma (architecture, tests em post EN)
    for lang in LANGS:
        key = key or index(tags, lang).get(name.casefold())
    return tags[key][to] if key else None


def posts(lang):
    for p in sorted(glob.glob(os.path.join(CONTENT, lang, "*", "*", "index.md"))):
        text = open(p, encoding="utf-8").read()
        if re.search(r"^draft:\s*true", text, re.M):
            continue
        yield p, text


def tags_of(text):
    m = re.search(r"^tags:\s*(\[.*\])\s*$", text, re.M)
    return json.loads(m.group(1).replace("'", '"')) if m else []


def wanted(tags):
    """{(lang, slug): (chave, nome)} das páginas de tag que devem existir."""
    out, unknown = {}, []
    for lang in LANGS:
        idx = index(tags, lang)
        for p, text in posts(lang):
            for t in tags_of(text):
                key = idx.get(t.casefold())
                if key:
                    out[(lang, slug(tags[key][lang]))] = (key, tags[key][lang])
                else:
                    unknown.append(f"{os.path.relpath(p, CONTENT)}: tag '{t}' não está no dicionário ({lang})")
    return out, unknown


def render(key, name):
    return f'---\ntitle: {json.dumps(name, ensure_ascii=False)}\ntranslationKey: "tag-{key}"\n{MARK}\n---\n'


def existing():
    """{(lang, slug): caminho} das páginas de tag geradas por este script."""
    out = {}
    for p in glob.glob(os.path.join(CONTENT, "*", "tags", "*", "_index.md")):
        if MARK in open(p, encoding="utf-8").read():
            parts = os.path.normpath(p).split(os.sep)
            out[(parts[-4], parts[-2])] = p
    return out


def check():
    tags = load()
    want, unknown = wanted(tags)
    have = existing()
    problems = list(unknown)
    for (lang, s), (key, name) in want.items():
        p = os.path.join(CONTENT, lang, "tags", s, "_index.md")
        if not os.path.exists(p) or open(p, encoding="utf-8").read() != render(key, name):
            problems.append(f"{lang}/tags/{s}: página de tag ausente ou desatualizada (rode sync)")
    for k in have.keys() - want.keys():
        problems.append(f"{k[0]}/tags/{k[1]}: tag sem posts, página sobrando (rode sync)")
    for line in problems:
        print(line)
    print(f"tags: {len(problems)} problema(s), {len(want)} página(s) de tag")
    sys.exit(1 if problems else 0)


def sync():
    tags = load()
    want, unknown = wanted(tags)
    for (lang, s), (key, name) in want.items():
        p = os.path.join(CONTENT, lang, "tags", s, "_index.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(key, name))
    for k, p in existing().items():
        if k not in want:
            os.remove(p)
            os.rmdir(os.path.dirname(p))
            print(f"removida {k[0]}/tags/{k[1]}")
    for line in unknown:
        print("aviso:", line)
    print(f"{len(want)} página(s) de tag sincronizada(s)")


def fix():
    """Tag escrita em outra grafia ou em outro idioma vira o nome do dicionário no idioma do post."""
    tags = load()
    for lang in LANGS:
        own = index(tags, lang)
        others = {n: k for l in LANGS if l != lang for n, k in index(tags, l).items()}
        for p in sorted(glob.glob(os.path.join(CONTENT, lang, "*", "*", "index.md"))):
            text = open(p, encoding="utf-8").read()
            old = tags_of(text)
            new = []
            for t in old:
                key = own.get(t.casefold()) or others.get(t.casefold())
                new.append(tags[key][lang] if key else t)
                if not key:
                    print(f"aviso: {os.path.relpath(p, CONTENT)}: '{t}' não está no dicionário, mantida")
            if new != old:
                text = re.sub(r"^tags:.*$", "tags: " + json.dumps(new, ensure_ascii=False), text, count=1, flags=re.M)
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text)
                print(f"{os.path.relpath(p, CONTENT)}: {old} -> {new}")


if __name__ == "__main__":
    {"check": check, "sync": sync, "fix": fix}.get(sys.argv[1] if len(sys.argv) > 1 else "check", lambda: sys.exit(__doc__))()
