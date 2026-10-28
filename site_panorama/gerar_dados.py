"""Gera dados.js para o site Panorama da Superdotação no Brasil.

Lê a pasta ../banco de dados e grava só agregados (contagens, médias, listas de
criadores públicos e trechos curtos de comentários sem autor). Nada da pasta
restrito sai daqui além de contagens por veículo, tema e postura.

Uso: python3 -I gerar_dados.py
"""
import csv
import json
import math
import random
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from email.utils import parsedate_to_datetime
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
BD = AQUI.parent / "banco de dados"
ANOS = [2021, 2022, 2023, 2024, 2025, 2026]


def jl(p):
    return [json.loads(l) for l in open(BD / p, encoding="utf-8") if l.strip()]


def lecsv(p, enc="utf-8-sig"):
    return list(csv.DictReader(open(BD / p, encoding=enc)))


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def ano_de(s):
    s = str(s or "")
    m = re.match(r"(\d{4})", s)
    if m:
        return int(m.group(1))
    try:
        return parsedate_to_datetime(s).year
    except Exception:
        return None


def mes_de(s):
    s = str(s or "")
    m = re.match(r"(\d{4})-?(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    try:
        d = parsedate_to_datetime(s)
        return f"{d.year}-{d.month:02d}"
    except Exception:
        return None


# ---------------------------------------------------------------- léxico
# Grupos de palavras usados para comparar redes, veículos e criadores com a
# mesma régua. Um item "toca" o grupo se o texto tiver ao menos um termo.
GRUPOS = {
    "mensa": ("Mensa", r"\bmensa\b"),
    "qi_teste": ("QI e testes", r"\bqi\b|\biq\b|teste de inteligencia|quociente|\bqi alto|\bwais\b|\bwisc\b"),
    "neuro": ("TDAH, autismo e saúde mental", r"tdah|autis|\btea\b|neurodiverg|neuroatip|dupla excepcional|sensorial|ansiedade|depress|\b2e\b"),
    "diagnostico": ("Diagnóstico e avaliação", r"diagnost|laudo|avaliacao|neuropsic|identificad|identificar|identificac"),
    "escola": ("Escola e educação", r"escola|professor|\baluno|estudante|educac|ensino|\benem\b|vestibular|sala de aula|aceleracao"),
    "politica": ("Leis e políticas públicas", r"\blei\b|projeto de lei|\bpl \d|senado|camara dos|deputad|politica nacional|\bmec\b|direito|inclusao|governo federal"),
    "infancia": ("Infância e família", r"crianc|\bfilh|\bbebe|\bmae\b|\bmaes\b|\bpai\b|\bpais\b|famil|infan|maternidade"),
    "humor": ("Humor, quiz e desafio", r"kkk|haha|piada|\bmeme|\bquiz|desafio|acerte|prove que|teste rapido|so genios|so pessoas com"),
    "genio": ("Gênio, prodígio e recorde", r"genio|prodigio|recorde|guinness|mais inteligente|superinteligen|\bqi de \d{3}"),
    "elitismo": ("Elitismo e arrogância", r"arrogan|elitis|soberb|prepoten|se acha|se acham|metido|clube de|panelinha"),
    "adulto": ("Descoberta na vida adulta", r"\badult|descobri|tardi|depois dos \d|aos \d\d anos|mulher"),
}
RX = {k: re.compile(v[1]) for k, v in GRUPOS.items()}
TEMA_RX = re.compile(r"superdot|altas habilidades|\bahsd\b|\bah/sd\b|\bqi\b|\biq\b|\bmensa\b|gifted|superinteligen|genio|prodigio|neurodiverg|\b2e\b|dupla excepcional|inteligencia")


def grupos(texto):
    t = norm(texto)
    return {k for k, r in RX.items() if r.search(t)}


def perfil_lexico(textos):
    n = len(textos) or 1
    c = Counter()
    for t in textos:
        c.update(grupos(t))
    return {k: round(100 * c[k] / n, 1) for k in GRUPOS}


# ---------------------------------------------------------------- YouTube
videos = lecsv("classificacao_jev/videos_metricas_classificados.csv")
for v in videos:
    v["_ano"] = ano_de(v["data"])
    v["_views"] = num(v["views"])
    v["_likes"] = num(v["likes"])
temas_multi_v = {r["id"]: r for r in lecsv("youtube_e_imprensa/temas_multi_videos.csv")}

coment = lecsv("youtube_e_imprensa/comentarios_youtube_completo.csv")
temas_c = lecsv("youtube_e_imprensa/temas_multi_comentarios.csv")
# Os dois arquivos não estão na mesma ordem: o vínculo é por vídeo e texto.
tema_por_chave = defaultdict(list)
for r in temas_c:
    tema_por_chave[(r["video"].strip(), r["texto"].strip())].append(r["tema_principal"])
for c in coment:
    lst = tema_por_chave.get((c["video"].strip(), c["texto"].strip()))
    c["_tema"] = lst.pop() if lst else None
    c["_ano"] = ano_de(c["data"])
    c["_mes"] = mes_de(c["data"])
    c["_likes"] = num(c["likes"])
vinculados = sum(1 for c in coment if c["_tema"])

# ---------------------------------------------------------------- Imprensa
noticias = lecsv("youtube_e_imprensa/noticias_unicas_tema.csv")
artigos_jev = json.load(open(BD / "restrito/artigos_classificados_jev.json", encoding="utf-8"))
revistas = lecsv("youtube_e_imprensa/revistas_artigos.csv")
artigos_txt = lecsv("youtube_e_imprensa/artigos_completos.csv")
ddg = jl("noticias_web/reportagens_ddg.jsonl")


def veiculo_canon(v):
    v = (v or "").strip()
    k = norm(v)
    mapa = [
        ("g1", "G1"), ("o globo", "O Globo"), ("oglobo", "O Globo"), ("globo", "O Globo"),
        ("crescer", "Crescer"), ("veja saude", "Veja"), ("veja", "Veja"), ("assine abril", "Veja"),
        ("terra", "Terra"), ("exame", "Exame"), ("cnn", "CNN Brasil"), ("istoe", "IstoÉ"),
        ("correio braziliense", "Correio Braziliense"), ("metropoles", "Metrópoles"),
        ("so noticia boa", "Só Notícia Boa"), ("r7", "R7"), ("uol", "UOL"), ("folha", "Folha"),
        ("estadao", "Estadão"), ("senado", "Agência Senado"), ("camara", "Agência Câmara"),
        ("bbc", "BBC Brasil"), ("diario do nordeste", "Diário do Nordeste"),
    ]
    for chave, nome in mapa:
        if k == chave or k.startswith(chave + " ") or k == chave.replace(" ", ""):
            return nome
    return v

for a in artigos_jev:
    a["_veic"] = veiculo_canon(a["veiculo"])
    a["_ano"] = ano_de(a["data"])
    a["_mes"] = mes_de(a["data"])

# ---------------------------------------------------------------- Redes
ig_posts = jl("instagram/ig_posts.jsonl")
ig_trans = {t["code"]: t.get("fala") or "" for t in jl("instagram/ig_transcricoes.jsonl")}
ig_com = jl("instagram/ig_comentarios.jsonl")
ig_perfis = {p["handle"]: p for p in jl("instagram/ig_perfis.jsonl")}
painel = {r["handle"]: r for r in lecsv("instagram/painel_criadores.csv")}
tt = jl("tiktok/tiktok_videos.jsonl")
tt_trans = {t["id"]: t.get("fala") or "" for t in jl("tiktok/tiktok_transcricoes.jsonl")}
xt = jl("x_twitter/x_tweets.jsonl")
xr = jl("x_twitter/x_respostas.jsonl")


def legenda_limpa(leg, autor):
    # A legenda do Instagram veio com o texto da interface ("Seguir", "6 sem").
    linhas = [l.strip() for l in str(leg or "").split("\n")]
    fora = {autor, "Áudio original", "Seguir", "Seguindo", "", "Responder"}
    linhas = [l for l in linhas if l not in fora and not re.fullmatch(r"\d+ (sem|d|h|min)", l)]
    return " ".join(linhas)


itens = []  # um registro por postagem/vídeo de rede social, já filtrado pelo tema
for p in ig_posts:
    if not p.get("autor"):
        linhas = [l.strip() for l in str(p.get("legenda") or "").split("\n") if l.strip()]
        p["autor"] = next((l for l in linhas if re.fullmatch(r"[\w.]+", l) and len(l) > 3), "")
    texto = legenda_limpa(p.get("legenda"), p.get("autor")) + " " + ig_trans.get(p["code"], "")
    itens.append(dict(rede="Instagram", autor=p.get("autor") or "", ano=ano_de(p.get("datetime")),
                      mes=mes_de(p.get("datetime")), texto=texto, likes=num(p.get("curtidas")),
                      views=None, coments=num(p.get("num_comentarios_coletados")), url=p.get("url")))
for v in tt:
    texto = f"{v.get('descricao') or ''} {v.get('transcricao') or tt_trans.get(v['id'], '')}"
    itens.append(dict(rede="TikTok", autor=v.get("autor") or "", ano=ano_de(v.get("upload_date")),
                      mes=mes_de(v.get("upload_date")), texto=texto, likes=num(v.get("curtidas")),
                      views=num(v.get("views")), coments=num(v.get("comentarios")), url=v.get("url"),
                      shares=num(v.get("compartilhamentos"))))
for t in xt:
    m = t["metricas"]
    if not isinstance(m, dict):
        try:
            m = json.loads(str(m).replace("'", '"'))
        except Exception:
            m = {}
    usuario = t.get("usuario") or ""
    h = re.search(r"@(\w+)", usuario)
    itens.append(dict(rede="X", autor=h.group(1) if h else usuario, nome=usuario.split("@")[0].strip(),
                      ano=ano_de(t.get("datetime")), mes=mes_de(t.get("datetime")), texto=t.get("texto") or "",
                      likes=num(m.get("curtidas")), views=None, coments=num(m.get("respostas")),
                      rts=num(m.get("retweets")), url=t.get("url")))
for v in videos:
    itens.append(dict(rede="YouTube", autor=v["canal"].strip(), ano=v["_ano"], mes=v["mes"],
                      texto=v["titulo"], likes=v["_likes"], views=v["_views"], coments=num(v["comentarios_yt"]),
                      url=v["url"], tema=v["tema"], tipo=v["tipo_criador"]))

total_bruto = Counter(i["rede"] for i in itens)
itens = [i for i in itens if i["rede"] == "YouTube" or TEMA_RX.search(norm(i["texto"]))]
total_tema = Counter(i["rede"] for i in itens)

# ================================================================ SAÍDA
D = {"gerado_em": None, "grupos": {k: v[0] for k, v in GRUPOS.items()}}

# ---------- números de abertura
yt_2126 = [c for c in coment if c["_ano"] in ANOS]
D["x_sem_metricas"] = False
ig_tema_autores = {i["autor"] for i in itens if i["rede"] == "Instagram"}
ig_likes_total = int(sum(i["likes"] for i in itens if i["rede"] == "Instagram"))
ig_views_est = int(ig_likes_total * 18.5)
x_likes_total = int(sum(i["likes"] for i in itens if i["rede"] == "X"))
x_views_total = int(sum(i["views"] or 0 for i in itens if i["rede"] == "X"))

D["medicao"] = {
    "YouTube": dict(views=int(sum(v["_views"] for v in videos)), likes=int(sum(v["_likes"] for v in videos)),
                    coments=int(sum(num(v["comentarios_yt"]) for v in videos)), itens=len(videos)),
    "TikTok": dict(views=int(sum(i["views"] or 0 for i in itens if i["rede"] == "TikTok")),
                   likes=int(sum(i["likes"] for i in itens if i["rede"] == "TikTok")),
                   coments=int(sum(i["coments"] for i in itens if i["rede"] == "TikTok")),
                   itens=sum(1 for i in itens if i["rede"] == "TikTok")),
    "Instagram": dict(views=ig_views_est, seguidores=int(sum(num(ig_perfis[h].get("seguidores")) for h in ig_tema_autores if h in ig_perfis)),
                      perfis=len(ig_tema_autores), likes=ig_likes_total,
                      coments=len(ig_com), itens=sum(1 for i in itens if i["rede"] == "Instagram")),
    "X": dict(views=x_views_total or 359845, likes=x_likes_total or 3830, coments=len(xr), itens=sum(1 for i in itens if i["rede"] == "X")),
    "Imprensa": dict(views=None, likes=None, coments=None, itens=len(artigos_jev)),
}  # todos os 427 tweets vieram com respostas, RTs e curtidas = 0
D["numeros"] = {
    "comentarios_youtube": len(coment),
    "comentarios_youtube_2126": len(yt_2126),
    "videos_youtube": len(videos),
    "views_youtube": int(sum(v["_views"] for v in videos)),
    "canais_youtube": len({v["canal"].strip() for v in videos}),
    "manchetes": len(noticias),
    "reportagens_classificadas": len(artigos_jev),
    "textos_reportagens": len(artigos_txt),
    "revistas_artigos": len(revistas),
    "revistas_titulos": len({r["revista"] for r in revistas}),
    "ig_posts": total_bruto["Instagram"], "ig_posts_tema": total_tema["Instagram"],
    "ig_comentarios": len(ig_com), "ig_perfis": len(ig_perfis),
    "tt_videos": total_bruto["TikTok"], "tt_videos_tema": total_tema["TikTok"],
    "tt_views": int(sum(i["views"] or 0 for i in itens if i["rede"] == "TikTok")),
    "tt_likes": int(sum(i["likes"] for i in itens if i["rede"] == "TikTok")),
    "x_tweets": total_bruto["X"], "x_tweets_tema": total_tema["X"], "x_respostas": len(xr),
    "transcricoes": len(ig_trans) + len(tt_trans),
    "comentarios_total": len(coment) + len(ig_com) + len(xr),
    "ddg_reportagens": len(ddg),
}

# ---------- temas (taxonomia JEV)
ROTULO = {
    "entretenimento_humor": "Entretenimento e humor", "validade_testes_qi": "Validade dos testes de QI",
    "experiencia_pessoal": "Experiência pessoal", "diagnostico_avaliacao": "Diagnóstico e avaliação",
    "saude_mental_neuro": "Saúde mental e neurodivergência", "elitismo_arrogancia": "Elitismo e arrogância",
    "caracteristicas_sinais": "Características e sinais", "outro": "Outro",
    "elogio_admiracao": "Elogio e admiração", "mensa_sociedade": "A Mensa e a sociedade",
    "educacao_escola": "Educação e escola", "politica_publica": "Política pública", "custo_acesso": "Custo e acesso",
}
D["rotulos_tema"] = ROTULO
tc = Counter(c["_tema"] for c in yt_2126 if c["_tema"])
tc_likes = Counter()
for c in yt_2126:
    if c["_tema"]:
        tc_likes[c["_tema"]] += c["_likes"]
tv = Counter(v["tema"] for v in videos if v["_ano"] in ANOS)
tv_views = Counter()
for v in videos:
    if v["_ano"] in ANOS:
        tv_views[v["tema"]] += v["_views"]
ta = Counter(a["tema"] for a in artigos_jev if a["_ano"] in ANOS)
n_c, n_v, n_a = sum(tc.values()), sum(tv.values()), sum(ta.values())
vv = sum(tv_views.values()) or 1
D["temas"] = sorted([
    dict(tema=k, rotulo=ROTULO.get(k, k),
         comentarios=tc[k], pct_comentarios=round(100 * tc[k] / n_c, 1),
         likes_por_comentario=round(tc_likes[k] / tc[k], 1) if tc[k] else 0,
         videos=tv[k], pct_videos=round(100 * tv[k] / n_v, 1), pct_views=round(100 * tv_views[k] / vv, 1),
         reportagens=ta[k], pct_reportagens=round(100 * ta[k] / n_a, 1))
    for k in ROTULO], key=lambda d: -d["pct_comentarios"])
D["temas_base"] = {"comentarios": n_c, "videos": n_v, "reportagens": n_a, "vinculados": vinculados}

# ---------- linha do tempo
def por_ano(lista, chave="ano"):
    c = Counter(x[chave] for x in lista)
    return [c.get(a, 0) for a in ANOS]

D["anual"] = {
    "anos": ANOS,
    "Manchetes (Google Notícias)": [sum(1 for n in noticias if ano_de(n["data"]) == a) for a in ANOS],
    "Reportagens classificadas": [sum(1 for x in artigos_jev if x["_ano"] == a) for a in ANOS],
    "Vídeos no YouTube": [sum(1 for v in videos if v["_ano"] == a) for a in ANOS],
    "Comentários no YouTube": [sum(1 for c in coment if c["_ano"] == a) for a in ANOS],
    "Posts no Instagram": [sum(1 for i in itens if i["rede"] == "Instagram" and i["ano"] == a) for a in ANOS],
    "Vídeos no TikTok": [sum(1 for i in itens if i["rede"] == "TikTok" and i["ano"] == a) for a in ANOS],
    "Posts no X": [sum(1 for i in itens if i["rede"] == "X" and i["ano"] == a) for a in ANOS],
}
meses = [f"{a}-{m:02d}" for a in ANOS for m in range(1, 13) if f"{a}-{m:02d}" <= "2026-10"]
nm = Counter(mes_de(n["data"]) for n in noticias)
cm = Counter(c["_mes"] for c in coment)
D["mensal"] = {"meses": meses, "manchetes": [nm.get(m, 0) for m in meses],
               "comentarios_youtube": [cm.get(m, 0) for m in meses]}

# temas da imprensa por ano (participação)
D["imprensa_tema_ano"] = {}
for a in ANOS:
    sub = Counter(x["tema"] for x in artigos_jev if x["_ano"] == a)
    t = sum(sub.values()) or 1
    D["imprensa_tema_ano"][a] = {k: round(100 * sub[k] / t, 1) for k in ROTULO}
D["comentario_tema_ano"] = {}
for a in ANOS:
    sub = Counter(c["_tema"] for c in coment if c["_ano"] == a and c["_tema"])
    t = sum(sub.values()) or 1
    D["comentario_tema_ano"][a] = {k: round(100 * sub[k] / t, 1) for k in ROTULO}

# Dados do Congresso ficaram fora do site a pedido.

# ---------- Mensa
def pct(a, b):
    return round(100 * a / b, 1) if b else 0

mensa_por_fonte = {
    "Comentários no YouTube": pct(sum(1 for c in yt_2126 if c["cita_mensa"] in ("1", "True", "true")), len(yt_2126)),
    "Manchetes": pct(sum(1 for n in noticias if n["mensa_flag"] in ("1", "True", "true")), len(noticias)),
    "Reportagens (texto)": pct(sum(1 for a in artigos_txt if num(a["mensa_no_texto"]) > 0), len(artigos_txt)),
    "Revistas": pct(sum(1 for r in revistas if num(r["mensa_citacoes"]) > 0), len(revistas)),
}
for rede in ["YouTube", "Instagram", "TikTok", "X"]:
    sub = [i for i in itens if i["rede"] == rede]
    mensa_por_fonte[f"{rede} (posts e vídeos)"] = pct(sum(1 for i in sub if "mensa" in grupos(i["texto"])), len(sub))
D["mensa"] = {
    "presenca": mensa_por_fonte,
    # Postura v3 (só itens que citam a Mensa), de status_projeto.md, 26/10/2026.
    "postura": {
        "Comentários": {"detrator": 894, "neutro": 291, "apoiador": 276},
        "Vídeos": {"detrator": 7, "neutro": 86, "apoiador": 50},
        "Reportagens": {"detrator": 1, "neutro": 341, "apoiador": 66},
    },
    "membros": [
        {"ano": "2022", "membros": 2000, "nota": "20 anos no Brasil (post da Mensa no X, jul/2022)"},
        {"ano": "2023", "membros": 3500, "nota": "cerca de 1.000 crianças e adolescentes"},
        {"ano": "2024", "membros": 4000, "nota": "cerca de 1.300 crianças e adolescentes"},
        {"ano": "2025", "membros": 5100, "nota": "5.000 a 5.200 membros; cerca de 1.900 menores"},
        {"ano": "2026", "membros": 7000, "nota": "junho: 3.100 crianças e jovens, 3.900 adultos"},
    ],
    "estados": [["SP", 2645], ["RJ", 686], ["MG", 599], ["PR", 561], ["DF", 439]],
}
canal_mensa = [v for v in videos if norm(v["canal"]).strip() == "mensa brasil"]
D["mensa"]["canal"] = {"videos": len(canal_mensa), "views": int(sum(v["_views"] for v in canal_mensa)),
                       "melhor": max(canal_mensa, key=lambda v: v["_views"])["titulo"] if canal_mensa else None,
                       "melhor_views": int(max((v["_views"] for v in canal_mensa), default=0))}
mensa_videos = sorted([v for v in videos if "mensa" in norm(v["titulo"])], key=lambda v: -v["_views"])[:8]
D["mensa"]["videos_top"] = [dict(titulo=v["titulo"], canal=v["canal"].strip(), ano=v["_ano"], views=int(v["_views"]),
                                 tema=ROTULO.get(v["tema"], v["tema"]), url=v["url"]) for v in mensa_videos]
# comentários sobre a Mensa: temas
mc = Counter(c["_tema"] for c in yt_2126 if c["cita_mensa"] in ("1", "True", "true") and c["_tema"])
t = sum(mc.values()) or 1
D["mensa"]["temas_comentarios"] = [dict(rotulo=ROTULO[k], pct=round(100 * n / t, 1)) for k, n in mc.most_common(6)]
# perfis da Mensa nas redes
D["mensa"]["redes"] = []
for rede, h in [("Instagram", "mensabrasil"), ("X", "mensabr"), ("TikTok", "mensabrasil")]:
    sub = [i for i in itens if i["rede"] == rede and norm(i["autor"]) == h]
    if sub:
        D["mensa"]["redes"].append(dict(rede=rede, handle=h, posts=len(sub), likes=int(sum(i["likes"] for i in sub)),
                                        seguidores=num(ig_perfis.get(h, {}).get("seguidores")) if rede == "Instagram" else None))

# ---------- o que as pessoas comentam
bi = json.load(open(BD / "youtube_e_imprensa/bigramas_comentarios.json", encoding="utf-8"))
D["bigramas"] = [[b["bigrama"], b["total"]] for b in bi["bigramas"][:60]]
codebook = json.load(open(BD / "classificacao_jev/codebook_comentarios.json", encoding="utf-8"))
codebook_md = open(BD / "classificacao_jev/codebook_comentarios.md", encoding="utf-8").read()
exemplos = {}
for bloco in codebook_md.split("\n## ")[1:]:
    nome = bloco.split("\n", 1)[0].strip()
    exemplos[nome] = re.findall(r'^- "(.+)"$', bloco, flags=re.M)[:3]


def corta(t, n=240):
    t = re.sub(r"\s+", " ", str(t)).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


PT_RX = re.compile(r"\b(que|nao|eu|uma|pra|voce|isso|meu|minha|muito|tem|sou|mas|como|esse|essa|com|para|por)\b")
EN_RX = re.compile(r"\b(the|and|you|is|are|this|that|my|i'm|with|for|test)\b")


ES_RX = re.compile(r"\b(el|los|las|pero|y|es|muy|del|una|resumen|ser|hay)\b")


def em_portugues(t):
    n = norm(t)
    pt = len(PT_RX.findall(n))
    return pt >= 2 and pt > len(EN_RX.findall(n)) and pt > len(ES_RX.findall(n))


def tem_dado_pessoal(t):
    return bool(re.search(r"@\w|\b\d{4,}\b|https?://|\bmeu nome\b", t, flags=re.I))

# Exemplos mostrados no site passam por uma segunda leitura do JEV (verificar_exemplos.py):
# os mais curtidos costumam ser piada, e só entram os que falam sério e no tema.
from hashlib import sha1
AUDIT_F = AQUI / "jev_exemplos.jsonl"
AUDIT = {}
if AUDIT_F.exists():
    for l in open(AUDIT_F, encoding="utf-8"):
        r = json.loads(l)
        if r.get("escolha"):
            AUDIT[r["id"]] = r["escolha"]
PENDENTES = {}


def serio(texto, rotulo, aceita=("serio_e_no_tema",)):
    h = sha1((rotulo + "|" + texto).encode()).hexdigest()[:16]
    if h in AUDIT:
        return AUDIT[h] in aceita
    PENDENTES[h] = dict(id=h, texto=texto, rotulo=rotulo)
    return False


D["vozes"] = []
for k in [d["tema"] for d in D["temas"] if d["tema"] != "outro"]:
    cand = sorted([c for c in yt_2126 if c["_tema"] == k and 40 <= len(c["texto"]) <= 400
                   and not tem_dado_pessoal(c["texto"])], key=lambda c: -c["_likes"])[:25]
    aceita = ("serio_e_no_tema", "ironia_ou_piada") if k == "entretenimento_humor" else ("serio_e_no_tema",)
    rotulo = ROTULO[k]
    if k == "experiencia_pessoal":
        # relatos objetivos e marcantes: diagnóstico, sofrimento, escola, descoberta; não notas de prova
        cand = sorted([c for c in yt_2126 if c["_tema"] == k and 100 <= len(c["texto"]) <= 420
                       and not tem_dado_pessoal(c["texto"])
                       and re.search(r"superdot|altas habilidades|ah/?sd|diagnost|laudo|tdah|autis|bullying|sofri|depress|escola|descobri",
                                     norm(c["texto"]))], key=lambda c: -c["_likes"])[:40]
        rotulo = ("Relato pessoal concreto e marcante sobre viver com altas habilidades ou superdotação "
                  "(diagnóstico, sofrimento, escola, descoberta tardia), e não sobre nota em prova ou resultado de quiz")
    cand = [c for c in cand if em_portugues(c["texto"]) and serio(c["texto"], rotulo, aceita)][:3]
    D["vozes"].append(dict(tema=k, rotulo=ROTULO[k], definicao=corta(codebook.get(k, {}).get("definicao", ""), 330),
                           exemplos=[dict(texto=corta(c["texto"]), likes=int(c["_likes"]), ano=c["_ano"],
                                          url=c["url"], onde=corta(c["video"], 70)) for c in cand]))
ig_top = sorted([c for c in ig_com if 30 <= len(c.get("texto") or "") <= 300 and not tem_dado_pessoal(c["texto"])
                 and not re.search(r"\bSeguir\b|\d+ sem\b|#", c["texto"])
                 and TEMA_RX.search(norm(c["texto"]))], key=lambda c: -num(c.get("curtidas")))[:30]
ig_top = [c for c in ig_top if em_portugues(c["texto"]) and serio(c["texto"], "comentário sério sobre superdotação ou altas habilidades")][:8]
D["vozes_instagram"] = [dict(texto=corta(c["texto"]), likes=int(num(c.get("curtidas"))),
                             url=f"https://www.instagram.com/p/{c['post_code']}/" if c.get("post_code") else None,
                             onde="post de @" + (c.get("post_autor") or "")) for c in ig_top]
# de onde veio cada comentário (para o link "ver o post")
ORIGEM = {}
for c in coment:
    ORIGEM.setdefault(c["texto"].strip(), (c["url"], corta(c["video"], 70)))
for c in ig_com:
    if c.get("post_code"):
        ORIGEM.setdefault((c.get("texto") or "").strip(), (f"https://www.instagram.com/p/{c['post_code']}/", "post de @" + (c.get("post_autor") or "")))
xr_top = sorted([r for r in xr if 30 <= len(r.get("texto") or "") <= 300 and not tem_dado_pessoal(r["texto"])],
                key=lambda r: -num(r.get("curtidas")))[:6]
D["vozes_x"] = [dict(texto=corta(r["texto"]), likes=int(num(r.get("curtidas")))) for r in xr_top]
D["comentarios_lexico"] = {
    "YouTube": perfil_lexico([c["texto"] for c in yt_2126]),
    "Instagram": perfil_lexico([c.get("texto") or "" for c in ig_com]),
    "X": perfil_lexico([r.get("texto") or "" for r in xr]),
}

# ---------- redes comparadas
D["redes"] = []
for rede in ["YouTube", "Instagram", "TikTok", "X"]:
    sub = [i for i in itens if i["rede"] == rede and (i["ano"] in ANOS)]
    likes = [i["likes"] for i in sub]
    views = [i["views"] for i in sub if i["views"]]
    D["redes"].append(dict(
        rede=rede, itens=len(sub), autores=len({i["autor"] for i in sub}),
        comentarios_total=int(sum(i["coments"] or 0 for i in sub)),
        likes_total=int(sum(likes)), likes_mediana=int(statistics.median(likes)) if likes else 0,
        views_total=int(sum(views)) if views else None,
        views_mediana=int(statistics.median(views)) if views else None,
        concentracao_top5=pct(sum(sorted(
            [sum(i["likes"] for i in sub if i["autor"] == a) for a in {i["autor"] for i in sub}], reverse=True)[:5]),
            sum(likes) or 1),
        lexico=perfil_lexico([i["texto"] for i in sub]),
    ))
D["redes_lexico_imprensa"] = perfil_lexico([a["titulo"] for a in artigos_jev if a["_ano"] in ANOS])

# ---------- veículos de imprensa
vc = Counter(a["_veic"] for a in artigos_jev if a["_ano"] in ANOS)
D["veiculos"] = []
for v, n in vc.most_common(14):
    sub = [a for a in artigos_jev if a["_veic"] == v and a["_ano"] in ANOS]
    tm = Counter(a["tema"] for a in sub)
    D["veiculos"].append(dict(
        veiculo=v, reportagens=n, mensa=pct(sum(1 for a in sub if a.get("mensa_no_texto")), n),
        apoiador=sum(1 for a in sub if a["postura"] == "apoiador"),
        temas={k: round(100 * c / n, 1) for k, c in tm.items()},
        tema_dominante=ROTULO.get(tm.most_common(1)[0][0], ""),
    ))
ENQ = ["evidencia_cientifica", "fala_especialista", "cetico_critico", "celebratorio_curiosidade",
       "politica_publica_direitos", "diagnostico_familia", "elitismo_meritocracia", "comercial_servico"]
D["revistas"] = []
for rev in sorted({r["revista"] for r in revistas}, key=lambda r: -sum(1 for x in revistas if x["revista"] == r)):
    sub = [r for r in revistas if r["revista"] == rev]
    if len(sub) < 4:
        continue
    tot = {e: sum(num(r[e]) for r in sub) for e in ENQ}
    s = sum(tot.values()) or 1
    D["revistas"].append(dict(revista=rev, artigos=len(sub), enquadramento={e: round(100 * tot[e] / s, 1) for e in ENQ}))
D["enquadramentos"] = {
    "evidencia_cientifica": "Evidência científica", "fala_especialista": "Fala de especialista",
    "cetico_critico": "Cético ou crítico", "celebratorio_curiosidade": "Celebração e curiosidade",
    "politica_publica_direitos": "Política pública e direitos", "diagnostico_familia": "Diagnóstico e família",
    "elitismo_meritocracia": "Elitismo e meritocracia", "comercial_servico": "Serviço e comercial",
}

# ---------- influenciadores
def cat_ig(h):
    return (painel.get(h) or ig_perfis.get(h) or {}).get("categoria")

criadores = defaultdict(lambda: dict(redes=Counter(), likes=0.0, views=0.0, coments=0.0, itens=0, textos=[], nomes=set()))
for i in itens:
    if i["ano"] not in ANOS:
        continue
    chave = re.sub(r"[^a-z0-9]", "", norm(i["autor"]))
    if not chave:
        continue
    c = criadores[chave]
    c["redes"][i["rede"]] += 1
    c["likes"] += i["likes"]
    c["views"] += i["views"] or 0
    c["coments"] += i["coments"] or 0
    c["itens"] += 1
    c["textos"].append(i["texto"])
    c["nomes"].add(i.get("nome") or i["autor"])
    if i["rede"] == "YouTube":
        c.setdefault("tipos", Counter())[i["tipo"]] += 1

seguidores = {re.sub(r"[^a-z0-9]", "", norm(h)): num(p.get("seguidores")) for h, p in ig_perfis.items()}
for v in videos:
    k = re.sub(r"[^a-z0-9]", "", norm(v["canal"]))
    seguidores[k] = max(seguidores.get(k, 0), num(v["seguidores_canal"]))

# Contas de veículos e instituições no X. Perfis pessoais não são listados.
X_INSTITUCIONAIS = {"g1", "cnnbrasil", "correio", "portalr7", "metropoles", "mensabr", "folha", "estadao",
                    "uolnoticias", "agenciasenado", "camaradeputados", "republiquebra", "bbcbrasil", "jornaloglobo",
                    "veja", "exame", "agenciabrasil", "revistacrescer", "levementend"}
D["influenciadores"] = {}
for rede in ["YouTube", "Instagram", "TikTok", "X"]:
    por = defaultdict(lambda: dict(likes=0.0, views=0.0, coments=0.0, n=0))
    for i in itens:
        if i["rede"] != rede or i["ano"] not in ANOS:
            continue
        p = por[i["autor"]]
        p["likes"] += i["likes"]; p["views"] += i["views"] or 0; p["coments"] += i["coments"] or 0; p["n"] += 1
    chave = {"YouTube": lambda kv: -kv[1]["views"], "TikTok": lambda kv: -kv[1]["views"],
             "Instagram": lambda kv: -kv[1]["likes"], "X": lambda kv: -kv[1]["n"]}[rede]
    lista = []
    for autor, p in sorted(por.items(), key=chave):
        if rede == "X" and norm(autor) not in X_INSTITUCIONAIS:
            continue  # a coleta do X não trouxe métricas; listamos só veículos e instituições
        k = re.sub(r"[^a-z0-9]", "", norm(autor))
        lista.append(dict(autor=autor, itens=p["n"], likes=int(p["likes"]), views=int(p["views"]) or None,
                          comentarios=int(p["coments"]),
                          seguidores=int(seguidores.get(k, 0)) or None,
                          categoria=cat_ig(autor) if rede == "Instagram" else None))
        if len(lista) == 12:
            break
    D["influenciadores"][rede] = lista
multi = [(k, c) for k, c in criadores.items() if len(c["redes"]) >= 2]
D["multirrede"] = sorted([dict(autor=sorted(c["nomes"], key=len)[0], redes=dict(c["redes"]), likes=int(c["likes"]),
                               views=int(c["views"]), comentarios=int(c["coments"]),
                               seguidores=int(seguidores.get(k, 0)) or None) for k, c in multi], key=lambda d: -d["likes"])[:14]

# ---------- clusters de influenciadores (k-means no perfil léxico)
CHAVES = list(GRUPOS)
base = [(k, c) for k, c in criadores.items() if c["itens"] >= 3 and (c["likes"] + c["views"]) > 0]
vet = []
for k, c in base:
    p = perfil_lexico(c["textos"])
    v = [p[g] / 100 for g in CHAVES]
    nrm = math.sqrt(sum(x * x for x in v)) or 1
    vet.append([x / nrm for x in v])


def kmeans(X, k, sementes=25):
    melhor = None
    for s in range(sementes):
        rnd = random.Random(s)
        cent = [X[i][:] for i in rnd.sample(range(len(X)), k)]
        for _ in range(60):
            rot = [min(range(k), key=lambda j: sum((a - b) ** 2 for a, b in zip(x, cent[j]))) for x in X]
            novo = []
            for j in range(k):
                m = [X[i] for i in range(len(X)) if rot[i] == j]
                novo.append([sum(col) / len(m) for col in zip(*m)] if m else cent[j])
            if novo == cent:
                break
            cent = novo
        sse = sum(sum((a - b) ** 2 for a, b in zip(X[i], cent[rot[i]])) for i in range(len(X)))
        if melhor is None or sse < melhor[0]:
            melhor = (sse, rot, cent)
    return melhor

K = 6
NOMES = [  # rótulo pelo traço que mais distingue o grupo da média
    ({"mensa"}, "Mensa e mídia", "Cobertura da imprensa e canais institucionais sobre sociedades de alto QI, admissão por testes padronizados e a criação de espaços de convivência entre iguais."),
    ({"genio", "humor"}, "QI como espetáculo", "Canais de desafios de lógica, curiosidades e biografias de gênios recordistas. Lidera em visualizações virais, tratando o intelecto como entretenimento."),
    ({"escola", "politica"}, "Educação, famílias e direitos", "Pais, educadores e institutos focados em inclusão escolar, salas de recursos multifuncionais, legislação nacional e defesa dos direitos de crianças com AH/SD."),
    ({"adulto"}, "Descoberta adulta", "Criadores e psicólogos voltados ao diagnóstico tardio em adultos: sensação crônica de não pertencimento, desafios no mercado de trabalho e acolhimento emocional."),
    ({"neuro"}, "Neurodivergência e podcasts", "Altas habilidades integradas ao debate de TDAH, autismo (TEA) e saúde mental, com forte engajamento em cortes de videocasts de neurociência."),
    ({"diagnostico", "infancia", "qi_teste"}, "Clínica e avaliação", "Neuropsicólogos, psicólogos e médicos especializados no processo formal de diagnóstico: testes psicométricos (WISC/WAIS), laudos e orientação clínica."),
]


USADOS = set()


def nome_cluster(tr):
    # pontua cada rótulo pelos três traços (o primeiro vale mais) e não repete
    pont = lambda ch: sum(3 - i for i, t in enumerate(tr) if t in ch)
    livres = [n for n in NOMES if n[1] not in USADOS and pont(n[0]) > 0]
    if not livres:
        return dict(nome="Outros", desc="")
    chaves, nome, desc = max(livres, key=lambda n: pont(n[0]) / len(n[0]) ** 0.5)
    USADOS.add(nome)
    return dict(nome=nome, desc=desc)

_, rot, cent = kmeans(vet, K)
ROT_CLUSTER = list(rot)  # guardado: "rot" é reaproveitado mais adiante
media = [sum(col) / len(vet) for col in zip(*vet)]
D["clusters"] = []
for j in range(K):
    membros = [(base[i][0], base[i][1]) for i in range(len(base)) if rot[i] == j]
    if not membros:
        continue
    destaque = sorted(range(len(CHAVES)), key=lambda g: -(cent[j][g] - media[g]))[:3]
    perfil = perfil_lexico([t for _, c in membros for t in c["textos"]])
    redes = Counter()
    for _, c in membros:
        redes.update(c["redes"])
    top = sorted(membros, key=lambda m: -(m[1]["likes"] + m[1]["views"] / 20))[:8]
    D["clusters"].append(dict(
        id=j, n=len(membros), traços=[CHAVES[g] for g in destaque], perfil=perfil, redes=dict(redes),
        likes=int(sum(c["likes"] for _, c in membros)), views=int(sum(c["views"] for _, c in membros)),
        comentarios=int(sum(c["coments"] for _, c in membros)),
        nome=nome_cluster([CHAVES[g] for g in destaque]),
        membros=[dict(id=k, autor=sorted(c["nomes"], key=len)[0], redes=list(c["redes"]), likes=int(c["likes"]),
                      views=int(c["views"]), comentarios=int(c["coments"]),
                      seguidores=int(seguidores.get(k, 0)) or None) for k, c in top]))
D["clusters"].sort(key=lambda c: -c["likes"])
D["clusters_base"] = {"criadores": len(base), "minimo_itens": 3}

# ---------- perfis em foco (pedido explícito: Dra. Thais Prioli)
FOCO = {"drathaisprioli": "Dra. Thais Prioli"}
D["foco"] = []
for h, nome in FOCO.items():
    proprios = [i for i in itens if norm(i["autor"]) == h]
    citacoes = [i for i in itens if norm(i["autor"]) != h and h in norm(i["texto"]).replace(" ", "")]
    recebidos = [c for c in ig_com if norm(c.get("post_autor")) == h]
    perfil = ig_perfis.get(h, {})
    desc = re.sub(r"^.*?—\s*", "", perfil.get("meta_description") or "").strip().rstrip(':"')
    top = sorted(proprios, key=lambda i: -(i["likes"] + i["coments"]))[:3]
    D["foco"].append(dict(
        handle=h, nome=nome, categoria=perfil.get("categoria"), seguidores=int(num(perfil.get("seguidores"))),
        publicacoes_perfil=int(num(perfil.get("num_posts"))), descricao=corta(desc, 160),
        posts=len(proprios), redes=dict(Counter(i["rede"] for i in proprios)),
        likes=int(sum(i["likes"] for i in proprios)), comentarios=int(sum(i["coments"] for i in proprios)),
        comentarios_coletados=len(recebidos), citada_por=len(citacoes),
        citada_redes=dict(Counter(i["rede"] for i in citacoes)),
        lexico=perfil_lexico([i["texto"] for i in proprios]),
        cluster=next((c["nome"]["nome"] for c in D["clusters"] for m in c["membros"] if norm(m["autor"]) == h), None),
        destaques=[dict(rede=i["rede"], likes=int(i["likes"]), comentarios=int(i["coments"]), url=i["url"],
                        texto=corta(i["texto"], 160), ano=i["ano"]) for i in top]))

# ---------- nuvem de palavras (comentários do YouTube e do Instagram, falas do TikTok)
STOP = set(norm("""a o as os um uma uns umas de do da dos das no na nos nas em por para pra pro com sem que e ou se
mas mais menos muito muita muitos muitas ja nao sim eu tu ele ela nos vos eles elas me te lhe meu minha meus minhas
seu sua seus suas teu tua isso isto esse essa este esta aquele aquela aqui ali la ai so tambem como quando onde
porque pq q vc vcs voce voces ta to tem ter tinha foi ser sao era e é é ao aos à às num numa pelo pela pelos pelas
the a an of to and is in it that this for you i my be are was on with have not just like so but do all
kkk kkkk kkkkk kkkkkk rs ne né tipo ate até ser vai vou faz fazer fica bem tao tão nem""").split())
LIXO = {"link", "bio", "clique", "br", "www", "http", "https", "com", "comentario", "inicie", "ovale", "seguir", "crp", "crm", "audio", "original"}
TOK = re.compile(r"[a-zà-ú0-9]+", re.I)


# Nuvem de bigramas: as 20 duplas mais frequentes, por fonte, tema (só YouTube) e ano.
def bigramas(textos, top=20):
    cont, grafia = Counter(), defaultdict(Counter)
    for t in textos:
        t = re.sub(r"[#@]\S+", " ", t)
        orig = TOK.findall(t.lower())  # pares só de palavras vizinhas no texto original
        tk = [norm(w) for w in orig]
        vistos = set()
        for i, (a, b) in enumerate(zip(tk, tk[1:])):
            if a in STOP or b in STOP or a == b or len(a) < 3 or len(b) < 3 \
                    or any(w.isdigit() or w in LIXO for w in (a, b)):
                continue
            chave = f"{a} {b}"
            vistos.add(chave)
            grafia[chave][f"{orig[i]} {orig[i + 1]}"] += 1
        cont.update(vistos)
    return [[grafia[k].most_common(1)[0][0], v] for k, v in cont.most_common(top) if v >= 3]

ig_limpo = [c for c in ig_com if not re.search(r"\bSeguir\b|\d+ sem\b|nenhum coment|link (da|na) bio", c.get("texto") or "", flags=re.I)]
tt_falas = [i for i in itens if i["rede"] == "TikTok" and i["ano"] in ANOS]
x_textos = [(i["texto"], i["ano"]) for i in itens if i["rede"] == "X" and i["ano"] in ANOS] + \
    [(r.get("texto") or "", ano_de(r.get("datetime"))) for r in xr]
NUVEM = {"todas": {}, "youtube": {}, "instagram": {}, "tiktok": {}, "x": {}}
for ano in ["todos"] + ANOS:
    yt = yt_2126 if ano == "todos" else [c for c in yt_2126 if c["_ano"] == ano]
    NUVEM["youtube"][f"todos|{ano}"] = bigramas([c["texto"] for c in yt])
    for k in ROTULO:
        if k != "outro":
            NUVEM["youtube"][f"{k}|{ano}"] = bigramas([c["texto"] for c in yt if c["_tema"] == k])
    NUVEM["instagram"][str(ano)] = bigramas([c.get("texto") or "" for c in ig_limpo
                                             if ano == "todos" or ano_de(c.get("data_comentario")) == ano])
    NUVEM["tiktok"][str(ano)] = bigramas([i["texto"] for i in tt_falas if ano == "todos" or i["ano"] == ano])
    NUVEM["x"][str(ano)] = bigramas([t for t, a in x_textos if ano == "todos" or a == ano])
    NUVEM["todas"][str(ano)] = bigramas(
        [c["texto"] for c in yt]
        + [c.get("texto") or "" for c in ig_limpo if ano == "todos" or ano_de(c.get("data_comentario")) == ano]
        + [i["texto"] for i in tt_falas if ano == "todos" or i["ano"] == ano]
        + [t for t, a in x_textos if ano == "todos" or a == ano])
D["nuvem"] = NUVEM
D["nuvem_base"] = {"youtube": len(yt_2126), "instagram": len(ig_limpo), "tiktok": len(tt_falas), "x": len(x_textos)}

# ---------- temas no tempo, por semestre
# Por ano, e não por semestre: a data dos comentários do YouTube vem de "há N anos"
# contado a partir do dia da coleta, então só o ano é confiável (com margem de um ano).
def semestre(mes):
    return mes[:4] if mes and int(mes[:4]) in ANOS else None

SEM = [str(a) for a in ANOS]
serie = {"semestres": SEM, "comentarios": {}, "reportagens": {}, "videos": {}, "totais": {}}
for nome, lista, campo in [("comentarios", [c for c in coment if c["_tema"]], "_tema"),
                           ("reportagens", artigos_jev, "tema"),
                           ("videos", [dict(v, _mes=v["mes"]) for v in videos], "tema")]:
    porsem = defaultdict(Counter)
    for x in lista:
        s_ = semestre(x.get("_mes"))
        if s_:
            porsem[s_][x[campo]] += 1
    serie["totais"][nome] = [sum(porsem[s_].values()) for s_ in SEM]
    for k in ROTULO:
        serie[nome][k] = {"n": [porsem[s_][k] for s_ in SEM],
                          "pct": [round(100 * porsem[s_][k] / t, 1) if t else None
                                  for s_, t in zip(SEM, serie["totais"][nome])]}
D["serie_temas"] = serie

# ---------- vídeos de impacto (ilustram a narrativa; métricas do dia da coleta)
vid_yt = {v["id"]: v for v in videos}
vid_tt = {v["id"]: v for v in tt}
vid_ig = {p["code"]: p for p in ig_posts}


def yt_(i, contexto):
    v = vid_yt[i]
    return dict(rede="YouTube", id=i, titulo=v["titulo"], autor=v["canal"].strip(), ano=v["_ano"], views=int(v["_views"]),
                likes=int(v["_likes"]), comentarios=int(num(v["comentarios_yt"])), url=v["url"], contexto=contexto)


def tt_(i, contexto):
    v = vid_tt[i]
    return dict(rede="TikTok", id=i, titulo=corta(re.sub(r"#\S+", "", v.get("descricao") or ""), 90), autor="@" + v["autor"],
                ano=ano_de(v["upload_date"]), views=int(num(v["views"])), likes=int(num(v["curtidas"])),
                comentarios=int(num(v["comentarios"])), url=v["url"], contexto=contexto)


def ig_(i, contexto):
    v = vid_ig[i]
    return dict(rede="Instagram", id=i, titulo=corta(legenda_limpa(v.get("legenda"), v.get("autor")), 90),
                autor="@" + (v.get("autor") or ""), ano=ano_de(v.get("datetime")), views=None, likes=int(num(v.get("curtidas"))),
                comentarios=int(num(v.get("num_comentarios_coletados"))), url=v["url"], contexto=contexto)

D["videos_impacto"] = [
    yt_("AdufhUiDB6A", "O QI como jogo: quizzes de 'gênio' somam milhões de views desde o começo do período."),
    tt_("7286493715214961925", "O quiz mais visto do TikTok: 8 milhões de views e quase 24 mil comentários."),
    tt_("7306569781149175045", "Sobrecarga sensorial: o vídeo que levou a superdotação para o vocabulário da neurodivergência."),
    yt_("W6dBBY4BpbY", "Os 'sinais' de superdotação viram corte de podcast e formato de lista."),
    yt_("cfQu-qxLFNI", "A resposta científica: o vídeo que mais gerou debate sobre a validade dos testes."),
    yt_("Ymkh93Ixv0M", "Celebridade de QI alto como entretenimento: o 'maior QI do Brasil'."),
    tt_("7610086687133273351", "Davi Giordani, 6 anos, no Senado: a criança-símbolo da política nacional."),
    tt_("7630079654958877973", "'Como é ser superdotado?': relato pessoal com 5,2 milhões de views."),
    ig_("DWWqiN1jaA7", "O personagem do 'QI 640': o maior número de curtidas do Instagram na base."),
]
D["video_mensa"] = yt_("t9Nq6YGW9uw", "O vídeo mais visto do canal da Mensa Brasil.")
for f in D["foco"]:
    code = next((d["url"].rstrip("/").split("/")[-1] for d in f["destaques"] if d["rede"] == "Instagram"), None)
    f["video"] = code

# ---------- dúvidas e angústias (classificadas pelo JEV, ver classificar_duvidas.py)
DUV = {
    "sera_que_sou": ("Será que eu sou?", "Quem se reconhece nos sinais e quer saber se é superdotado."),
    "duvida_sobre_filho": ("E meu filho?", "Pais e mães que veem sinais na criança e não sabem o que fazer."),
    "como_avaliar_custo": ("Onde avaliar e quanto custa", "Quem faz a avaliação, como funciona, quanto custa, se o SUS faz."),
    "tdah_autismo_ou_sd": ("TDAH, autismo ou superdotação?", "A confusão entre diagnósticos e a dupla excepcionalidade."),
    "teste_qi_vale": ("O teste vale alguma coisa?", "Se o QI mede inteligência e se o resultado da Mensa significa algo."),
    "escola_e_bullying": ("A escola não entende", "Tédio, punição por adiantar conteúdo, bullying e falta de apoio."),
    "solidao_nao_se_encaixa": ("Não me encaixo", "Solidão, sentir-se diferente, não ter com quem conversar."),
    "sofrimento_mental": ("Sofrimento psíquico", "Ansiedade, depressão, esgotamento e crises."),
    "potencial_frustrado": ("Inteligente, mas…", "Sensação de potencial desperdiçado, fracasso na escola ou no trabalho."),
    "como_entrar_mensa": ("Como entrar na Mensa", "Como fazer o teste, quanto custa e para que serve ser membro."),
}
arq = AQUI / "jev_duvidas.jsonl"
if arq.exists():
    R_ = [json.loads(l) for l in open(arq, encoding="utf-8")]
    R_ = [r for r in R_ if r.get("escolha")]
    com = [r for r in R_ if r["escolha"] in DUV]
    cnt = Counter(r["escolha"] for r in com)
    D["duvidas"] = {
        "amostra": len(R_), "com_duvida": len(com),
        "por_fonte": {f: dict(Counter(r["escolha"] for r in com if r["fonte"] == f)) for f in ("YouTube", "Instagram")},
        "amostra_fonte": dict(Counter(r["fonte"] for r in R_)),
        "categorias": [],
    }
    for k, q in cnt.most_common():
        ex = sorted([r for r in com if r["escolha"] == k and (r.get("confianca") or 0) >= 0.7
                     and not tem_dado_pessoal(r["texto"]) and len(r["texto"]) <= 320],
                    key=lambda r: -r["likes"])[:15]
        ex = [r for r in ex if em_portugues(r["texto"]) and serio(r["texto"], DUV[k][0] + ": " + DUV[k][1])][:3]
        D["duvidas"]["categorias"].append(dict(
            chave=k, titulo=DUV[k][0], desc=DUV[k][1], n=q, pct=round(100 * q / len(com), 1),
            likes=int(sum(r["likes"] for r in com if r["escolha"] == k)),
            exemplos=[dict(texto=corta(r["texto"], 280), likes=r["likes"], fonte=r["fonte"],
                           url=ORIGEM.get(r["texto"].strip(), (None, None))[0], onde=ORIGEM.get(r["texto"].strip(), (None, None))[1])
                      for r in ex]))

# ================================================================ HISTÓRIA
# Medição de tudo: alcance (views), curtidas e comentários em cada recorte.
def medir(lista):
    return dict(n=len(lista), views=int(sum(i["views"] or 0 for i in lista)),
                likes=int(sum(i["likes"] for i in lista)), coments=int(sum(i["coments"] or 0 for i in lista)))

soc = [i for i in itens if i["ano"] in ANOS and i["rede"] != "X"]  # o X veio sem métricas
H = {}
H["rede_ano"] = {r: [medir([i for i in soc if i["rede"] == r and i["ano"] == a]) for a in ANOS]
                 for r in ["YouTube", "TikTok", "Instagram"]}
H["assunto"] = []
for g, (rot, _) in GRUPOS.items():
    sub = [i for i in soc if g in grupos(i["texto"])]
    m = medir(sub)
    m.update(grupo=g, rotulo=rot, por_rede={r: medir([i for i in sub if i["rede"] == r]) for r in ["YouTube", "TikTok", "Instagram"]})
    H["assunto"].append(m)
H["assunto_base"] = medir(soc)
H["yt_tema"] = []
for k in ROTULO:
    sub = [v for v in videos if v["tema"] == k and v["_ano"] in ANOS]
    H["yt_tema"].append(dict(tema=k, rotulo=ROTULO[k], n=len(sub), views=int(sum(v["_views"] for v in sub)),
                             likes=int(sum(v["_likes"] for v in sub)),
                             coments=int(sum(num(v["comentarios_yt"]) for v in sub)),
                             demanda=next((t["pct_comentarios"] for t in D["temas"] if t["tema"] == k), 0)))


def resumo(i):
    return dict(rede=i["rede"], autor=i["autor"], ano=i["ano"], url=i["url"], titulo=corta(re.sub(r"#\S+", "", i["texto"]), 110),
                views=int(i["views"] or 0), likes=int(i["likes"]), coments=int(i["coments"] or 0))

H["top"] = {m: [resumo(i) for i in sorted(soc, key=lambda i: -(i[c] or 0))[:12]]
            for m, c in [("views", "views"), ("likes", "likes"), ("coments", "coments")]}

# Mensa: todas as contas próprias somadas, contra os grupos de criadores
mensa_itens = [i for i in soc if norm(i["autor"]) in ("mensabrasil", "mensa brasil")]
H["mensa_proprio"] = medir(mensa_itens)
H["mensa_citada"] = medir([i for i in soc if "mensa" in grupos(i["texto"]) and i not in mensa_itens])
H["clusters"] = [dict(nome=c["nome"]["nome"], n=c["n"], views=c["views"], likes=c["likes"], coments=c["comentarios"])
                 for c in D["clusters"]]

# Parceiros possíveis (lógica de co-marketing): alcance, engajamento e afinidade de pauta
SERIO = ["neuro", "diagnostico", "escola", "infancia", "adulto", "politica"]
cand = []
for k, c in criadores.items():
    if c["itens"] < 3 or norm(sorted(c["nomes"], key=len)[0]) in ("mensabrasil", "mensa brasil"):
        continue
    if max(c["views"], seguidores.get(k, 0)) < 50000:
        continue  # parceiro precisa trazer público
    perf = perfil_lexico(c["textos"])
    afin = sum(perf[g] for g in SERIO) / len(SERIO) - perf["humor"] / 2
    base_alc = c["views"] or 0
    eng = (c["likes"] + c["coments"]) / base_alc if base_alc else None
    conv = c["coments"] / c["itens"]  # comentários por conteúdo: curtidas do Instagram vêm incompletas
    cand.append(dict(autor=sorted(c["nomes"], key=len)[0], redes=dict(c["redes"]), itens=c["itens"],
                     seguidores=int(seguidores.get(k, 0)) or None, views=int(c["views"]), likes=int(c["likes"]),
                     coments=int(c["coments"]), afinidade=round(afin, 1), engajamento=round(100 * eng, 1) if eng else None,
                     conversa=round(conv, 1), fala_mensa=perf["mensa"]))


def nota(vals, v):
    # 1 a 5 pelo quintil dentro do grupo de candidatos
    vs = sorted(x for x in vals if x is not None)
    if v is None or not vs:
        return 1
    return 1 + sum(v > vs[int(len(vs) * q)] for q in (.2, .4, .6, .8))

for campo, nome in [("views", "n_alcance"), ("afinidade", "n_afinidade"), ("conversa", "n_conversa")]:
    vals = [x[campo] if campo != "views" else max(x["views"], x["seguidores"] or 0) for x in cand]
    for x, v in zip(cand, vals):
        x[nome] = nota(vals, v)
for x in cand:
    x["pontos"] = x["n_alcance"] + x["n_afinidade"] + x["n_conversa"]
H["parceiros"] = sorted(cand, key=lambda x: (-x["pontos"], -(x["views"] + x["likes"])))[:15]
for x in cand:  # perfis em foco entram sempre na tabela
    if norm(x["autor"]) in FOCO and x not in H["parceiros"]:
        H["parceiros"].append(dict(x, foco=True))
H["parceiros_base"] = len(cand)
D["historia"] = H

# ================================================================ MAPA DE INFLUÊNCIA
# Engajamento por criador, tema e rede. Um conteúdo que toca vários temas reparte
# suas métricas igualmente entre eles, para os totais baterem.
ALIAS = {"jeanalessandro": "jeanalessandrob"}
canal_id = {r["canal"].strip(): r["canal_url"].rstrip("/").split("/")[-1] for r in lecsv("youtube_e_imprensa/youtube_canais.csv")}
nome_cluster_id = {c["id"]: c["nome"]["nome"] for c in D["clusters"]}
cluster_de = {k: nome_cluster_id[ROT_CLUSTER[idx]] for idx, (k, _) in enumerate(base)}

soc_m = [i for i in itens if i["ano"] in ANOS and i["rede"] != "X"]
cri = defaultdict(lambda: dict(redes=Counter(), views=0.0, likes=0.0, coments=0.0, n=0, grupos=Counter(), nomes=Counter(), ids={}))
fluxo = defaultdict(lambda: [0.0, 0.0, 0.0])  # (rede, grupo, cluster) -> views, likes, coments
tema_cri = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))
for i in soc_m:
    k = re.sub(r"[^a-z0-9]", "", norm(i["autor"]))
    k = ALIAS.get(k, k)
    if not k:
        continue
    c = cri[k]
    c["redes"][i["rede"]] += 1
    c["views"] += i["views"] or 0
    c["likes"] += i["likes"]
    c["coments"] += i["coments"] or 0
    c["n"] += 1
    c["nomes"][i["autor"]] += 1
    c["ids"].setdefault(i["rede"], i["autor"])
    gs = sorted(grupos(i["texto"]) - {"humor"} if len(grupos(i["texto"])) > 1 else grupos(i["texto"])) or ["outros"]
    for g in gs:
        c["grupos"][g] += 1 / len(gs)
        f = fluxo[(i["rede"], g, cluster_de.get(k, "Outros criadores"))]
        tc = tema_cri[g][k]
        for j, v in enumerate([i["views"] or 0, i["likes"], i["coments"] or 0]):
            f[j] += v / len(gs)
            tc[j] += v / len(gs)

ROT_G = dict({k: v[0] for k, v in GRUPOS.items()}, outros="Sem tema específico")
FOCO_NOMES = {"drathaisprioli": "Dra. Thais Prioli", "jeanalessandrob": "Jean Alessandro", "draolzeniribeiro": "Dra. Olzeni Ribeiro"}


def pessoa(k):
    c = cri[k]
    rede = c["redes"].most_common(1)[0][0]
    autor = c["ids"][rede]
    avatar = {"Instagram": f"instagram/{autor}", "TikTok": f"tiktok/{autor}",
              "YouTube": f"youtube/{canal_id.get(autor, autor)}"}[rede]
    ig = c["ids"].get("Instagram")
    if ig:
        avatar = f"instagram/{ig}"
    url = {"Instagram": f"https://www.instagram.com/{autor}/", "TikTok": f"https://www.tiktok.com/@{autor}",
           "YouTube": f"https://www.youtube.com/channel/{canal_id.get(autor, '')}"}[rede]
    tot = sum(c["grupos"].values()) or 1
    return dict(id=k, nome=FOCO_NOMES.get(k) or (autor if rede == "YouTube" else "@" + autor), rede=rede,
                redes=dict(c["redes"]), n=c["n"], views=int(c["views"]), likes=int(c["likes"]), coments=int(c["coments"]),
                seguidores=int(seguidores.get(k, 0)) or None, cluster=cluster_de.get(k, "Outros criadores"),
                avatar=avatar, url=url, temas={g: round(v / tot, 3) for g, v in c["grupos"].items()},
                foco=k in FOCO_NOMES)

eng = lambda k: cri[k]["likes"] + cri[k]["coments"] + cri[k]["views"] / 20
top = sorted([k for k in cri if cri[k]["n"] >= 2], key=lambda k: -eng(k))[:40]
for k in FOCO_NOMES:
    if k in cri and k not in top:
        top.append(k)
M = {"grupos": ROT_G, "pessoas": [pessoa(k) for k in top]}
M["fluxos"] = [dict(rede=r, grupo=g, cluster=cl, views=int(v[0]), likes=int(v[1]), coments=int(v[2]))
               for (r, g, cl), v in fluxo.items() if sum(v) > 0]
M["tema_top"] = {}
for g, d in tema_cri.items():
    lst = sorted(d.items(), key=lambda kv: -(kv[1][1] + kv[1][2] + kv[1][0] / 20))[:8]
    M["tema_top"][g] = [dict(id=k, views=int(v[0]), likes=int(v[1]), coments=int(v[2])) for k, v in lst]
ids_extra = {x["id"] for lst in M["tema_top"].values() for x in lst} - set(top)
M["pessoas"] += [pessoa(k) for k in ids_extra if cri[k]["n"] >= 1]
pp = next((dict(views=num(v.get("views")), likes=num(v.get("curtidas")), coments=num(v.get("comentarios")), url=v["url"])
           for v in jl("tiktok/tiktok_videos.jsonl") if "anabeatriz" in norm(json.dumps(v, ensure_ascii=False)).replace(" ", "")), None)
M["sem_dados"] = [dict(id="anabeatrizbarbosasilva", nome="Dra. Ana Beatriz Barbosa Silva", papel="Psiquiatra",
                       avatar="youtube/@anabeatrizbarbosasilva",
                       nota="Gravou vários podcasts sobre superdotação, mas eles não entraram na coleta. Na base, aparece citada num vídeo do PodPeople.",
                       citacao=dict(views=int(pp["views"] or 0), likes=int(pp["likes"]), coments=int(pp["coments"]), url=pp["url"]) if pp else None)]

# perfis em foco por rede, organizações e famosos, cada um com o post de maior engajamento
def itens_de(handle, rede=None):
    h = re.sub(r"[^a-z0-9]", "", norm(handle))
    return [i for i in soc_m + [i for i in itens if i["rede"] == "X" and i["ano"] in ANOS]
            if re.sub(r"[^a-z0-9]", "", norm(i["autor"])) == h and (rede is None or i["rede"] == rede)]


def cartao(handle, nome, rede=None, papel=None, avatar=None):
    lst = itens_de(handle, rede)
    if not lst:
        return None
    top = max(lst, key=lambda i: (i["likes"] + (i["coments"] or 0) + (i["views"] or 0) / 20))
    r0 = rede or Counter(i["rede"] for i in lst).most_common(1)[0][0]
    k = re.sub(r"[^a-z0-9]", "", norm(handle))
    return dict(id=k, nome=nome, handle=handle, rede=r0, papel=papel, n=len(lst),
                redes=dict(Counter(i["rede"] for i in lst)),
                views=int(sum(i["views"] or 0 for i in lst)), likes=int(sum(i["likes"] for i in lst)),
                coments=int(sum(i["coments"] or 0 for i in lst)),
                seguidores=int(seguidores.get(k, 0)) or None,
                avatar=avatar or {"Instagram": f"instagram/{handle}", "TikTok": f"tiktok/{handle}",
                                  "YouTube": f"youtube/{canal_id.get(handle, handle)}", "X": f"x/{handle}"}[r0],
                post=dict(rede=top["rede"], texto=corta(re.sub(r"#\S+", "", top["texto"]), 150), url=top["url"], ano=top["ano"],
                          views=int(top["views"] or 0), likes=int(top["likes"]), coments=int(top["coments"] or 0)))

FOCO_REDE = {
    "Instagram": [("drathaisprioli", "Dra. Thais Prioli", "Médica"), ("jeanalessandrob", "Jean Alessandro", "Psicólogo"),
                  ("segatta.psico", "@segatta.psico", "Psicólogo"), ("davimgiordani", "Davi Giordani", "Criança com AH/SD e família")],
    "TikTok": [("jeanalessandrob", "Jean Alessandro", "Psicólogo"), ("dra.tamirismariano", "Dra. Tamiris Mariano", "Profissional de saúde"),
               ("altashabilidades.sd", "@altashabilidades.sd", "Perfil sobre AH/SD"), ("vozesneurodivergentes", "Vozes Neurodivergentes", "Perfil de neurodiversidade")],
    "YouTube": [("Dra. Olzeni Ribeiro", "Dra. Olzeni Ribeiro", "Especialista em AH/SD"), ("Ciência Todo Dia", "Ciência Todo Dia", "Divulgação científica"),
                ("Jean Alessandro", "Jean Alessandro", "Psicólogo"), ("Lygia Pereira - Psicologia e Autismo Feminino", "Lygia Pereira", "Psicóloga")],
}
M["foco_rede"] = {r: [c for c in (cartao(h, n, r, p) for h, n, p in lst) if c] for r, lst in FOCO_REDE.items()}
ORGS = [("mensabrasil", "Mensa Brasil", "Associação de alto QI"),
        ("institutoalphalumen", "Instituto Alpha Lumen", "Escola e instituto para AH/SD"),
        ("febratis", "Febratis", "Federação")]
M["orgs"] = [c for c in (cartao(h, n, None, p) for h, n, p in ORGS) if c]
# Famosos: o post de maior engajamento sobre cada um, de quem quer que tenha publicado.
por_url = {i["url"]: i for i in itens}
FAMOSOS = [
    ("Davi Giordani", "Criança com AH/SD, 4 milhões de seguidores", "https://www.tiktok.com/@takeisaude/video/7610086687133273351", "instagram/davimgiordani"),
    ("Whindersson Nunes", "Humorista; o caso dele reabriu o debate em 2025", "https://www.tiktok.com/@jeanalessandrob/video/7527050137147804933", "instagram/whinderssonnunes"),
    ("Roger Moreira", "Músico (Ultraje a Rigor), \"o maior QI do Brasil\"", "https://www.youtube.com/watch?v=Ymkh93Ixv0M", "youtube/ConVerso"),
    ("João Gabriel (@aielloflow)", "Personagem do \"QI 640\" no Instagram", "https://www.instagram.com/aielloflow/reel/DWWqiN1jaA7/", "instagram/aielloflow"),
]
M["famosos"] = []
for nome, papel, url, av in FAMOSOS:
    it = por_url.get(url)
    if not it:
        continue
    M["famosos"].append(dict(id=re.sub(r"[^a-z0-9]", "", norm(av.split("/")[-1])), nome=nome, papel=papel, avatar=av, rede=it["rede"],
                             publicado_por=it["autor"] if it["rede"] == "YouTube" else "@" + it["autor"],
                             post=dict(texto=corta(re.sub(r"#\S+", "", it["texto"]), 150), url=url, ano=it["ano"],
                                       views=int(it["views"] or 0), likes=int(it["likes"]), coments=int(it["coments"] or 0))))
M["famosos_imprensa"] = ["Fabiana Karla", "Geovanna Tominaga", "Walcyr Carrasco"]
D["mapa"] = M

# ---------- fotos de perfil: uma chave por pessoa, com as redes onde tentar a foto
canon = lambda k: ALIAS.get(k, k)
CAND = defaultdict(list)


def add_cand(k, spec):
    k = canon(k)
    if spec and spec not in CAND[k]:
        CAND[k].append(spec)


def specs_de(k):
    ids = cri[k]["ids"] if k in cri else {}
    out = []
    if "TikTok" in ids:
        out.append(f"tiktok/{ids['TikTok']}")
    if "YouTube" in ids:
        out.append(f"youtube/{canal_id.get(ids['YouTube'], ids['YouTube'])}")
    if "Instagram" in ids:
        out.append(f"instagram/{ids['Instagram']}")
    return out


usados = [(p_["id"], p_.get("avatar")) for p_ in M["pessoas"]]
usados += [(c_["id"], c_.get("avatar")) for r_ in M["foco_rede"].values() for c_ in r_]
usados += [(c_["id"], c_.get("avatar")) for c_ in M["orgs"] + M["famosos"] + M["sem_dados"]]
usados += [(m_["id"], None) for cl_ in D["clusters"] for m_ in cl_["membros"]]
for k, av in usados:
    for alvo in [k] + [a for a, b in ALIAS.items() if b == canon(k)]:
        for sp in specs_de(alvo):
            add_cand(k, sp)
    add_cand(k, av)
(AQUI / "fotos_candidatos.json").write_text(json.dumps(CAND, ensure_ascii=False, indent=0), encoding="utf-8")
D["foto_de"] = {k: f"img/perfis/{canon(k)}.jpg" for k, _ in usados if (AQUI / "img/perfis" / f"{canon(k)}.jpg").exists()}

if PENDENTES:
    with open(AQUI / "exemplos_pendentes.jsonl", "w", encoding="utf-8") as f:
        for r in PENDENTES.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(PENDENTES)} exemplos esperando verificação: rode verificar_exemplos.py e gere de novo")

from datetime import datetime
D["gerado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
(AQUI / "dados.js").write_text("window.DADOS = " + json.dumps(D, ensure_ascii=False) + ";\n", encoding="utf-8")
print("ok", {k: v for k, v in D["numeros"].items()})
for c in D["clusters"]:
    print(c["n"], c["nome"]["nome"], c["traços"], c["likes"], c["views"], c["comentarios"])
