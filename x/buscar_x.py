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

TERMOS = [
    "superdotação",
    '"Mensa Brasil"',
    '"altas habilidades"',
    "superdotado",
    "superdotada",
    '"dupla excepcionalidade"',
    '"teste de QI"',
    '"alto QI"',
    "Mensa"
]

def buscar_termo(termo, max_scrolls=25):
    q_enc = urllib.parse.quote(termo)
    url = f"https://x.com/search?q={q_enc}&f=live"
    print(f"\n[X.com Busca] Navegando para {url}...", flush=True)
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
                    
                    # Filtro de data: estritamente 2021 a 2026
                    if dt and (dt < "2021-01-01" or dt > "2026-12-31"):
                        continue
                        
                    if u and u not in existentes:
                        existentes.add(u)
                        novos_tweets += 1
                        with open(F_TWEETS_URLS, "a", encoding="utf-8") as f:
                            f.write(f"{u}\t{termo}\t{dt}\t{it.get('usuario')}\t{it.get('texto')}\n")
            except Exception as e:
                print(f"Erro parse: {e}", flush=True)

        print(f"  Scroll {s+1}/{max_scrolls} | Novos tweets relevantes acumulados: {novos_tweets}", flush=True)
        dom_x.js("window.scrollBy(0, 1500);")
        time.sleep(2.5)

    print(f"Fim da busca por '{termo}': +{novos_tweets} tweets mapeados.", flush=True)

def run():
    print("Iniciando varredura automatizada no X.com (2021-2026)...")
    for t in TERMOS:
        try:
            buscar_termo(t, max_scrolls=20)
        except Exception as e:
            print(f"Erro buscando '{t}': {e}", flush=True)

    print("\nVarredura concluída. Drenando fila de tweets para extração completa de respostas e métricas...")
    coletados = coletar_tweets.carregar_coletados()
    if F_TWEETS_URLS.exists():
        urls = [l.split("\t")[0] for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines() if l.strip()]
        pendentes = [u for u in urls if u not in coletados]
        print(f"Total de tweets pendentes para extração detalhada: {len(pendentes)}", flush=True)
        for i, u in enumerate(pendentes, 1):
            print(f"[{i}/{len(pendentes)}] Extraindo tweet e respostas...", flush=True)
            try:
                coletar_tweets.coletar_tweet(u)
            except Exception as e:
                print(f"Erro coletando {u}: {e}", flush=True)

if __name__ == "__main__":
    run()
