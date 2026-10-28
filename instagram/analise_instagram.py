#!/usr/bin/env python3
"""Gera relatório e consolidação dos dados coletados do Instagram:
- Mapeamento de criadores (médicos, psicólogos, atores, etc.)
- Métricas de engajamento (curtidas, comentários, seguidores)
- Transcrições dos vídeos e legendas
- Análise temporal e temática dos últimos 5 anos
Saídas:
  instagram/dados/relatorio_instagram.md
  instagram/dados/painel_criadores.csv
"""
import collections
import datetime
import json
import pathlib

IG = pathlib.Path(__file__).parent
DADOS = IG / "dados"
F_PERFIS = DADOS / "ig_perfis.jsonl"
F_POSTS = DADOS / "ig_posts.jsonl"
F_COM = DADOS / "ig_comentarios.jsonl"
F_TRANS = DADOS / "ig_transcricoes.jsonl"
OUT_MD = DADOS / "relatorio_instagram.md"
OUT_CSV = DADOS / "painel_criadores.csv"


def carregar_jsonl(p):
    if not p.exists():
        return []
    out = []
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            try:
                out.append(json.loads(l))
            except Exception:
                pass
    return out


def gerar_relatorio():
    perfis = carregar_jsonl(F_PERFIS)
    posts = carregar_jsonl(F_POSTS)
    comentarios = carregar_jsonl(F_COM)
    transcricoes = carregar_jsonl(F_TRANS)

    # Filtro estrito: 2021 a 2026
    posts = [p for p in posts if not p.get("datetime") or ("2021" <= str(p.get("datetime"))[:4] <= "2026")]
    posts_validos_codes = {p["code"] for p in posts}
    comentarios = [c for c in comentarios if c.get("post_code") in posts_validos_codes]
    transcricoes = [t for t in transcricoes if t.get("code") in posts_validos_codes]

    mapa_trans = {t["code"]: t for t in transcricoes}

    # Agrupa posts por autor
    posts_por_autor = collections.defaultdict(list)
    for p in posts:
        autor = (p.get("autor") or "desconhecido").lower()
        posts_por_autor[autor].append(p)

    # Métricas por criador
    criadores = []
    for per in perfis:
        h = per["handle"].lower()
        p_list = posts_por_autor.get(h, [])
        total_curtidas = sum(p.get("curtidas", 0) for p in p_list)
        total_comentarios = sum(p.get("num_comentarios_coletados", 0) for p in p_list)
        criadores.append({
            "handle": per["handle"],
            "nome": per.get("nome") or per["handle"],
            "categoria": per.get("categoria", "outro"),
            "seguidores": per.get("seguidores", 0),
            "posts_coletados": len(p_list),
            "total_curtidas": total_curtidas,
            "total_comentarios": total_comentarios,
            "bio": per.get("bio", "")
        })

    criadores.sort(key=lambda x: x["seguidores"], reverse=True)

    # Salva CSV
    with open(OUT_CSV, "w", encoding="utf-8") as f:
        f.write("handle,nome,categoria,seguidores,posts_coletados,total_curtidas,total_comentarios,bio\n")
        for c in criadores:
            bio_clean = c["bio"].replace("\n", " ").replace(",", ";")
            f.write(f"{c['handle']},{c['nome']},{c['categoria']},{c['seguidores']},{c['posts_coletados']},{c['total_curtidas']},{c['total_comentarios']},\"{bio_clean}\"\n")

    # Gera Markdown
    md = []
    md.append("# Análise de Dados: Instagram — Mensa, Altas Habilidades e Superdotação")
    md.append(f"Data da análise: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    md.append("\n## 1. Resumo Geral da Coleta\n")
    md.append(f"- **Perfis Mapeados:** {len(perfis)}")
    md.append(f"- **Postagens / Reels Coletados:** {len(posts)}")
    md.append(f"- **Comentários Extraídos:** {len(comentarios)}")
    md.append(f"- **Vídeos com Transcrição de Fala (Whisper):** {len(transcricoes)}")

    # Categorias de Criadores
    cat_count = collections.Counter(c["categoria"] for c in criadores)
    md.append("\n## 2. Distribuição de Criadores por Categoria\n")
    md.append("| Categoria | Criadores Mapeados | Exemplo de Handle |")
    md.append("|---|---|---|")
    for cat, count in cat_count.most_common():
        ex = next((c["handle"] for c in criadores if c["categoria"] == cat), "")
        md.append(f"| `{cat}` | {count} | @{ex} |")

    # Tabela de Principais Vozes
    md.append("\n## 3. Principais Vozes e Engajamento\n")
    md.append("| Handle | Categoria | Seguidores | Posts Analisados | Curtidas Totais |")
    md.append("|---|---|---|---|---|")
    for c in criadores[:20]:
        md.append(f"| [@{c['handle']}](https://instagram.com/{c['handle']}) | `{c['categoria']}` | {c['seguidores']:,} | {c['posts_coletados']} | {c['total_curtidas']:,} |")

    # Vídeos e Transcrições Mais Engajados
    md.append("\n## 4. Destaques de Vídeos e Falas Transcritas\n")
    posts_com_video = [p for p in posts if p["code"] in mapa_trans and mapa_trans[p["code"]].get("fala")]
    posts_com_video.sort(key=lambda x: x.get("curtidas", 0), reverse=True)

    for p in posts_com_video[:10]:
        t = mapa_trans[p["code"]]
        md.append(f"### Reel: [{p['code']}]({p['url']}) — @{p.get('autor')}")
        md.append(f"- **Data:** {p.get('datetime', 'N/D')}")
        md.append(f"- **Curtidas:** {p.get('curtidas', 0):,} | **Comentários coletados:** {p.get('num_comentarios_coletados', 0)}")
        md.append(f"- **Legenda:** {p.get('legenda', '')[:250]}...")
        md.append(f"- **O que foi falado no vídeo (Transcrição Whisper):**")
        md.append(f"> \"{t.get('fala', '')}\"\n")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Relatório gerado em: {OUT_MD}")
    print(f"Painel CSV gerado em: {OUT_CSV}")


if __name__ == "__main__":
    gerar_relatorio()
