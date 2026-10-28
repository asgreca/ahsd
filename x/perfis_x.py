import subprocess
import time
import json
import datetime
from pathlib import Path
import dom_x
import coletar_tweets

DADOS = Path("x/dados")
DADOS.mkdir(exist_ok=True)
F_TWEETS_URLS = DADOS / "tweets_urls.tsv"

PERFIS = [
    # Institucionais e Especialistas
    "mensabr",
    "alphalumen",
    "visibilidadeahsd",
    "neuroconecta",
    "institutoinclus",
    
    # Celebridades e Membros Públicos
    "FabianaKarla",
    "tainamuller",
    "DrauzioVarella",
    "mayragaiato",
    
    # Portais de Notícias que cobrem superdotação e Mensa
    "g1",
    "uol",
    "folha",
    "estadao",
    "veja",
    "metropoles",
    "bbcbrasil",
    "cnnbrasil",
    "revistagalileu",
    "superinteressan"
]

TERMOS_FILTRO = [
    "mensa", "superdota", "superdotad", "altas habilidades", "dupla excepcionalidade",
    "teste de qi", "alto qi", "prodígio", "prodigio", "ah/sd"
]

def tweet_tem_tema(texto):
    if not texto:
        return False
    t = texto.lower()
    return any(termo in t for termo in TERMOS_FILTRO)

def varrer_perfil(handle, max_scrolls=12):
    url = f"https://x.com/{handle}"
    print(f"\n[Perfil X] Visitando @{handle} em {url}...", flush=True)
    dom_x.nav(url)
    dom_x.espera(5)

    existentes = set()
    if F_TWEETS_URLS.exists():
        for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    encontrados = 0
    for s in range(max_scrolls):
        js_get_tweets = """
        (() => {
            let articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
            let data = [];
            for (let art of articles) {
                let timeEl = art.querySelector('time');
                let dt = timeEl ? timeEl.getAttribute('datetime') : null;
                let textEl = art.querySelector('div[data-testid="tweetText"]');
                let txt = textEl ? textEl.innerText : '';
                let a = art.querySelector('a[href*="/status/"]');
                let link = a ? a.href.split('?')[0] : null;
                if (link && !link.includes('/photo/') && !link.includes('/video/')) {
                    data.push({ url: link, datetime: dt, texto: txt });
                }
            }
            return JSON.stringify(data);
        })()
        """
        res = dom_x.js(js_get_tweets)
        if res and res.startswith("["):
            try:
                itens = json.loads(res)
                for it in itens:
                    u = it.get("url")
                    dt = it.get("datetime")
                    txt = it.get("texto", "")
                    
                    # Filtra data 2021-2026
                    if dt and (dt < "2021-01-01" or dt > "2026-12-31"):
                        continue
                    
                    # Se for perfil institucional da Mensa/AH/SD, pega todos os tweets do período.
                    # Se for portal de notícia ou geral, filtra pelos termos.
                    if handle in ["mensabr", "alphalumen", "visibilidadeahsd"] or tweet_tem_tema(txt):
                        if u and u not in existentes:
                            existentes.add(u)
                            encontrados += 1
                            with open(F_TWEETS_URLS, "a", encoding="utf-8") as f:
                                f.write(f"{u}\tperfil:@{handle}\t{dt}\t{txt.replace(chr(10), ' ')}\n")
            except Exception as e:
                print(f"Erro parse perfil: {e}", flush=True)

        dom_x.js("window.scrollBy(0, 1500);")
        time.sleep(2)

    print(f"  -> Total de tweets relevantes mapeados em @{handle}: {encontrados}", flush=True)
    return encontrados

def run():
    print("Iniciando varredura de perfis no X.com...")
    for h in PERFIS:
        try:
            varrer_perfil(h)
        except Exception as e:
            print(f"Erro ao varrer @{h}: {e}", flush=True)
    print("\nVarredura de perfis concluída. Iniciando coleta detalhada dos tweets mapeados...")

    # Drena fila de tweets
    coletados = coletar_tweets.carregar_coletados()
    if F_TWEETS_URLS.exists():
        urls = [l.split("\t")[0] for l in F_TWEETS_URLS.read_text(encoding="utf-8").splitlines() if l.strip()]
        pendentes = [u for u in urls if u not in coletados]
        print(f"Total de tweets pendentes para extração completa: {len(pendentes)}", flush=True)
        for i, u in enumerate(pendentes, 1):
            print(f"[{i}/{len(pendentes)}] Extraindo tweet...", flush=True)
            try:
                coletar_tweets.coletar_tweet(u)
            except Exception as e:
                print(f"Erro coletando {u}: {e}", flush=True)

if __name__ == "__main__":
    run()
