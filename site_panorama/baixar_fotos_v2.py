"""Fotos de perfil por pessoa (img/perfis/<chave>.jpg), tentando cada rede onde ela atua.

Lê fotos_candidatos.json (gerado por gerar_dados.py) e os links colados em
fotos_manuais.json ("link_da_foto"). Para cada chave sem foto:
reaproveita um arquivo já baixado com o nome do perfil; senão tenta TikTok
(avatarLarger), YouTube (og:image) e, por último, Instagram via unavatar.io.
Uso: python3 -I baixar_fotos_v2.py <pasta_bruta>
"""
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PERFIS = AQUI / "img/perfis"
bruto = Path(sys.argv[1])
bruto.mkdir(exist_ok=True)
cand = json.loads((AQUI / "fotos_candidatos.json").read_text())


def ler(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"}), timeout=30) as r:
        return r.headers.get("Content-Type", ""), r.read()


def salvar(dado, chave):
    (bruto / chave).write_bytes(dado)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "160",
                    str(bruto / chave), "--out", str(PERFIS / f"{chave}.jpg")], capture_output=True)


def tentar(spec):
    rede, ident = spec.split("/", 1)
    if rede == "tiktok":
        _, html = ler(f"https://www.tiktok.com/@{ident}")
        m = re.search(r'"avatarLarger":"([^"]+)"', html.decode("utf-8", "replace"))
    elif rede == "youtube":
        url = f"https://www.youtube.com/{ident}" if ident.startswith("@") else f"https://www.youtube.com/channel/{ident}"
        _, html = ler(url)
        m = re.search(r'<meta property="og:image" content="([^"]+)"', html.decode("utf-8", "replace"))
    elif rede == "instagram":
        tipo, dado = ler(f"https://unavatar.io/instagram/{ident}?fallback=false")
        return dado if tipo.startswith("image/") else None
    else:
        return None
    if not m:
        return None
    tipo, dado = ler(m.group(1).encode().decode("unicode_escape").replace("&amp;", "&"))
    return dado if tipo.startswith("image/") else None


ok = 0
# links colados à mão em fotos_manuais.json têm prioridade
manual = AQUI / "fotos_manuais.json"
if manual.exists():
    for chave, info in json.loads(manual.read_text()).items():
        link = (info.get("link_da_foto") or "").strip()
        if link.startswith("http") and not (PERFIS / f"{chave}.jpg").exists():
            try:
                tipo, dado = ler(link)
                if tipo.startswith("image/"):
                    salvar(dado, chave)
                    ok += 1
                    print("foto manual:", chave, flush=True)
            except Exception as e:
                print("link manual falhou:", chave, type(e).__name__, flush=True)

for chave, specs in cand.items():
    if (PERFIS / f"{chave}.jpg").exists():
        continue
    antigo = next((PERFIS / f"{''.join(ch for ch in s.split('/', 1)[1] if ch.isalnum() or ch in '_.-')}.jpg"
                   for s in specs if (PERFIS / f"{''.join(ch for ch in s.split('/', 1)[1] if ch.isalnum() or ch in '_.-')}.jpg").exists()), None)
    if antigo:
        shutil.copy(antigo, PERFIS / f"{chave}.jpg")
        ok += 1
        continue
    for s in specs:
        try:
            dado = tentar(s)
        except Exception:
            dado = None
        time.sleep(1.5)
        if dado:
            salvar(dado, chave)
            ok += 1
            break
    else:
        print("sem foto:", chave, specs, flush=True)
print("fotos novas:", ok, flush=True)
