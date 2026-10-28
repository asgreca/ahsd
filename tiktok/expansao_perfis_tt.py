import subprocess
import time
import json
from pathlib import Path
import dom_tt
import drenar_tt

DADOS = Path("tiktok/dados")
DADOS.mkdir(exist_ok=True)
F_VIDEOS_URLS = DADOS / "tiktok_videos_urls.tsv"

PERFIS_TIKTOK = [
    "jeanalessandrob",
    "altashabilidades.sd",
    "eu.superdotado",
    "vozesneurodivergentes",
    "dra.tamirismariano",
    "luana_braghirolli",
    "sandrahernandes22",
    "psicoklein",
    "febratis",
    "descobertamental",
    "hipertesteoficial",
    "doutormarcone",
    "virando.adulta",
    "souandressa.psi",
    "drarafaellalorrayne",
    "almasdeouro",
    "priscilabcunha",
    "podpeople",
    "enova.film",
    "jhenifervmoura"
]

def varrer_perfil(handle, max_scrolls=6):
    url = f"https://www.tiktok.com/@{handle}"
    print(f"\n[TikTok Perfil] Visitando @{handle} em {url}...", flush=True)
    dom_tt.nav(url)
    dom_tt.espera(6)

    existentes = set()
    if F_VIDEOS_URLS.exists():
        for l in F_VIDEOS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                existentes.add(l.split("\t")[0])

    novos = 0
    for s in range(max_scrolls):
        js_extract = """
        (() => {
            let anchors = Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h.includes('/video/'));
            return JSON.stringify(anchors);
        })()
        """
        res = dom_tt.js(js_extract)
        if res and res.startswith("["):
            try:
                links = json.loads(res)
                for l in links:
                    u = l.split("?")[0]
                    if u not in existentes:
                        existentes.add(u)
                        novos += 1
                        with open(F_VIDEOS_URLS, "a", encoding="utf-8") as f:
                            f.write(f"{u}\tperfil:@{handle}\tperfil\n")
            except Exception as e:
                print(f"Erro parse: {e}", flush=True)

        dom_tt.js("window.scrollBy(0, 1500);")
        time.sleep(2)

    print(f"  -> +{novos} novos vídeos mapeados de @{handle}.", flush=True)
    return novos

def run():
    print("Iniciando varredura profunda dos 20 principais perfis de superdotação no TikTok...", flush=True)
    total_novos = 0
    for h in PERFIS_TIKTOK:
        try:
            total_novos += varrer_perfil(h)
        except Exception as e:
            print(f"Erro em @{h}: {e}", flush=True)

    print(f"\nVarredura de perfis concluída: +{total_novos} novos vídeos mapeados!", flush=True)
    print("Iniciando drenagem, extração de metadados e transcrições Whisper...", flush=True)
    drenar_tt.run()

if __name__ == "__main__":
    run()
