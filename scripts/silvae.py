"""Posts que vêm do Silva (E:/silva, Astro). O Silva é a fonte: aqui só se republica,
com a URL canônica apontando para lá.

Cada post importado guarda no front matter de onde saiu:
  silvaeSlug:   id do post no Silva (pasta, ou arquivo .md sem a extensão)
  silvaeCommit: último commit do Silva que tocou nesse post no momento da importação

  python scripts/silvae.py check                      # lista os posts que mudaram no Silva desde a importação
  python scripts/silvae.py pull <slug>...             # (re)importa para pt/kungfu
  python scripts/silvae.py pull --to en/codes <slug>  # destino <idioma>/<seção> em content/
  python scripts/silvae.py pull --outdated            # reimporta os desatualizados, cada um no lugar onde já está

Não faz git pull no Silva; o check compara com o que estiver no disco (avisa se o Silva
estiver atrás do remoto).
"""
import glob, json, os, re, shutil, subprocess, sys

SILVA_REPO = "E:/silva"
SILVA_POSTS = f"{SILVA_REPO}/src/content/post"
KF_CONTENT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content")
DEFAULT_TO = "pt/kungfu"


def git(*args):
    return subprocess.check_output(["git", "-C", SILVA_REPO, *args], text=True, encoding="utf-8").strip()


def silva_path(slug):
    """Caminho do post no Silva, relativo ao repo: pasta (bundle) ou arquivo único .md."""
    if os.path.isdir(f"{SILVA_POSTS}/{slug}"):
        return f"src/content/post/{slug}"
    if os.path.isfile(f"{SILVA_POSTS}/{slug}.md"):
        return f"src/content/post/{slug}.md"
    sys.exit(f"post não encontrado no Silva: {slug}")


def last_commit(slug):
    return git("log", "-1", "--format=%H", "--", silva_path(slug))


def split(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.replace("\r\n", "\n"), re.S)
    return m.group(1), m.group(2)


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else None


def nested(fm, parent, key):
    m = re.search(rf"^{parent}:\n((?:[ \t]+.+\n?)+)", fm, re.M)
    mm = m and re.search(rf"^\s+{key}:\s*(.+)$", m.group(1), re.M)
    return mm.group(1).strip() if mm else None


def unq(v):
    return v[1:-1] if v and len(v) > 1 and v[0] == v[-1] and v[0] in "\"'" else v


def q(v):
    return json.dumps(v, ensure_ascii=False)


def imported():
    """{pasta do bundle aqui: (silvaeSlug, silvaeCommit)}, em qualquer idioma/seção."""
    out = {}
    for p in sorted(glob.glob(os.path.join(KF_CONTENT, "*", "*", "*", "index.md"))):
        fm, _ = split(open(p, encoding="utf-8").read())
        slug = unq(field(fm, "silvaeSlug"))
        if slug:
            out[os.path.dirname(p)] = (slug, unq(field(fm, "silvaeCommit")))
    return out


def pull(slug, dst):
    src = os.path.join(SILVA_REPO, silva_path(slug))
    index = f"{src}/index.md" if os.path.isdir(src) else src
    fm, body = split(open(index, encoding="utf-8").read())
    title = unq(field(fm, "title"))
    cover = unq(nested(fm, "coverImage", "src"))
    out = ["---", f"title: {q(title)}", f"date: {q(unq(field(fm, 'publishDate')))}",
           f"description: {q(unq(field(fm, 'description')))}", f"tags: {field(fm, 'tags')}"]
    if cover:
        alt = unq(nested(fm, "coverImage", "alt")) or title
        out += [f"featureimage: {q(cover.removeprefix('./'))}", f"featureimagealt: {q(alt)}"]
    if field(fm, "pinned") == "true":
        out.append("pinned: true")
        if field(fm, "pin_weight"):
            out.append(f"pin_weight: {field(fm, 'pin_weight')}")
    # sources: lista YAML em bloco, copiada como está (o template do post mostra como "Fontes")
    m = re.search(r"^sources:\n((?:[ \t]+.*\n?)+)", fm + "\n", re.M)
    if m:
        out.append("sources:\n" + m.group(1).rstrip("\n"))
    out += [f"canonicalURL: {q(f'https://silva.thluiz.com/posts/{slug}/')}",
            f"silvaeSlug: {q(slug)}", f"silvaeCommit: {q(last_commit(slug))}", "---", ""]
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(dst):
        os.remove(os.path.join(dst, f))
    if os.path.isdir(src):
        for f in os.listdir(src):
            if not f.startswith("index."):
                shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    with open(os.path.join(dst, "index.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + body.lstrip("\n"))
    print(f"pulled {slug} @ {last_commit(slug)[:7]} -> {os.path.relpath(dst, KF_CONTENT)}")


def outdated():
    return {d: (s, c) for d, (s, c) in imported().items() if last_commit(s) != c}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        try:
            git("fetch", "-q", "origin")
            branch = git("rev-parse", "--abbrev-ref", "HEAD")
            behind = git("rev-list", "--count", f"HEAD..origin/{branch}")
            if behind != "0":
                print(f"aviso: E:/silva está {behind} commit(s) atrás do remoto; rode git pull lá antes")
        except subprocess.CalledProcessError:
            print("aviso: não consegui consultar o remoto do Silva; comparando com o disco")
        stale = outdated()
        for d, (s, c) in stale.items():
            print(f"{os.path.relpath(d, KF_CONTENT)}: importado de {c[:7]}, Silva agora em {last_commit(s)[:7]}")
            print("  " + git("log", "--format=%h %ad %s", "--date=short", f"{c}..HEAD", "--", silva_path(s)).replace("\n", "\n  "))
        print(f"{len(stale)} desatualizado(s) de {len(imported())} importado(s)")
        sys.exit(1 if stale else 0)
    elif cmd == "pull":
        args = sys.argv[2:]
        if args == ["--outdated"]:
            for dst, (slug, _) in outdated().items():
                pull(slug, dst)
            return
        to = DEFAULT_TO
        if args[:1] == ["--to"]:
            to, args = args[1], args[2:]
        for slug in args:
            pull(slug.removesuffix(".md"), os.path.join(KF_CONTENT, *to.split("/"), slug.removesuffix(".md")))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
