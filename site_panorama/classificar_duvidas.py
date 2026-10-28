"""Classifica dúvidas e angústias dos comentários com o JEV.

Amostra: comentários de 2021 a 2026 (YouTube) e do Instagram que fazem pergunta
ou trazem palavras de sofrimento. Entram os mais curtidos e uma parte sorteada.
Grava jev_duvidas.jsonl (sem autor) e pode ser interrompido e retomado.

Uso: python3 -I classificar_duvidas.py [tamanho_youtube] [tamanho_instagram]
"""
import csv
import json
import random
import re
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha1
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
BD = AQUI.parent / "banco de dados"
SAIDA = AQUI / "jev_duvidas.jsonl"
JEV = str(Path.home() / ".local/bin/jev")
OPCOES = ("sera_que_sou|duvida_sobre_filho|como_avaliar_custo|tdah_autismo_ou_sd|teste_qi_vale|"
          "escola_e_bullying|solidao_nao_se_encaixa|sofrimento_mental|potencial_frustrado|como_entrar_mensa|nenhuma")
PERGUNTA = ("Este comentário foi escrito num vídeo ou post sobre superdotação, altas habilidades, QI ou Mensa. "
            "Qual dúvida ou angústia pessoal ele expressa? Use 'nenhuma' se for piada, opinião genérica, elogio "
            "ou resposta sem dúvida nem sofrimento.")
ANG = re.compile(r"\?|sera que|nao sei se|sofr|ansied|depress|medo|sozinh|solid|angust|frustr|chor|nao me encaix|"
                 r"ninguem entend|incompreend|bullying|cansad|exaust|burnout|isolad|dificuldade|como (faco|fazer|saber|descobr)|"
                 r"onde (faco|fazer)|quanto custa|vale a pena")
PT = re.compile(r"\b(que|nao|eu|meu|minha|voce|com|para|filho|filha)\b")


def norm(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


def candidatos():
    for r in csv.DictReader(open(BD / "youtube_e_imprensa/comentarios_youtube_completo.csv", encoding="utf-8")):
        t = r["texto"]
        if r["data"][:4] in {"2021", "2022", "2023", "2024", "2025", "2026"} and 30 <= len(t) <= 500 \
                and ANG.search(norm(t)) and PT.search(norm(t)):
            yield dict(fonte="YouTube", texto=t, likes=int(float(r["likes"] or 0)), ano=int(r["data"][:4]))
    for l in open(BD / "instagram/ig_comentarios.jsonl", encoding="utf-8"):
        r = json.loads(l)
        t = r.get("texto") or ""
        if 30 <= len(t) <= 500 and ANG.search(norm(t)) and not re.search(r"\bSeguir\b|\d+ sem\b", t):
            ano = str(r.get("data_comentario") or r.get("post_datetime") or "")[:4]
            yield dict(fonte="Instagram", texto=t, likes=int(float(r.get("curtidas") or 0)),
                       ano=int(ano) if ano.isdigit() else None)


def amostra(lista, n, rnd):
    lista = sorted(lista, key=lambda x: -x["likes"])
    topo = lista[: n // 2]
    resto = lista[n // 2:]
    return topo + rnd.sample(resto, min(len(resto), n - len(topo)))


def classificar(item):
    for _ in range(3):
        p = subprocess.run([JEV, "escolha", PERGUNTA, "--opcoes", OPCOES, "--estado", item["texto"]],
                           capture_output=True, text=True, timeout=120)
        try:
            r = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            continue
        if "escolha" in r:
            return {**item, "escolha": r["escolha"], "confianca": r.get("confianca"), "motivo": r.get("motivo")}
    return {**item, "escolha": None, "erro": p.stderr[-200:] or p.stdout[-200:]}


def main():
    n_yt = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    n_ig = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    rnd = random.Random(42)
    todos = list(candidatos())
    yt = [x for x in todos if x["fonte"] == "YouTube"]
    ig = [x for x in todos if x["fonte"] == "Instagram"]
    alvo = amostra(yt, n_yt, rnd) + amostra(ig, n_ig, rnd)
    for x in alvo:
        x["id"] = sha1((x["fonte"] + x["texto"]).encode()).hexdigest()[:16]
    feitos = set()
    if SAIDA.exists():
        feitos = {json.loads(l)["id"] for l in open(SAIDA, encoding="utf-8") if '"escolha": "' in l}
    falta = [x for x in {x["id"]: x for x in alvo}.values() if x["id"] not in feitos]
    print(f"candidatos YT {len(yt)} IG {len(ig)} · amostra {len(alvo)} · faltam {len(falta)}", flush=True)
    with open(SAIDA, "a", encoding="utf-8") as f, ThreadPoolExecutor(12) as ex:
        for i, fut in enumerate(as_completed([ex.submit(classificar, x) for x in falta]), 1):
            f.write(json.dumps(fut.result(), ensure_ascii=False) + "\n")
            f.flush()
            if i % 50 == 0:
                print(i, flush=True)
    print("fim", flush=True)


if __name__ == "__main__":
    main()
