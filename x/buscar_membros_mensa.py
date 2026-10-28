import subprocess
import time
import json
import urllib.parse
from pathlib import Path
import dom_x
import coletar_tweets

DADOS = Path("x/dados")
DADOS.mkdir(exist_ok=True)
F_TWEETS_URLS = DADOS / "tweets_urls.tsv"

ANOS = [
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-12-31")
]

TERMOS_MEMBROS = [
    '"membro da Mensa"',
    '"membros da Mensa"',
    '"carteirinha da Mensa"',
    '"passei na Mensa"',
    '"teste da Mensa"',
    '"entrei na Mensa"'
]

def buscar_membros():
    existentes = set()
    if F_TWEETS_URLS.exists():
        for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    print(f"Total atual de tweets no banco: {len(existentes)}")
    novos_total = 0

    for termo in TERMOS_MEMBROS:
        for dt_ini, dt_fim in ANOS:
            ano = dt_ini[:4]
            query = f'{termo} since:{dt_ini} until:{dt_fim}'
            q_enc = urllib.parse.quote(query)
            url = f"https://x.com/search?q={q_enc}&f=top"
            print(f"\n[X Membros Mensa] {ano} | {termo}: {url}", flush=True)
            dom_x.nav(url)
            dom_x.espera(5)

            novos_nesta_busca = 0
            for s in range(8):
                js_extract = """
                (() => {
                    let articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
                    let data = [];
                    for (let art of articles) {
                        let links = Array.from(art.querySelectorAll('a[href*="/status/"]'));
                        let tweetUrl = null;
                        for (let a of links) {
                            if (a.href.includes('/status/') && !a.href.includes('/photo/') && !a.href.includes('/video/')) {
                                tweetUrl = a.href.split('?')[0];
                                break;
                            }
                        }
                        if (tweetUrl) data.push(tweetUrl);
                    }
                    return Array.from(new Set(data)).join('\\n');
                })()
                """
                res = dom_x.js(js_extract)
                if res and res.strip():
                    for u in res.strip().split("\n"):
                        u = u.strip()
                        if u and u not in existentes:
                            existentes.add(u)
                            novos_total += 1
                            novos_nesta_busca += 1
                            with open(F_TWEETS_URLS, "a", encoding="utf-8") as f:
                                f.write(f"{u}\t{termo}\t{ano}\n")
                            print(f"  + Novo tweet: {u}", flush=True)
                dom_x.js("window.scrollBy(0, 800);")
                time.sleep(2)
            print(f"  -> Concluído {termo} ({ano}): {novos_nesta_busca} novos.")

    print(f"\n[Busca Concluída] Total de novos tweets mapeados: {novos_total}")
    if novos_total > 0:
        print("\nIniciando coleta detalhada de conteúdo e threads para os novos tweets...")
        coletar_tweets.processar_novos()

if __name__ == "__main__":
    buscar_membros()
