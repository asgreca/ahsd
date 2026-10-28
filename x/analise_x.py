import json
from pathlib import Path
from collections import Counter

DADOS = Path("x/dados")
F_TWEETS = DADOS / "x_tweets.jsonl"
F_RESPOSTAS = DADOS / "x_respostas.jsonl"
F_RELATORIO = DADOS / "relatorio_x.md"

def analisar():
    if not F_TWEETS.exists():
        print("Sem dados de tweets.")
        return

    tweets = []
    with open(F_TWEETS, "r", encoding="utf-8") as f:
        for l in f:
            if l.strip():
                tweets.append(json.loads(l))

    respostas = []
    if F_RESPOSTAS.exists():
        with open(F_RESPOSTAS, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    respostas.append(json.loads(l))

    total_tweets = len(tweets)
    total_respostas = len(respostas)

    # Autores mais frequentes
    autores = Counter(t.get("usuario", "").split("@")[-1].strip() for t in tweets if t.get("usuario"))

    # Análise temática simples por palavras-chave
    temas = Counter()
    for t in tweets:
        txt = (t.get("texto") or "").lower()
        if "mensa" in txt:
            temas["Mensa / Teste de QI"] += 1
        if "dupla excepcionalidade" in txt or "tdah" in txt or "tea" in txt or "autismo" in txt:
            temas["Dupla Excepcionalidade / Neurodivergência"] += 1
        if "laudo" in txt or "diagnóstico" in txt or "diagnostico" in txt:
            temas["Diagnóstico / Laudo Clínico"] += 1
        if "escola" in txt or "criança" in txt or "aluno" in txt or "educação" in txt:
            temas["Educação / Escola"] += 1
        if "burr" in txt or "ego" in txt or "meme" in txt or "humor" in txt:
            temas["Sátira / Humor / Defesa Social"] += 1

    md = f"""# Relatório de Discurso no X.com (Twitter) — Mensa & Superdotação Brasil (2021–2026)

## 1. Visão Geral da Coleta
* **Total de Tweets Coletados:** {total_tweets}
* **Total de Respostas e Comentários Extraídos:** {total_respostas}
* **Período de Coleta:** Estritamente 2021 a 2026

## 2. Distribuição Temática das Postagens
"""
    for tema, count in temas.most_common():
        pct = (count / total_tweets * 100) if total_tweets else 0
        md += f"* **{tema}:** {count} tweets ({pct:.1f}%)\n"

    md += "\n## 3. Principais Postagens e Narrativas Identificadas\n\n"
    for i, t in enumerate(tweets[:10], 1):
        u = t.get("usuario", "Anônimo")
        dt = t.get("datetime", "")[:10]
        txt = t.get("texto", "").replace("\n", " ")
        resp_count = t.get("num_respostas_coletadas", 0)
        md += f"### {i}. {u} ({dt}) — {resp_count} respostas coletadas\n"
        md += f"> \"{txt}\"\n\n"

    F_RELATORIO.write_text(md, encoding="utf-8")
    print(f"Relatório gerado em: {F_RELATORIO}")

if __name__ == "__main__":
    analisar()
