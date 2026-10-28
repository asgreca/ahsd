"""Baixa as fotos públicas de perfil (via unavatar.io) que ainda faltam em img/perfis.

Vai devagar para não estourar o limite do serviço; pode ser rodado de novo.
Uso: python3 -I baixar_fotos.py <lista_de_avatares.txt> <pasta_bruta>
"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
lista = Path(sys.argv[1]).read_text().split()
bruto = Path(sys.argv[2])
bruto.mkdir(exist_ok=True)
(AQUI / "img/perfis").mkdir(parents=True, exist_ok=True)
ok = falha = 0
for av in lista:
    pid = "".join(ch for ch in av.split("/")[-1] if ch.isalnum() or ch in "_.-")
    destino = AQUI / "img/perfis" / f"{pid}.jpg"
    if destino.exists():
        continue
    for tentativa in range(3):
        try:
            req = urllib.request.Request(f"https://unavatar.io/{av}?fallback=false", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                tipo = r.headers.get("Content-Type", "")
                dado = r.read()
            if not tipo.startswith("image/"):
                break
            (bruto / pid).write_bytes(dado)
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "160",
                            str(bruto / pid), "--out", str(destino)], capture_output=True)
            ok += 1
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(30 * (tentativa + 1))
                continue
            break
        except Exception:
            break
    if not destino.exists():
        falha += 1
        print("sem foto:", av, flush=True)
    time.sleep(6)
print(f"ok={ok} falha={falha}", flush=True)
