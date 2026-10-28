import subprocess
import time
import json
import urllib.parse
from pathlib import Path
import dom_tt

DADOS = Path("tiktok/dados")
DADOS.mkdir(exist_ok=True)
F_VIDEOS_URLS = DADOS / "tiktok_videos_urls.tsv"

TERMOS = [
    "superdotação",
    "superdotado",
    "altas habilidades",
    "mensa brasil",
    "dupla excepcionalidade",
    "teste de qi",
    "alto qi"
]

def buscar_termo(termo, max_scrolls=15):
    q_enc = urllib.parse.quote(termo)
    url = f"https://www.tiktok.com/search?q={q_enc}"
    print(f"\n[TikTok Busca] Navegando para {url}...", flush=True)
    dom_tt.nav(url)
    dom_tt.espera(6)

    existentes = set()
    if F_VIDEOS_URLS.exists():
        for l in F_VIDEOS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    novos = 0
    for s in range(max_scrolls):
        js_extract = """
        (() => {
            let anchors = Array.from(document.querySelectorAll('a[href*="/video/"]'));
            let data = [];
            for (let a of anchors) {
                let href = a.href.split('?')[0];
                let card = a.closest('[data-e2e*="search"]') || a.parentElement;
                let text = card ? card.innerText.replace(/\\n/g, ' ') : '';
                data.push({
                    url: href,
                    texto: text
                });
            }
            return JSON.stringify(data);
        })()
        """
        res = dom_tt.js(js_extract)
        if res and res.startswith("["):
            try:
                itens = json.loads(res)
                for it in itens:
                    u = it.get("url")
                    if u and u not in existentes:
                        existentes.add(u)
                        novos += 1
                        with open(F_VIDEOS_URLS, "a", encoding="utf-8") as f:
                            f.write(f"{u}\t{termo}\t{it.get('texto')}\n")
            except Exception as e:
                print(f"Erro parse TikTok: {e}", flush=True)

        print(f"  Scroll {s+1}/{max_scrolls} | Novos vídeos mapeados: {novos}", flush=True)
        dom_tt.js("window.scrollBy(0, 1200);")
        time.sleep(2.5)

    print(f"Fim da busca TikTok por '{termo}': +{novos} vídeos.", flush=True)

def run():
    for t in TERMOS:
        buscar_termo(t)

if __name__ == "__main__":
    run()
