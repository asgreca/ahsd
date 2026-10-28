import sys
import json
import time
import datetime
from pathlib import Path
import dom_ig

DADOS = Path("instagram/dados")
F_PERFIS = DADOS / "ig_perfis.jsonl"
F_POSTS = DADOS / "posts_urls.tsv"

def visitar(h):
    url = f"https://www.instagram.com/{h}/"
    print(f"Visitando @{h} em {url}...")
    dom_ig.nav(url)
    time.sleep(6)

    # Coleta bio, seguidores e nome
    js_info = """
    (() => {
        let text = document.body ? document.body.innerText : '';
        let header = document.querySelector('header');
        let headerText = header ? header.innerText : '';
        let metaDesc = document.querySelector('meta[name="description"]');
        let desc = metaDesc ? metaDesc.content : '';
        return JSON.stringify({
            header: headerText,
            desc: desc
        });
    })()
    """
    res = dom_ig.js(js_info)
    info = json.loads(res) if res and res.startswith("{") else {}
    
    # Rola e coleta links de posts
    links = set()
    for _ in range(4):
        js_links = """
        (() => {
            let anchors = Array.from(document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]'));
            return JSON.stringify(anchors.map(a => a.href));
        })()
        """
        r = dom_ig.js(js_links)
        if r and r.startswith("["):
            for l in json.loads(r):
                if "/p/" in l or "/reel/" in l:
                    links.add(l.split("?")[0])
        dom_ig.js("window.scrollBy(0, 1000);")
        time.sleep(2)

    rec = {
        "handle": h,
        "url": url,
        "categoria": "entidade",
        "info": info,
        "links_encontrados": len(links),
        "coletado_em": datetime.datetime.now().isoformat()
    }
    with open(F_PERFIS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

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

    print(f"Pronto! Encontrados {len(links)} links.")

if __name__ == "__main__":
    handle = sys.argv[1]
    visitar(handle)
