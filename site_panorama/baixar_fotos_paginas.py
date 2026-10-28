"""Fotos de perfil que faltam, lidas das páginas públicas do TikTok e do YouTube.

TikTok: "avatarLarger" na página do perfil. YouTube: og:image da página do canal.
O Instagram exige login para isso e fica de fora (o site mostra as iniciais).
Uso: python3 -I baixar_fotos_paginas.py <lista_de_avatares.txt> <pasta_bruta>
"""
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
lista = Path(sys.argv[1]).read_text().split()
bruto = Path(sys.argv[2])
bruto.mkdir(exist_ok=True)


def pagina(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"}), timeout=30) as r:
        return r.read().decode("utf-8", "replace")


ok = 0
for av in lista:
    rede, ident = av.split("/", 1)
    pid = "".join(ch for ch in ident if ch.isalnum() or ch in "_.-")
    destino = AQUI / "img/perfis" / f"{pid}.jpg"
    if destino.exists() or rede == "instagram":
        continue
    try:
        if rede == "tiktok":
            m = re.search(r'"avatarLarger":"([^"]+)"', pagina(f"https://www.tiktok.com/@{ident}"))
        else:
            url = f"https://www.youtube.com/{ident}" if ident.startswith("@") else f"https://www.youtube.com/channel/{ident}"
            m = re.search(r'<meta property="og:image" content="([^"]+)"', pagina(url))
        if not m:
            print("sem foto:", av, flush=True)
            continue
        src = m.group(1).encode().decode("unicode_escape").replace("&amp;", "&")
        with urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=30) as r:
            if not r.headers.get("Content-Type", "").startswith("image/"):
                continue
            (bruto / pid).write_bytes(r.read())
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "160",
                        str(bruto / pid), "--out", str(destino)], capture_output=True)
        ok += 1
    except Exception as e:
        print("erro:", av, type(e).__name__, flush=True)
    time.sleep(1.5)
print("novas fotos:", ok, flush=True)
