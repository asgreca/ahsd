#!/usr/bin/env python3
"""Coleta metadados, legendas, curtidas e comentários de cada post/reel do Instagram.
Grava:
  instagram/dados/ig_posts.jsonl
  instagram/dados/ig_comentarios.jsonl
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

F_URLS = dom_ig.DADOS / "posts_urls.tsv"
F_POSTS = dom_ig.DADOS / "ig_posts.jsonl"
F_COM = dom_ig.DADOS / "ig_comentarios.jsonl"
F_HANDLES = dom_ig.DADOS / "handles_descobertos.tsv"
F_IGNORADOS = dom_ig.DADOS / "ig_posts_ignorados.jsonl"

JS_EXPAND = r'''(() => {
    // Expande comentários principais e respostas em loop
    let iter = 0;
    const maxIter = 12;
    while (iter < maxIter) {
        let clicked = 0;
        const spinner = document.querySelector('svg[aria-label="Carregando..."]');
        if (spinner && spinner.parentElement) {
            spinner.parentElement.click();
            clicked++;
        }
        const replyBtns = Array.from(document.querySelectorAll('div, span, button'))
            .filter(el => /^Ver todas as \d+ respostas|^Ver mais respostas/i.test(el.innerText));
        for (const b of replyBtns.slice(0, 10)) {
            try { b.click(); clicked++; } catch(e){}
        }
        if (clicked === 0) break;
        iter++;
    }
    return iter;
})()'''

JS_POST = r'''(() => {
    const timeEl = document.querySelector('time');
    const datetime = timeEl ? timeEl.getAttribute('datetime') : null;
    
    // Tenta achar autor
    let autor = '';
    const h2 = document.querySelector('header h2 a, header h2 span, header a[role="link"]');
    if (h2) autor = h2.innerText.trim();
    if (!autor) {
        const firstLink = document.querySelector('article header a') || document.querySelector('header a');
        if (firstLink) autor = firstLink.innerText.trim();
    }
    
    // Curtidas
    let curtidasStr = null;
    const likesEl = Array.from(document.querySelectorAll('span, a')).find(el => /curtida|like/i.test(el.innerText));
    if (likesEl) curtidasStr = likesEl.innerText;

    // Vídeo
    const isVideo = !!document.querySelector('video') || location.pathname.includes('/reel/');

    // Legenda: primeiro bloco de texto associado ao autor ou article
    let legenda = '';
    const h1 = document.querySelector('h1');
    if (h1) {
        legenda = h1.innerText;
    } else {
        const article = document.querySelector('article') || document.querySelector('main');
        if (article) {
            legenda = article.innerText.slice(0, 1500);
        }
    }

    // Comentários
    const outCom = [], seen = new Set();
    const times = document.querySelectorAll('main time, article time');
    for (const t of times) {
        let e = t;
        for (let k = 0; k < 8 && e; k++) {
            e = e.parentElement;
            if (e && /Responder|Reply/.test(e.innerText)) break;
        }
        if (!e) continue;
        const L = e.innerText.split('\n').map(s => s.trim()).filter(Boolean);
        if (L.length < 3) continue;
        const u = L[0];
        const i = L.findIndex(s => /curtida|like|^Responder|^Reply/i.test(s));
        const txt = L.slice(2, i < 0 ? L.length : i).join(' ');
        const cm = (L.find(s => /curtida|like/i.test(s)) || '').match(/[\d.]+/);
        const key = u + '|' + txt;
        if (!txt || seen.has(key)) continue;
        seen.add(key);
        const rp = (L.find(s => /Ver todas as \d+ respostas|View all \d+ repl/i.test(s)) || '').match(/\d+/);
        outCom.push({
            u: u,
            quando: t.getAttribute('datetime'),
            txt: txt,
            curt: cm ? parseInt(cm[0].replace(/\./g, '')) : 0,
            respostas: rp ? parseInt(rp[0]) : 0
        });
    }

    return JSON.stringify({
        autor: autor,
        datetime: datetime,
        curtidasStr: curtidasStr,
        isVideo: isVideo,
        legenda: legenda,
        comentarios: outCom
    });
})()'''


def sanitize(obj):
    if isinstance(obj, str):
        return obj.encode("utf-16", "surrogatepass").decode("utf-16", "replace")
    elif isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


def parse_curtidas(curt_str):
    if not curt_str:
        return 0
    m = re.search(r"([\d.,]+)\s*(?:mil|k)?", curt_str, re.IGNORECASE)
    if not m:
        return 0
    val_str = m.group(1).replace(".", "").replace(",", ".")
    try:
        val = float(val_str)
        if "mil" in curt_str.lower() or "k" in curt_str.lower():
            val *= 1000
        return int(val)
    except Exception:
        return 0


def carregar_coletados():
    feitos = set()
    for fp in [F_POSTS, F_IGNORADOS]:
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            d = json.loads(line)
                            feitos.add(d["code"])
                        except Exception:
                            pass
    return feitos


def extrair_code(url):
    m = re.search(r"/(?:p|reel)/([A-Za-z0-9_-]+)/?", url)
    return m.group(1) if m else url


def run(limite=None):
    if not F_URLS.exists():
        print("Arquivo de URLs não encontrado. Execute descobrir.py primeiro.")
        return

    feitos = carregar_coletados()
    with open(F_URLS, "r", encoding="utf-8") as f:
        linhas = [l.strip().split("\t") for l in f if l.strip()]

    fila = []
    for l in linhas:
        url = l[0]
        code = extrair_code(url)
        if code not in feitos:
            fila.append((url, code, l[1] if len(l) > 1 else ""))

    print(f"Total na fila para coleta: {len(fila)} posts.")
    if limite:
        fila = fila[:limite]

    coletados = 0
    for url, code, tag_termo in fila:
        print(f"[{coletados+1}/{len(fila)}] Coletando {code} ({url})...", flush=True)
        dom_ig.nav(url)
        time.sleep(4)
        
        # Expande todos os comentários e respostas
        dom_ig.js(JS_EXPAND)
        time.sleep(2)

        raw = dom_ig.js(JS_POST)
        try:
            d = json.loads(raw) if raw and raw.startswith("{") else {}
        except Exception as e:
            print(f"  Erro ao parsear JS: {e}")
            d = {}

        autor = d.get("autor") or ""
        dt = d.get("datetime")
        legenda = d.get("legenda") or ""
        comentarios = d.get("comentarios") or []
        curt_str = d.get("curtidasStr") or ""
        curtidas = parse_curtidas(curt_str)
        is_video = d.get("isVideo", False)

        # Retry se veio vazio
        if not dt and not legenda and not autor:
            time.sleep(3)
            raw = dom_ig.js(JS_POST)
            try:
                d = json.loads(raw) if raw and raw.startswith("{") else {}
                autor = d.get("autor") or ""
                dt = d.get("datetime")
                legenda = d.get("legenda") or ""
                comentarios = d.get("comentarios") or []
                curt_str = d.get("curtidasStr") or ""
                curtidas = parse_curtidas(curt_str)
                is_video = d.get("isVideo", False)
            except Exception:
                pass
            if not dt and not legenda and not autor:
                print(f"  -> Post {code} inacessível ou vazio, ignorando.")
                with open(F_IGNORADOS, "a", encoding="utf-8") as fi:
                    fi.write(json.dumps({"code": code, "url": url, "motivo": "vazio_ou_inacessivel"}) + "\n")
                continue

        # Filtro estrito de data: 2021 a 2026
        if dt and not ("2021" <= str(dt)[:4] <= "2026"):
            print(f"  -> Ignorado: fora da janela (ano {str(dt)[:4]})")
            with open(F_IGNORADOS, "a", encoding="utf-8") as fi:
                fi.write(json.dumps({"code": code, "url": url, "datetime": str(dt), "motivo": "fora_da_janela"}) + "\n")
            continue

        # Limpa autor e legenda caso tenha vindo sujeira
        if "\n" in autor:
            autor = autor.split("\n")[0].strip()

        if not autor:
            partes = [pt for pt in url.split("/") if pt]
            if "instagram.com" in url:
                idx = partes.index("instagram.com") if "instagram.com" in partes else partes.index("www.instagram.com")
                if len(partes) > idx + 1 and partes[idx+1] not in ["p", "reel"]:
                    autor = partes[idx+1]
            if not autor and legenda:
                first = legenda.split("\n")[0].strip()
                if re.match(r"^[a-zA-Z0-9._]{2,30}$", first):
                    autor = first

        rec_post = {
            "code": code,
            "url": url,
            "autor": autor,
            "datetime": dt,
            "curtidas": curtidas,
            "curtidas_texto": curt_str,
            "is_video": is_video,
            "origem_busca": tag_termo,
            "legenda": legenda,
            "num_comentarios_coletados": len(comentarios),
            "coletado_em": datetime.datetime.now().isoformat()
        }

        rec_post = sanitize(rec_post)
        with open(F_POSTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec_post, ensure_ascii=False) + "\n")

        # Salva comentários
        if comentarios:
            with open(F_COM, "a", encoding="utf-8") as fc:
                for c in comentarios:
                    rec_com = {
                        "post_code": code,
                        "post_autor": autor,
                        "post_datetime": dt,
                        "usuario": c["u"],
                        "data_comentario": c["quando"],
                        "texto": c["txt"],
                        "curtidas": c["curt"],
                        "respostas": c["respostas"]
                    }
                    rec_com = sanitize(rec_com)
                    fc.write(json.dumps(rec_com, ensure_ascii=False) + "\n")

        # Registra novo handle descoberto
        if autor and len(autor) > 1:
            with open(F_HANDLES, "a", encoding="utf-8") as fh:
                fh.write(f"{autor}\tpost:{code}\t{datetime.datetime.now().isoformat()}\n")

        print(f"  -> Autor: @{autor} | Curtidas: {curtidas} | Comentários: {len(comentarios)} | Vídeo: {is_video}", flush=True)
        coletados += 1
        time.sleep(2)

    print(f"Coleta concluída! {coletados} novos posts processados.")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limite=lim)
