#!/usr/bin/env python3
"""Visita perfis descobertos no Instagram para extrair biografia, seguidores e classificar a profissão/tipo de criador.
Também descobre os Reels de cada perfil e adiciona à fila de posts para análise.
Grava:
  instagram/dados/ig_perfis.jsonl
  instagram/dados/posts_urls.tsv (novos reels de cada perfil)
"""
import datetime
import json
import pathlib
import re
import sys
import time

IG = pathlib.Path(__file__).parent
sys.path.insert(0, str(IG))
import dom_ig

F_HANDLES = dom_ig.DADOS / "handles_descobertos.tsv"
F_PERFIS = dom_ig.DADOS / "ig_perfis.jsonl"
F_POSTS = dom_ig.DADOS / "posts_urls.tsv"

JS_PERFIL = r'''(() => {
    const metaDesc = document.querySelector('meta[name="description"]')?.content || '';
    const h2 = document.querySelector('header h2')?.innerText || '';
    const h1 = document.querySelector('header h1')?.innerText || '';
    
    // Bio
    const bioEl = document.querySelector('header section div.-vDIg, header section h1 + div, header section ul + div');
    const bioText = bioEl ? bioEl.innerText : '';

    // Links de reels do perfil
    const links = Array.from(document.querySelectorAll('main a, article a'))
        .map(a => a.href)
        .filter(h => h && (h.includes('/p/') || h.includes('/reel/')));

    return JSON.stringify({
        metaDesc: metaDesc,
        h2: h2,
        nome: h1,
        bio: bioText,
        links: Array.from(new Set(links))
    });
})()'''


def classificar_profissao(bio, nome, handle):
    texto = f"{bio} {nome} {handle}".lower()
    
    if re.search(r"\b(médic[oa]|crm|neurologista|neuropediatra|psiquiatra|pediatra)\b", texto):
        return "medico"
    if re.search(r"\b(psicólog[oa]|crp|neuropsicólog[oa]|psicoterapeuta|terapeuta|psicologia)\b", texto):
        return "psicologo"
    if re.search(r"\b(ator|atriz|apresentador|comediante|humorista|cantor[a]?|artista)\b", texto):
        return "ator_celebridade"
    if re.search(r"\b(professor[a]?|pedagog[oa]|doutor[a]?|mestre|pesquisador[a]?|educador[a]?|educação)\b", texto):
        return "educador_pesquisador"
    if re.search(r"\b(instituto|associação|mensa|conbrasd|ong|sociedade|revista|podcast|portal)\b", texto):
        return "entidade_instituicao"
    if re.search(r"\b(superdotad[oa]|altas habilidades|ahsd|membro mensa|neurodivergente|autista)\b", texto):
        return "superdotado_criador"
    return "outro"


def extrair_metricas_meta(meta_desc):
    # Formato típico: "53K seguidores, 769 seguindo, 543 posts — Mensa Brasil (@mensabrasil) no Instagram: ..."
    seguidores = 0
    posts = 0
    m_seg = re.search(r"([\d.,]+)\s*(?:mil|k|m)?\s*seguidores", meta_desc, re.IGNORECASE)
    if m_seg:
        val_str = m_seg.group(1).replace(".", "").replace(",", ".")
        try:
            val = float(val_str)
            if "m" in m_seg.group(0).lower():
                val *= 1000000
            elif "mil" in m_seg.group(0).lower() or "k" in m_seg.group(0).lower():
                val *= 1000
            seguidores = int(val)
        except Exception:
            pass

    m_post = re.search(r"([\d.,]+)\s*posts", meta_desc, re.IGNORECASE)
    if m_post:
        try:
            posts = int(m_post.group(1).replace(".", ""))
        except Exception:
            pass

    return seguidores, posts


def carregar_feitos():
    feitos = set()
    if F_PERFIS.exists():
        for l in F_PERFIS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    d = json.loads(l)
                    feitos.add(d["handle"].lower())
                except Exception:
                    pass
    return feitos


def carregar_handles():
    handles = []
    vistos = set()
    if F_HANDLES.exists():
        for l in F_HANDLES.read_text(encoding="utf-8").splitlines():
            if l.strip():
                h = l.split("\t")[0].strip().replace("@", "")
                if h and h.lower() not in vistos:
                    vistos.add(h.lower())
                    handles.append(h)
    return handles


def run(limite=None):
    feitos = carregar_feitos()
    todos = carregar_handles()
    fila = [h for h in todos if h.lower() not in feitos]

    print(f"Perfis a visitar: {len(fila)} (já coletados: {len(feitos)})")
    if limite:
        fila = fila[:limite]

    for idx, h in enumerate(fila, 1):
        url = f"https://www.instagram.com/{h}/"
        print(f"[{idx}/{len(fila)}] Visitando @{h}...", flush=True)
        dom_ig.nav(url)
        time.sleep(3)
        for _ in range(2):
            dom_ig.js("window.scrollBy(0, 1200)")
            time.sleep(1.0)

        raw = dom_ig.js(JS_PERFIL)
        try:
            d = json.loads(raw) if raw and raw.startswith("{") else {}
        except Exception as e:
            print(f"  Erro no JSON: {e}")
            d = {}

        meta = d.get("metaDesc", "")
        seguidores, num_posts = extrair_metricas_meta(meta)
        bio = d.get("bio", "")
        nome = d.get("nome", "")
        categoria = classificar_profissao(bio + " " + meta, nome, h)
        links = d.get("links", [])

        rec = {
            "handle": h,
            "url": url,
            "nome": nome,
            "seguidores": seguidores,
            "num_posts": num_posts,
            "bio": bio,
            "meta_description": meta,
            "categoria": categoria,
            "links_encontrados": len(links),
            "coletado_em": datetime.datetime.now().isoformat()
        }

        with open(F_PERFIS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        # Salva novos posts/reels na fila de posts
        if links:
            existentes = set()
            if F_POSTS.exists():
                for l in F_POSTS.read_text(encoding="utf-8").splitlines():
                    if l.strip():
                        existentes.add(l.split("\t")[0])
            novos = [l for l in links if l not in existentes]
            if novos:
                with open(F_POSTS, "a", encoding="utf-8") as fp:
                    for l in novos:
                        fp.write(f"{l}\tperfil:@{h}\t{datetime.datetime.now().isoformat()}\n")
                print(f"  -> Adicionados +{len(novos)} posts do perfil @{h}", flush=True)

        print(f"  -> Categoria: {categoria} | Seguidores: {seguidores} | Bio: {bio[:60]}...", flush=True)
        time.sleep(2)

    print("Visita aos perfis concluída!")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limite=lim)
