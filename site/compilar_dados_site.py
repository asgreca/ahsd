import json
import os
import re

def extrair_dados():
    amostras = []

    def achar_caminho(caminho_bd, caminho_legado):
        if os.path.exists(caminho_bd):
            return caminho_bd
        return caminho_legado

    path_noticias = achar_caminho("banco de dados/noticias_web/reportagens_ddg.jsonl", "noticias/dados/reportagens_ddg.jsonl")
    path_ig = achar_caminho("banco de dados/instagram/ig_posts.jsonl", "instagram/dados/ig_posts.jsonl")
    path_tt = achar_caminho("banco de dados/tiktok/tiktok_videos.jsonl", "tiktok/dados/tiktok_videos.jsonl")
    path_x = achar_caminho("banco de dados/x_twitter/x_tweets.jsonl", "x/dados/x_tweets.jsonl")

    # 1. Imprensa (DuckDuckGo via Defuddle)
    if os.path.exists(path_noticias):
        with open(path_noticias, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if not line.strip(): continue
                obj = json.loads(line)
                txt = obj.get("texto_integral_md", "")
                if len(txt) < 300:
                    txt = obj.get("snippet", "")
                resumo = txt[:400] + "..." if len(txt) > 400 else txt
                amostras.append({
                    "id": f"noticia_{idx+1}",
                    "rede": "Imprensa",
                    "categoria": "Jornalismo",
                    "autor": obj.get("source", "Imprensa"),
                    "titulo": obj.get("title", ""),
                    "data": obj.get("ano_detectado", "2021-2026"),
                    "texto": resumo,
                    "texto_completo": txt[:1500],
                    "url": obj.get("url", ""),
                    "engajamento": "Veículo Nacional / Regional"
                })

    # 2. Instagram
    if os.path.exists(path_ig):
        with open(path_ig, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                txt = obj.get("caption", "") or obj.get("texto", "")
                if len(txt) > 80:
                    count += 1
                    amostras.append({
                        "id": f"ig_{count}",
                        "rede": "Instagram",
                        "categoria": "Criadores & Psicologia",
                        "autor": f"@{obj.get('perfil', 'criador')}",
                        "titulo": txt[:90] + ("..." if len(txt) > 90 else ""),
                        "data": str(obj.get("ano", "2021-2026")),
                        "texto": txt[:350] + "...",
                        "texto_completo": txt[:1500],
                        "url": obj.get("url", ""),
                        "engajamento": f"{obj.get('likes', 0):,} curtidas | {obj.get('comentarios_count', 0)} comentários".replace(",", ".")
                    })
                    if count >= 35:
                        break

    # 3. TikTok
    if os.path.exists(path_tt):
        with open(path_tt, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                txt = obj.get("transcricao", "") or obj.get("desc", "")
                if len(txt) > 60:
                    count += 1
                    autor = obj.get("autor") or obj.get("perfil") or "tiktok_creator"
                    amostras.append({
                        "id": f"tt_{count}",
                        "rede": "TikTok",
                        "categoria": "Vídeos & Relatos",
                        "autor": f"@{autor}",
                        "titulo": (obj.get("desc") or txt)[:90] + "...",
                        "data": "2021-2026",
                        "texto": txt[:350] + "...",
                        "texto_completo": txt[:1500],
                        "url": obj.get("url", ""),
                        "engajamento": f"{obj.get('views', 0):,} views | {obj.get('likes', 0):,} likes".replace(",", ".")
                    })
                    if count >= 35:
                        break

    # 4. X.com (Twitter)
    if os.path.exists(path_x):
        with open(path_x, "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                txt = obj.get("texto", "")
                if len(txt) > 50:
                    count += 1
                    amostras.append({
                        "id": f"x_{count}",
                        "rede": "X (Twitter)",
                        "categoria": "Debate Público & Membros",
                        "autor": f"@{obj.get('autor', 'usuario')}",
                        "titulo": txt[:90] + ("..." if len(txt) > 90 else ""),
                        "data": str(obj.get("ano", "2021-2026")),
                        "texto": txt[:350],
                        "texto_completo": txt[:1000],
                        "url": obj.get("url", ""),
                        "engajamento": f"{obj.get('likes', 0)} likes | {obj.get('replies', 0)} replies"
                    })
                    if count >= 35:
                        break

    print(f"Total de registros curados para o explorador: {len(amostras)}")
    with open("site/dados/amostras_explorer.json", "w", encoding="utf-8") as f:
        json.dump(amostras, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extrair_dados()
