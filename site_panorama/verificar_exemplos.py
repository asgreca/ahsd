"""Segunda leitura dos comentários que o site mostra como exemplo.

Lê exemplos_pendentes.jsonl (gerado por gerar_dados.py) e pergunta ao JEV se cada
comentário fala sério e no tema, ou se é ironia/piada. Grava jev_exemplos.jsonl.

Uso: python3 -I verificar_exemplos.py && python3 -I gerar_dados.py
"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
JEV = str(Path.home() / ".local/bin/jev")
PERG = ("Este comentário de rede social foi rotulado como \"{rotulo}\". Ele fala sério e de fato se encaixa nesse rótulo, "
        "ou é ironia, piada, exagero ou deboche? Relatos absurdos (QI 215, mover objetos com a mente) são ironia.")


def checar(r):
    for _ in range(3):
        p = subprocess.run([JEV, "escolha", PERG.format(rotulo=r["rotulo"]), "--opcoes",
                            "serio_e_no_tema|ironia_ou_piada|serio_fora_do_tema", "--estado", r["texto"]],
                           capture_output=True, text=True, timeout=120)
        try:
            out = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            continue
        if "escolha" in out:
            return {**r, "escolha": out["escolha"], "confianca": out.get("confianca")}
    return {**r, "escolha": None}


pend = [json.loads(l) for l in open(AQUI / "exemplos_pendentes.jsonl", encoding="utf-8")]
with open(AQUI / "jev_exemplos.jsonl", "a", encoding="utf-8") as f, ThreadPoolExecutor(12) as ex:
    for r in ex.map(checar, pend):
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("verificados", len(pend))
