#!/usr/bin/env python3
"""Baixa o áudio de vídeos/reels do Instagram e transcreve a fala usando Whisper local.
Grava:
  instagram/dados/ig_transcricoes.jsonl
"""
import datetime
import json
import pathlib
import re
import subprocess
import sys
import time

IG = pathlib.Path(__file__).parent
sys.path.insert(0, str(IG))
import dom_ig

DADOS = dom_ig.DADOS
MIDIA = dom_ig.MIDIA
F_POSTS = DADOS / "ig_posts.jsonl"
F_TRANS = DADOS / "ig_transcricoes.jsonl"
MAX_SEG = 600  # máx 10 minutos por vídeo


def carregar_transcritos():
    feitos = set()
    if F_TRANS.exists():
        for l in F_TRANS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    d = json.loads(l)
                    feitos.add(d["code"])
                except Exception:
                    pass
    return feitos


def carregar_elegiveis():
    feitos = carregar_transcritos()
    if not F_POSTS.exists():
        return []

    candidatos = []
    vistos = set()
    for l in F_POSTS.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        try:
            p = json.loads(l)
        except Exception:
            continue
        code = p["code"]
        if code in feitos or code in vistos:
            continue
        vistos.add(code)
        # Filtro estrito: apenas 2021 a 2026
        dt = p.get("datetime")
        if dt and not ("2021" <= dt[:4] <= "2026"):
            continue

        if p.get("is_video"):
            candidatos.append(p)

    # Ordena pelos mais curtidos primeiro
    candidatos.sort(key=lambda x: x.get("curtidas", 0), reverse=True)
    return candidatos


def baixar_e_transcrever(post):
    code = post["code"]
    url = post["url"]
    autor = post.get("autor", "")
    target_mp4 = MIDIA / f"{code}.mp4"

    # 1. Download via yt-dlp usando Safari cookies
    cmd_dl = [
        "yt-dlp",
        "--cookies-from-browser", "safari",
        "--no-playlist",
        "-o", str(MIDIA / f"{code}.%(ext)s"),
        url
    ]
    try:
        p_dl = subprocess.run(cmd_dl, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {
            "code": code,
            "url": url,
            "autor": autor,
            "status": "timeout_download",
            "detalhe": "download excedeu 120s",
            "fala": "",
            "duracao_seg": 0,
            "transcrito_em": datetime.datetime.now().isoformat()
        }

    # Acha o arquivo baixado
    arquivos = list(MIDIA.glob(f"{code}.*"))
    video_arq = None
    for a in arquivos:
        if a.suffix.lower() in [".mp4", ".mkv", ".webm", ".m4a"]:
            video_arq = a
            break

    if not video_arq or not video_arq.exists():
        return {
            "code": code,
            "url": url,
            "autor": autor,
            "fala": "",
            "status": "erro_download",
            "detalhe": p_dl.stderr[:200] if p_dl.stderr else "arquivo nao encontrado",
            "transcrito_em": datetime.datetime.now().isoformat()
        }

    # 2. Transcrição com Whisper local
    cmd_wh = [
        "whisper",
        str(video_arq),
        "--model", "base",
        "--language", "pt",
        "--output_format", "txt",
        "--output_dir", str(MIDIA)
    ]
    fala = ""
    status = "sucesso"
    detalhe = ""
    try:
        p_wh = subprocess.run(cmd_wh, capture_output=True, text=True, timeout=240)
        txt_arq = MIDIA / f"{video_arq.stem}.txt"
        if txt_arq.exists():
            fala = txt_arq.read_text(encoding="utf-8").strip()
            fala = re.sub(r"\s+", " ", fala)
        if not fala:
            status = "sem_audio_ou_vazio"
            detalhe = p_wh.stderr[:200] if p_wh.stderr else ""
    except subprocess.TimeoutExpired:
        status = "timeout"
        detalhe = "whisper excedeu tempo limite de 240s"
    except Exception as e:
        status = "erro_transcricao"
        detalhe = str(e)[:200]

    # 3. Limpeza dos arquivos de mídia (só guardamos o texto transcrito)
    for a in list(MIDIA.glob(f"{code}*")):
        try:
            a.unlink(missing_ok=True)
        except Exception:
            pass

    return {
        "code": code,
        "url": url,
        "autor": autor,
        "fala": fala,
        "status": status,
        "detalhe": detalhe,
        "transcrito_em": datetime.datetime.now().isoformat()
    }


def run(limite=None):
    MIDIA.mkdir(parents=True, exist_ok=True)
    elegiveis = carregar_elegiveis()
    print(f"Vídeos/reels elegíveis para transcrição: {len(elegiveis)}")

    if limite:
        elegiveis = elegiveis[:limite]

    for idx, p in enumerate(elegiveis, 1):
        print(f"[{idx}/{len(elegiveis)}] Baixando e transcrevendo {p['code']} (@{p.get('autor')})...", flush=True)
        t0 = time.time()
        res = baixar_e_transcrever(p)
        elapsed = round(time.time() - t0, 1)

        with open(F_TRANS, "a", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")

        print(f"  -> Status: {res['status']} em {elapsed}s | Fala: {res['fala'][:80]}...", flush=True)
        time.sleep(1)

    print("Transcrição concluída!")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limite=lim)
