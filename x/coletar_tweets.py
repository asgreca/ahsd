import subprocess
import time
import json
import re
import datetime
from pathlib import Path
import dom_x

DADOS = Path("x/dados")
DADOS.mkdir(exist_ok=True)
F_TWEETS_URLS = DADOS / "tweets_urls.tsv"
F_TWEETS = DADOS / "x_tweets.jsonl"
F_RESPOSTAS = DADOS / "x_respostas.jsonl"
F_IGNORADOS = DADOS / "x_tweets_ignorados.jsonl"

def carregar_coletados():
    coletados = set()
    if F_TWEETS.exists():
        with open(F_TWEETS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        d = json.loads(l)
                        coletados.add(d.get("url"))
                    except:
                        pass
    if F_IGNORADOS.exists():
        with open(F_IGNORADOS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        d = json.loads(l)
                        coletados.add(d.get("url"))
                    except:
                        pass
    return coletados

JS_EXPANDIR = """
(() => {
    // Tenta clicar em 'Show more replies' ou botões de expansão
    let buttons = Array.from(document.querySelectorAll('div[role="button"], button'));
    for (let b of buttons) {
        let t = b.innerText.toLowerCase();
        if (t.includes('show more replies') || t.includes('mostrar mais') || t.includes('show replies')) {
            b.click();
        }
    }
})()
"""

JS_EXTRAIR = """
(() => {
    let articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
    if (!articles.length) {
        return JSON.stringify({ erro: 'SEM_TWEETS' });
    }

    // O primeiro artigo costuma ser o tweet principal
    let mainArt = articles[0];
    let timeEl = mainArt.querySelector('time');
    let datetime = timeEl ? timeEl.getAttribute('datetime') : null;
    
    // Autor
    let userEl = mainArt.querySelector('div[data-testid="User-Name"]');
    let userText = userEl ? userEl.innerText.replace(/\\n/g, ' ') : '';
    
    // Texto
    let textEl = mainArt.querySelector('div[data-testid="tweetText"]');
    let text = textEl ? textEl.innerText : '';

    // Métricas (reply, retweet, like)
    let replyEl = mainArt.querySelector('div[data-testid="reply"]');
    let retweetEl = mainArt.querySelector('div[data-testid="retweet"]');
    let likeEl = mainArt.querySelector('div[data-testid="like"]');
    
    let parseNum = (el) => {
        if (!el) return 0;
        let t = el.innerText.trim();
        if (!t) return 0;
        if (t.includes('K') || t.includes('mil')) return Math.round(parseFloat(t.replace(',', '.')) * 1000);
        if (t.includes('M')) return Math.round(parseFloat(t.replace(',', '.')) * 1000000);
        return parseInt(t.replace(/\\D/g, '')) || 0;
    };

    let metrics = {
        respostas: parseNum(replyEl),
        retweets: parseNum(retweetEl),
        curtidas: parseNum(likeEl)
    };

    let hasVideo = !!mainArt.querySelector('div[data-testid="videoPlayer"], video');

    // Respostas / comentários (artigos seguintes)
    let replies = [];
    for (let i = 1; i < articles.length; i++) {
        let rArt = articles[i];
        let rTime = rArt.querySelector('time');
        let rDt = rTime ? rTime.getAttribute('datetime') : null;
        let rUser = rArt.querySelector('div[data-testid="User-Name"]');
        let rTxt = rArt.querySelector('div[data-testid="tweetText"]');
        let rLike = rArt.querySelector('div[data-testid="like"]');
        
        if (rTxt) {
            replies.push({
                datetime: rDt,
                usuario: rUser ? rUser.innerText.replace(/\\n/g, ' ') : '',
                texto: rTxt.innerText,
                curtidas: parseNum(rLike)
            });
        }
    }

    return JSON.stringify({
        datetime: datetime,
        usuario: userText,
        texto: text,
        metricas: metrics,
        has_video: hasVideo,
        num_respostas_coletadas: replies.length,
        respostas: replies
    });
})()
"""

def coletar_tweet(url):
    print(f"Coletando tweet: {url}...", flush=True)
    dom_x.nav(url)
    dom_x.espera(5)

    # Rola e tenta expandir respostas
    for _ in range(3):
        dom_x.js(JS_EXPANDIR)
        dom_x.js("window.scrollBy(0, 1000);")
        time.sleep(1.5)

    res = dom_x.js(JS_EXTRAIR)
    if not res or not res.startswith("{"):
        print(f"  -> Falha ao extrair tweet {url}", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "motivo": "extração_vazia"}, ensure_ascii=False) + "\n")
        return None

    data = json.loads(res)
    if data.get("erro"):
        print(f"  -> Erro retornado: {data.get('erro')}", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "motivo": data.get("erro")}, ensure_ascii=False) + "\n")
        return None

    dt = data.get("datetime")
    if dt and dt < "2021-01-01":
        print(f"  -> Fora do período ({dt} < 2021-01-01). Ignorando.", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "datetime": dt, "motivo": "fora_periodo_2021_2026"}, ensure_ascii=False) + "\n")
        return None

    # Salva tweet principal
    respostas = data.pop("respostas", [])
    data["url"] = url
    data["coletado_em"] = datetime.datetime.now().isoformat()

    with open(F_TWEETS, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # Salva respostas em arquivo separado
    if respostas:
        with open(F_RESPOSTAS, "a", encoding="utf-8") as f:
            for r in respostas:
                r["tweet_url"] = url
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  -> Sucesso: {data.get('metricas')} | Respostas coletadas: {len(respostas)}", flush=True)
    return data
