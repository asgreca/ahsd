import subprocess
import time
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
DADOS = BASE / "dados"
MIDIA = BASE / "midia"
DADOS.mkdir(exist_ok=True)
MIDIA.mkdir(exist_ok=True)

F_VIDEOS_URLS = DADOS / "tiktok_videos_urls.tsv"
F_VIDEOS = DADOS / "tiktok_videos.jsonl"
F_IGNORADOS = DADOS / "tiktok_videos_ignorados.jsonl"
F_TRANSCRICOES = DADOS / "tiktok_transcricoes.jsonl"

def carregar_processados():
    proc = set()
    if F_VIDEOS.exists():
        with open(F_VIDEOS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        proc.add(json.loads(l).get("url"))
                    except:
                        pass
    if F_IGNORADOS.exists():
        with open(F_IGNORADOS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        proc.add(json.loads(l).get("url"))
                    except:
                        pass
    return proc

def transcrever_audio(mp3_path, video_id):
    try:
        cmd_w = [
            "whisper",
            str(mp3_path),
            "--model", "base",
            "--language", "pt",
            "--output_dir", str(MIDIA),
            "--output_format", "txt"
        ]
        r = subprocess.run(cmd_w, capture_output=True, text=True, timeout=180)
        txt_out = MIDIA / f"{video_id}.txt"
        texto = ""
        if txt_out.exists():
            texto = txt_out.read_text(encoding="utf-8").strip()
            txt_out.unlink(missing_ok=True)
        return texto
    except Exception as e:
        print(f"Erro Whisper: {e}", flush=True)
        return ""

def processar_video(url, termo_busca=""):
    print(f"\n[TikTok] Processando: {url}...", flush=True)
    m = re.search(r'/video/(\d+)', url)
    vid = m.group(1) if m else str(int(time.time()))

    cmd_meta = ["yt-dlp", "--dump-json", "--no-warnings", url]
    try:
        res = subprocess.run(cmd_meta, capture_output=True, text=True, timeout=30)
        if res.returncode != 0 or not res.stdout.strip():
            print(f"  -> Falha ao extrair metadados.", flush=True)
            with open(F_IGNORADOS, "a", encoding="utf-8") as f:
                f.write(json.dumps({"url": url, "motivo": "falha_metadados"}, ensure_ascii=False) + "\n")
            return None
        meta = json.loads(res.stdout)
    except Exception as e:
        print(f"  -> Exceção metadados: {e}", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "motivo": str(e)}, ensure_ascii=False) + "\n")
        return None

    upload_date = meta.get("upload_date")  # e.g. "20250525"
    if upload_date and (upload_date < "20210101" or upload_date > "20261231"):
        print(f"  -> Fora do período ({upload_date}). Ignorando.", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "upload_date": upload_date, "motivo": "fora_periodo_2021_2026"}, ensure_ascii=False) + "\n")
        return None

    # Baixa áudio MP3
    out_tmpl = str(MIDIA / f"{vid}.%(ext)s")
    cmd_dl = [
        "yt-dlp",
        "--format", "ba/b",
        "--extract-audio",
        "--audio-format", "mp3",
        "--max-filesize", "30M",
        "-o", out_tmpl,
        url
    ]
    texto_transcricao = ""
    try:
        subprocess.run(cmd_dl, capture_output=True, text=True, timeout=45)
        mp3 = MIDIA / f"{vid}.mp3"
        if mp3.exists():
            print(f"  -> Áudio baixado. Executando Whisper...", flush=True)
            texto_transcricao = transcrever_audio(mp3, vid)
            mp3.unlink(missing_ok=True)
            print(f"  -> Transcrição concluída ({len(texto_transcricao)} chars): {texto_transcricao[:80]}...", flush=True)
    except Exception as e:
        print(f"  -> Erro áudio/whisper: {e}", flush=True)

    registro = {
        "id": vid,
        "url": url,
        "autor": meta.get("uploader") or meta.get("uploader_id"),
        "titulo": meta.get("title"),
        "descricao": meta.get("description"),
        "curtidas": meta.get("like_count") or 0,
        "comentarios": meta.get("comment_count") or 0,
        "views": meta.get("view_count") or 0,
        "compartilhamentos": meta.get("repost_count") or 0,
        "upload_date": upload_date,
        "duracao": meta.get("duration"),
        "termo_origem": termo_busca,
        "transcricao": texto_transcricao
    }

    with open(F_VIDEOS, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    if texto_transcricao:
        with open(F_TRANSCRICOES, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": vid, "url": url, "autor": registro["autor"], "fala": texto_transcricao}, ensure_ascii=False) + "\n")

    print(f"  -> Salvo com sucesso! Likes: {registro['curtidas']} | Comentários: {registro['comentarios']} | Fala transcrita: {bool(texto_transcricao)}", flush=True)
    return registro

def run():
    print("Iniciando drenagem e transcrição dos vídeos do TikTok...", flush=True)
    processados = carregar_processados()
    linhas = []
    if F_VIDEOS_URLS.exists():
        for l in F_VIDEOS_URLS.read_text(encoding="utf-8").splitlines():
            if l.strip():
                partes = l.split("\t")
                linhas.append((partes[0], partes[1] if len(partes) > 1 else ""))

    pendentes = [p for p in linhas if p[0] not in processados]
    print(f"Total na fila do TikTok: {len(pendentes)} vídeos pendentes.", flush=True)

    for i, (u, termo) in enumerate(pendentes, 1):
        print(f"\n[{i}/{len(pendentes)}] TikTok Video", flush=True)
        try:
            processar_video(u, termo)
        except Exception as e:
            print(f"Erro processando {u}: {e}", flush=True)
        time.sleep(1)

if __name__ == "__main__":
    run()
