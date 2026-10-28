"""Baixa as capas dos vídeos de impacto (YouTube e TikTok) para img/capas.

O claude.ai bloqueia imagens de outros sites, então as capas ficam junto do site.
Uso: python3 -I baixar_capas.py <pasta_bruta>
"""
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
bruto = Path(sys.argv[1])
bruto.mkdir(exist_ok=True)
saida = AQUI / "img/capas"
saida.mkdir(parents=True, exist_ok=True)
D = json.loads((AQUI / "dados.js").read_text()[len("window.DADOS = "):-2])
videos = D["videos_impacto"] + [D["video_mensa"]]


def baixar(url, nome):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        if not r.headers.get("Content-Type", "").startswith("image/"):
            return False
        (bruto / nome).write_bytes(r.read())
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "-Z", "540",
                    str(bruto / nome), "--out", str(saida / f"{nome}.jpg")], capture_output=True)
    return True


for v in videos:
    try:
        if v["rede"] == "YouTube":
            ok = baixar(f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", v["id"])
        elif v["rede"] in ("TikTok", "Instagram"):
            # a página pública traz a capa ("cover" no TikTok, og:image no Instagram)
            with urllib.request.urlopen(urllib.request.Request(v["url"], headers={"User-Agent": UA}), timeout=30) as r:
                pag = r.read().decode("utf-8", "replace")
            m = re.search(r'"cover":"([^"]+)"', pag) or re.search(r'property="og:image" content="([^"]+)"', pag)
            capa = m.group(1).encode().decode("unicode_escape").replace("&amp;", "&") if m else None
            ok = bool(capa) and baixar(capa, v["id"])
        else:
            ok = False
        print(v["rede"], v["id"], "ok" if ok else "sem capa", flush=True)
    except Exception as e:
        print(v["rede"], v["id"], "erro", type(e).__name__, flush=True)
