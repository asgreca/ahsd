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

TERMOS = [
    "superdotação",
    '"altas habilidades"',
    '"Mensa Brasil"',
    '"dupla excepcionalidade"',
    "superdotado",
    '"teste de QI"',
    '"alto QI"'
]

def buscar_ano_termo(termo, dt_ini, dt_fim, modo="top", max_scrolls=12):
    query = f'{termo} since:{dt_ini} until:{dt_fim}'
    q_enc = urllib.parse.quote(query)
    url = f"https://x.com/search?q={q_enc}&f={modo}"
    print(f"\n[X.com Busca Anual] {dt_ini[:4]} | {termo} ({modo}): {url}", flush=True)
    dom_x.nav(url)
    dom_x.espera(6)

    existentes = set()
    if F_TWEETS_URLS.exists():
        for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    novos_tweets = 0
    for s in range(max_scrolls):
        js_extract = """
        (() => {
            let articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
            let data = [];
            for (let art of articles) {
                let timeEl = art.querySelector('time');
                let datetime = timeEl ? timeEl.getAttribute('datetime') : null;
                let links = Array.from(art.querySelectorAll('a[href*="/status/"]'));
                let tweetUrl = null;
                for (let a of links) {
                    if (a.href.includes('/status/') && !a.href.includes('/photo/') && !a.href.includes('/video/')) {
                        tweetUrl = a.href.split('?')[0];
                        break;
                    }
                }
                let userEl = art.querySelector('div[data-testid="User-Name"]');
                let userText = userEl ? userEl.innerText.replace(/\\n/g, ' ') : '';
                let textEl = art.querySelector('div[data-testid="tweetText"]');
                let text = textEl ? textEl.innerText.replace(/\\n/g, ' ') : '';
                
                if (tweetUrl) {
                    data.push({
                        url: tweetUrl,
                        datetime: datetime,
                        usuario: userText,
                        texto: text
                    });
                }
            }
            return JSON.stringify(data);
        })()
        """
        res = dom_x.js(js_extract)
        if res and res.startswith("["):
            try:
                itens = json.loads(res)
                for it in itens:
                    u = it.get("url")
                    dt = it.get("datetime")
                    
                    if dt and (dt < "2021-01-01" or dt > "2026-12-31"):
                        continue
                        
                    if u and u not in existentes:
                        existentes.add(u)
                        novos_tweets += 1
                        with open(F_TWEETS_URLS, "a", encoding="utf-8") as f:
                            f.write(f"{u}\t{termo}:{dt_ini[:4]}\t{dt}\t{it.get('usuario')}\t{it.get('texto')}\n")
            except Exception as e:
                print(f"Erro parse: {e}", flush=True)

        dom_x.js("window.scrollBy(0, 1500);")
        time.sleep(2.5)

    print(f"  -> Concluído {dt_ini[:4]} '{termo}': +{novos_tweets} tweets mapeados.", flush=True)

def run():
    print("Iniciando varredura anual exaustiva no X.com (2021 a 2026)...", flush=True)
    for dt_ini, dt_fim in ANOS:
        ano = dt_ini[:4]
        print(f"\n================ ANO {ano} ================", flush=True)
        for t in TERMOS:
            try:
                buscar_ano_termo(t, dt_ini, dt_fim, modo="top", max_scrolls=10)
            except Exception as e:
                print(f"Erro em {ano} - {t}: {e}", flush=True)

    print("\nVarredura anual concluída! Drenando fila para coleta completa de respostas e métricas...", flush=True)
    coletados = coletar_tweets.carregar_coletados()
    if F_TWEETS_URLS.exists():
        urls = [l.split("\t")[0] for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines() if l.strip()]
        pendentes = [u for u in urls if u not in coletados]
        print(f"Total de novos tweets pendentes para extração detalhada: {len(pendentes)}", flush=True)
        for i, u in enumerate(pendentes, 1):
            print(f"[{i}/{len(pendentes)}] Extraindo tweet e respostas...", flush=True)
            try:
                coletar_tweets.coletar_tweet(u)
            except Exception as e:
                print(f"Erro coletando {u}: {e}", flush=True)

if __name__ == "__main__":
    run()
