import subprocess
import time
import json
import urllib.parse
from pathlib import Path
import dom_tt

DADOS = Path("tiktok/dados")
DADOS.mkdir(exist_ok=True)
F_VIDEOS_URLS = DADOS / "tiktok_videos_urls.tsv"

TERMOS_MEMBROS = [
    "membro da mensa",
    "membros da mensa",
    "teste da mensa",
    "passei na mensa",
    "carteirinha da mensa",
    "fiz o teste da mensa"
]

def buscar_membros_tt(max_scrolls=12):
    existentes = set()
    if F_VIDEOS_URLS.exists():
        for l in F_VIDEOS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    print(f"Total atual de vídeos mapeados: {len(existentes)}")
    novos_total = 0

    for termo in TERMOS_MEMBROS:
        q_enc = urllib.parse.quote(termo)
        url = f"https://www.tiktok.com/search?q={q_enc}"
        print(f"\n[TikTok Busca Membros] {termo}: {url}", flush=True)
        dom_tt.nav(url)
        dom_tt.espera(6)

        novos_nesta_busca = 0
        for s in range(max_scrolls):
            js_extract = """
            (() => {
                let anchors = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                let data = [];
                for (let a of anchors) {
                    let href = a.href.split('?')[0];
                    data.push(href);
                }
                return Array.from(new Set(data)).join('\\n');
            })()
            """
            res = dom_tt.js(js_extract)
            if res and res.strip():
                for u in res.strip().split("\n"):
                    u = u.strip()
                    if u and u not in existentes:
                        existentes.add(u)
                        novos_total += 1
                        novos_nesta_busca += 1
                        with open(F_VIDEOS_URLS, "a", encoding="utf-8") as f:
                            f.write(f"{u}\tbusca:{termo}\tbusca_membros\n")
                        print(f"  + Novo vídeo: {u}", flush=True)
            dom_tt.js("window.scrollBy(0, 1200);")
            time.sleep(2)
        print(f"  -> Concluído '{termo}': {novos_nesta_busca} novos vídeos.")

    print(f"\n[Busca TikTok Concluída] Total de novos vídeos de Membros da Mensa adicionados: {novos_total}")

if __name__ == "__main__":
    buscar_membros_tt()
