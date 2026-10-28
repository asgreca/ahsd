import json
from pathlib import Path
from collections import Counter

DADOS = Path("tiktok/dados")
F_VIDEOS = DADOS / "tiktok_videos.jsonl"
F_RELATORIO = DADOS / "relatorio_tiktok.md"

def analisar():
    if not F_VIDEOS.exists():
        print("Sem dados do TikTok.")
        return

    videos = []
    with open(F_VIDEOS, "r", encoding="utf-8") as f:
        for l in f:
            if l.strip():
                videos.append(json.loads(l))

    total_videos = len(videos)
    total_likes = sum(v.get("curtidas", 0) for v in videos)
    total_views = sum(v.get("views", 0) for v in videos)
    total_comms = sum(v.get("comentarios", 0) for v in videos)
    total_transcritos = sum(1 for v in videos if v.get("transcricao"))

    # Autores mais engajados
    criadores = Counter()
    for v in videos:
        aut = v.get("autor") or "desconhecido"
        criadores[aut] += v.get("curtidas", 0)

    # Ranking por curtidas
    top_videos = sorted(videos, key=lambda x: x.get("curtidas", 0), reverse=True)

    md = f"""# Relatório de Discurso no TikTok — Mensa & Superdotação Brasil (2021–2026)

## 1. Visão Geral da Base de Dados
* **Total de Vídeos Catalogados e Analisados:** {total_videos}
* **Engajamento Total Acumulado:**
  * **Curtidas:** {total_likes:,}
  * **Visualizações:** {total_views:,}
  * **Comentários Declarados:** {total_comms:,}
* **Vídeos com Transcrição de Áudio Completa (Whisper):** {total_transcritos}
* **Filtro Temporal:** Estritamente 2021 a 2026

## 2. Principais Criadores por Engajamento Acumulado (Curtidas)
"""
    for aut, likes in criadores.most_common(10):
        md += f"* **@{aut}:** {likes:,} curtidas\n"

    md += "\n## 3. Top Vídeos Virais e Transcrição das Falas Relevantes\n\n"
    for i, v in enumerate(top_videos[:10], 1):
        aut = v.get("autor", "desconhecido")
        likes = v.get("curtidas", 0)
        views = v.get("views", 0)
        comms = v.get("comentarios", 0)
        data = v.get("upload_date", "")
        dt_fmt = f"{data[:4]}-{data[4:6]}-{data[6:]}" if len(data) == 8 else data
        titulo = (v.get("titulo") or "").replace("\n", " ")
        fala = v.get("transcricao") or "(sem fala / áudio instrumental)"

        md += f"### {i}. @{aut} — {likes:,} curtidas | {views:,} views | {comms:,} comentários ({dt_fmt})\n"
        md += f"* **Link:** {v.get('url')}\n"
        md += f"* **Legenda:** {titulo}\n"
        md += f"* **Transcrição da Fala (Whisper):**\n> \"{fala[:400]}...\"\n\n"

    F_RELATORIO.write_text(md, encoding="utf-8")
    print(f"Relatório gerado em: {F_RELATORIO}")

if __name__ == "__main__":
    analisar()
