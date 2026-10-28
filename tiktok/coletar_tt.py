import subprocess
import time
import json
import re
import datetime
from pathlib import Path
import dom_tt

DADOS = Path("tiktok/dados")
DADOS.mkdir(exist_ok=True)
MIDIA = Path("tiktok/midia")
MIDIA.mkdir(exist_ok=True)

F_VIDEOS_URLS = DADOS / "tiktok_videos_urls.tsv"
F_VIDEOS = DADOS / "tiktok_videos.jsonl"
F_COMENTARIOS = DADOS / "tiktok_comentarios.jsonl"
F_IGNORADOS = DADOS / "tiktok_videos_ignorados.jsonl"
F_TRANSCRICOES = DADOS / "tiktok_transcricoes.jsonl"

def carregar_coletados():
    coletados = set()
    if F_VIDEOS.exists():
        with open(F_VIDEOS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        coletados.add(json.loads(l).get("url"))
                    except:
                        pass
    if F_IGNORADOS.exists():
        with open(F_IGNORADOS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        coletados.add(json.loads(l).get("url"))
                    except:
                        pass
    return coletados

JS_EXPANDIR = """
(() => {
    // Rola para carregar comentários
    let container = document.querySelector('[data-e2e="comment-list"]') || document.body;
    window.scrollBy(0, 800);
    
    // Clica em 'Ver mais respostas'
    let btns = Array.from(document.querySelectorAll('[data-e2e="view-more-1"], [data-e2e="view-more-2"], button'));
    for (let b of btns) {
        if (b.innerText && (b.innerText.includes('Ver mais') || b.innerText.includes('View more') || b.innerText.includes('respostas'))) {
            b.click();
        }
    }
})()
"""

JS_EXTRAIR = """
(() => {
    // Autor
    let userEl = document.querySelector('[data-e2e="browse-username"], [data-e2e="user-title"], h1[data-e2e="user-subtitle"]');
    let autor = userEl ? userEl.innerText.trim() : '';

    // Legenda e tags
    let descEl = document.querySelector('[data-e2e="browse-video-desc"], [data-e2e="video-desc"]');
    let desc = descEl ? descEl.innerText.trim() : '';

    // Data
    let timeEl = document.querySelector('span[data-e2e="browser-nickname"] + span, [data-e2e="video-create-time"]');
    let dataStr = timeEl ? timeEl.innerText.trim() : '';

    // Métricas (likes, comments, bookmarks, shares)
    let likeEl = document.querySelector('[data-e2e="like-count"], [data-e2e="browse-like-icon"] + strong');
    let commentEl = document.querySelector('[data-e2e="comment-count"], [data-e2e="browse-comment-icon"] + strong');
    let shareEl = document.querySelector('[data-e2e="share-count"]');

    let parseNum = (el) => {
        if (!el) return 0;
        let t = el.innerText.trim();
        if (!t) return 0;
        if (t.includes('K')) return Math.round(parseFloat(t.replace('K', '')) * 1000);
        if (t.includes('M')) return Math.round(parseFloat(t.replace('M', '')) * 1000000);
        return parseInt(t.replace(/\\D/g, '')) || 0;
    };

    // Comentários
    let commElements = Array.from(document.querySelectorAll('[data-e2e="comment-level-1"], [data-e2e="comment-item"]'));
    let comentarios = [];
    for (let c of commElements) {
        let u = c.querySelector('[data-e2e="comment-username"], a');
        let txt = c.querySelector('[data-e2e="comment-level-1"] > span, p');
        let lk = c.querySelector('[data-e2e="comment-like-count"]');
        if (txt) {
            comentarios.push({
                usuario: u ? u.innerText.trim() : '',
                texto: txt.innerText.trim(),
                curtidas: parseNum(lk)
            });
        }
    }

    return JSON.stringify({
        autor: autor,
        legenda: desc,
        data_texto: dataStr,
        curtidas: parseNum(likeEl),
        num_comentarios_metrica: parseNum(commentEl),
        compartilhamentos: parseNum(shareEl),
        num_comentarios_coletados: comentarios.length,
        comentarios: comentarios
    });
})()
"""

def transcrever_video(url, video_id):
    out_tmpl = str(MIDIA / f"{video_id}.%(ext)s")
    cmd_dl = [
        "yt-dlp",
        "--format", "ba/b",
        "--extract-audio",
        "--audio-format", "mp3",
        "--max-filesize", "40M",
        "-o", out_tmpl,
        url
    ]
    try:
        subprocess.run(cmd_dl, capture_output=True, text=True, timeout=60)
        mp3 = MIDIA / f"{video_id}.mp3"
        if not mp3.exists():
            return None

        # Whisper local
        cmd_w = ["whisper", str(mp3), "--model", "base-pt", "--language", "pt", "--output_dir", str(MIDIA), "--output_format", "json"]
        subprocess.run(cmd_w, capture_output=True, text=True, timeout=180)
        json_out = MIDIA / f"{video_id}.json"
        texto = ""
        if json_out.exists():
            data = json.loads(json_out.read_text(encoding="utf-8"))
            texto = data.get("text", "").strip()
            json_out.unlink(missing_ok=True)
        mp3.unlink(missing_ok=True)
        return texto
    except Exception as e:
        print(f"Erro transcrição TikTok: {e}", flush=True)
        return None

def coletar_video(url):
    print(f"Coletando vídeo TikTok: {url}...", flush=True)
    dom_tt.nav(url)
    dom_tt.espera(5)

    # Rola e expande comentários
    for _ in range(4):
        dom_tt.js(JS_EXPANDIR)
        time.sleep(1.5)

    res = dom_tt.js(JS_EXTRAIR)
    if not res or not res.startswith("{"):
        print(f"  -> Falha na extração de {url}", flush=True)
        with open(F_IGNORADOS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"url": url, "motivo": "extração_vazia"}, ensure_ascii=False) + "\n")
        return None

    data = json.loads(res)
    comentarios = data.pop("comentarios", [])
    data["url"] = url
    data["coletado_em"] = datetime.datetime.now().isoformat()

    # Transcrição via áudio Whisper
    m = re.search(r'/video/(\d+)', url)
    vid = m.group(1) if m else str(int(time.time()))
    transcricao = transcrever_video(url, vid)
    data["transcricao"] = transcricao

    with open(F_VIDEOS, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    if comentarios:
        with open(F_COMENTARIOS, "a", encoding="utf-8") as f:
            for c in comentarios:
                c["video_url"] = url
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"  -> Vídeo coletado! Curtidas: {data.get('curtidas')} | Comentários: {len(comentarios)} | Transcrição: {bool(transcricao)}", flush=True)
    return data
