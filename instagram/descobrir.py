#!/usr/bin/env python3
"""Descobre posts, reels e perfis no Instagram a partir de tags e buscas por palavra-chave.
Grava:
  instagram/dados/posts_urls.tsv     (post_url, tag_ou_termo, descoberto_em)
  instagram/dados/handles_descobertos.tsv (handle, fonte, descoberto_em)
"""
import datetime
import json
import pathlib
import re
import sys
import time
import urllib.parse

IG = pathlib.Path(__file__).parent
sys.path.insert(0, str(IG))
import dom_ig
import termos_ig

F_POSTS = dom_ig.DADOS / "posts_urls.tsv"
F_HANDLES = dom_ig.DADOS / "handles_descobertos.tsv"

JS_EXTRACT = '''(() => {
    const postLinks = Array.from(document.querySelectorAll('a'))
        .map(a => a.href)
        .filter(h => h && (h.includes('/p/') || h.includes('/reel/')));

    const handles = Array.from(document.querySelectorAll('a'))
        .map(a => a.getAttribute('href'))
        .filter(h => h && h.startsWith('/') && !h.includes('/p/') && !h.includes('/reel/') && !h.includes('/explore/') && !h.includes('/stories/') && !h.includes('/direct/'))
        .map(h => h.replace(/\\//g, '').trim())
        .filter(h => h && h.length > 2 && !['about', 'legal', 'help', 'privacy', 'terms', 'developer'].includes(h));

    return JSON.stringify({
        posts: Array.from(new Set(postLinks)),
        handles: Array.from(new Set(handles))
    });
})()'''


def carregar_existentes():
    feitos_posts = set()
    if F_POSTS.exists():
        for line in F_POSTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                partes = line.split("\t")
                feitos_posts.add(partes[0])

    feitos_handles = set()
    if F_HANDLES.exists():
        for line in F_HANDLES.read_text(encoding="utf-8").splitlines():
            if line.strip():
                partes = line.split("\t")
                feitos_handles.add(partes[0])

    return feitos_posts, feitos_handles


def salvar_posts(novos_links, termo):
    agora = datetime.datetime.now().isoformat()
    with open(F_POSTS, "a", encoding="utf-8") as f:
        for link in novos_links:
            f.write(f"{link}\t{termo}\t{agora}\n")


def salvar_handles(novos_handles, fonte):
    agora = datetime.datetime.now().isoformat()
    with open(F_HANDLES, "a", encoding="utf-8") as f:
        for h in novos_handles:
            f.write(f"{h}\t{fonte}\t{agora}\n")


def run():
    vistos_posts, vistos_handles = carregar_existentes()
    print(f"Iniciando descoberta profunda. Já conhecidos: {len(vistos_posts)} posts, {len(vistos_handles)} handles.")

    # Registra handles semente se não existirem
    novos_sementes = [h for h in termos_ig.HANDLES_SEMENTE if h not in vistos_handles]
    if novos_sementes:
        salvar_handles(novos_sementes, "semente")
        vistos_handles.update(novos_sementes)
        print(f"Registrados {len(novos_sementes)} handles semente.")

    # 1. Varredura de tags ampliadas
    for tag in termos_ig.TAGS:
        url = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(tag)}/"
        print(f"Buscando tag #{tag}...", flush=True)
        dom_ig.nav(url)
        time.sleep(3.5)

        for _ in range(3):
            dom_ig.js("window.scrollBy(0, 1000)")
            time.sleep(1.2)

        res = dom_ig.js(JS_EXTRACT)
        dados = {"posts": [], "handles": []}
        try:
            dados = json.loads(res)
        except Exception:
            pass

        novos_p = [l for l in dados.get("posts", []) if l not in vistos_posts]
        if novos_p:
            salvar_posts(novos_p, f"#{tag}")
            vistos_posts.update(novos_p)
            print(f"  -> +{len(novos_p)} posts descobertos", flush=True)

        novos_h = [h for h in dados.get("handles", []) if h not in vistos_handles]
        if novos_h:
            salvar_handles(novos_h, f"tag:{tag}")
            vistos_handles.update(novos_h)
            print(f"  -> +{len(novos_h)} novos perfis descobertos", flush=True)

    # 2. Varredura de palavras-chave ampliadas
    for kw in termos_ig.KEYWORDS:
        url = f"https://www.instagram.com/explore/search/keyword/?q={urllib.parse.quote(kw)}"
        print(f"Buscando keyword '{kw}'...", flush=True)
        dom_ig.nav(url)
        time.sleep(3.5)

        for _ in range(3):
            dom_ig.js("window.scrollBy(0, 1000)")
            time.sleep(1.2)

        res = dom_ig.js(JS_EXTRACT)
        dados = {"posts": [], "handles": []}
        try:
            dados = json.loads(res)
        except Exception:
            pass

        novos_p = [l for l in dados.get("posts", []) if l not in vistos_posts]
        if novos_p:
            salvar_posts(novos_p, kw)
            vistos_posts.update(novos_p)
            print(f"  -> +{len(novos_p)} posts descobertos", flush=True)

        novos_h = [h for h in dados.get("handles", []) if h not in vistos_handles]
        if novos_h:
            salvar_handles(novos_h, f"kw:{kw}")
            vistos_handles.update(novos_h)
            print(f"  -> +{len(novos_h)} novos perfis descobertos", flush=True)

    print(f"Descoberta profunda concluída! Total de posts: {len(vistos_posts)} | Total de perfis: {len(vistos_handles)}.")


if __name__ == "__main__":
    run()
