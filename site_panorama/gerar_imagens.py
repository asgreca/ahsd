"""Gera as ilustrações da página da história com a API de imagens da OpenAI.

Lê a chave de Projeto de Dados/Alpes/.env (variáveis OPENAI e OPENAI_IMAGE_MODEL)
sem imprimi-la. Grava img/<nome>.png e pula as que já existem.

Uso: python3 -I gerar_imagens.py
"""
import base64
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = AQUI.parents[2] / "Alpes" / ".env"
PASTA = AQUI / "img"

ESTILO = ("Editorial illustration for a data journalism story. Deep dark green background (#08110d), "
          "luminous emerald and mint line work, a few lime highlights, soft glow, minimal and elegant, "
          "flat vector feel with subtle grain. Anonymous figures only, no faces, no real people, "
          "no text, no letters, no numbers, no logos.")
CENAS = {
    "capa": "A human head in profile made of glowing neural network lines and nodes, with small phone screens, "
            "video frames and newspaper pages orbiting it like satellites.",
    "espetaculo": "A game show stage built from a giant multiple choice test sheet, spotlights, floating puzzle pieces "
                  "and optical illusion shapes, a crowd of tiny silhouettes holding up glowing phones.",
    "espelho": "A young adult silhouette holding a smartphone whose screen works as a mirror, reflecting a bright "
               "brain drawn with lines; floating checklist icons and heart and comment bubbles around.",
    "lei": "A school desk with a child's backpack connected by glowing lines to a stylized parliament dome, "
           "documents with seals floating between them.",
    "clube": "A round glowing door slightly open with warm light inside and a small group within, while many "
             "silhouettes stand outside looking in, some curious, some with crossed arms.",
    "vozes": "A crowd of silhouettes seen from above, with many speech bubbles rising, most dim, a few bright ones "
             "containing question shapes, like lanterns in the night.",
    "ponte": "A bridge of light being built between two cliffs, small figures crossing from a dark side toward a "
             "brighter side, construction lines still visible.",
}


CENAS_ANOS = {
    "ano2021": "A testing room reopening after a long pause: spaced desks with answer sheets under soft green lamps, "
               "a large screen showing a glowing quiz with optical illusion shapes, a few masked silhouettes walking in.",
    "ano2022": "A round table seen from above with twenty small lights around it forming a ring, like a birthday "
               "celebration of a community, newspaper pages fanned out on the table.",
    "ano2023": "A swarm of vertical phone screens floating in the dark, each one glowing, a silhouette in front of them "
               "reading a checklist of signs, sound waves around the head suggesting sensory overload.",
    "ano2024": "An adult woman silhouette looking into a mirror that reflects a bright neural network, a magnifying "
               "glass and an assessment form beside her, sense of late discovery.",
    "ano2025": "A stage with spotlights and microphones, two overlapping brain outlines glowing in different greens "
               "above it, an audience of silhouettes with speech bubbles.",
    "ano2026": "A child silhouette at a podium in front of a stylized parliament dome, a document with an official "
               "seal floating above, school desks in the foreground, morning light.",
}

CENAS_CLUSTERS = {
    "cl_clinica": "A calm clinic office: a therapist silhouette and a client silhouette facing each other, an assessment "
                  "booklet and a stethoscope on the desk, a brain diagram on the wall.",
    "cl_espetaculo": "A flashy game show stage with a giant spinning quiz wheel, sparkling question marks and a trophy, "
                     "a crowd of phone screens recording it.",
    "cl_neuro": "Two podcast microphones facing each other in a dim studio, headphones, sound waves turning into "
                "puzzle-piece and infinity shapes between them.",
    "cl_educacao": "A classroom with a child silhouette and a parent silhouette holding hands at the door, a stack of "
                   "books and a law book with a seal on the teacher desk.",
    "cl_adulto": "An adult silhouette at a window at night holding an old school report card, a younger reflection of "
                 "themselves faintly visible in the glass, neural lines glowing.",
    "cl_midia": "A TV studio camera and a round table logo-free emblem in the background, news screens glowing, "
                "a small group on a stage.",
}


def ler_env():
    v = {}
    for linha in ENV.read_text().splitlines():
        if "=" in linha and not linha.strip().startswith("#"):
            k, _, val = linha.partition("=")
            v[k.strip()] = val.strip().strip('"').strip("'")
    return v


def gerar(nome, cena, chave, modelo):
    destino = PASTA / f"{nome}.png"
    if destino.exists():
        return nome, "já existe"
    corpo = {"model": modelo, "prompt": f"{ESTILO} Scene: {cena}", "size": "1536x1024", "n": 1}
    if modelo.startswith("gpt-image"):
        corpo["quality"] = "medium"
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=json.dumps(corpo).encode(),
                                 headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            dado = json.load(r)["data"][0]
    except urllib.error.HTTPError as e:
        msg = e.read()[:300].decode(errors="replace")
        if e.code in (400, 404) and modelo != "gpt-image-1" and "model" in msg.lower():
            return gerar(nome, cena, chave, "gpt-image-1")  # modelo do .env indisponível
        return nome, f"erro {e.code}: {msg}"
    if "b64_json" in dado:
        destino.write_bytes(base64.b64decode(dado["b64_json"]))
    else:
        destino.write_bytes(urllib.request.urlopen(dado["url"], timeout=120).read())
    return nome, f"ok ({modelo})"


def main():
    env = ler_env()
    chave = env.get("OPENAI")
    modelo = env.get("OPENAI_IMAGE_MODEL") or "gpt-image-1"
    if not chave:
        sys.exit("chave OPENAI não encontrada no .env")
    PASTA.mkdir(exist_ok=True)
    print("modelo:", modelo, flush=True)
    cenas = {**CENAS, **CENAS_ANOS, **CENAS_CLUSTERS}
    with ThreadPoolExecutor(4) as ex:
        for nome, st in ex.map(lambda kv: gerar(kv[0], kv[1], chave, modelo), cenas.items()):
            print(nome, st, flush=True)


if __name__ == "__main__":
    main()
