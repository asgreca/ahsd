import subprocess
import time
import json
import os
import re
from urllib.parse import quote_plus, urlparse

QUERIES = [
    # (query_string, is_news_tab)
    ("Mensa Brasil", True),
    ("membros da Mensa Brasil", True),
    ("membro da Mensa Brasil reportagem", False),
    ("superdotação Brasil", True),
    ("altas habilidades Brasil", True),
    ("dupla excepcionalidade diagnóstico", True),
    ("superdotados Brasil identificados", True),
    ("teste da Mensa Brasil", True),
    ("criancas superdotadas Mensa Brasil", True),
    ("Jovanka superdotação", True),
    ("Jovanka superdotação", False),
]

OUTPUT_DIR = "noticias/dados"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "reportagens_ddg.jsonl")
URLS_FILE = os.path.join(OUTPUT_DIR, "urls_coletadas.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_applescript(code):
    proc = subprocess.run(["osascript", "-e", code], capture_output=True, text=True)
    if proc.returncode != 0:
        return None, proc.stderr.strip()
    return proc.stdout.strip(), None

def load_ddg_and_extract(query, is_news):
    q_enc = quote_plus(query)
    if is_news:
        url = f"https://duckduckgo.com/?q={q_enc}&iar=news&kl=br-pt"
    else:
        url = f"https://duckduckgo.com/?q={q_enc}&kl=br-pt"
        
    print(f"\n[DDG] Carregando: {query} ({'NOTÍCIAS' if is_news else 'WEB'})...")
    
    # Navega na aba atual da janela 1
    nav_script = f"""
    tell application "Safari"
        tell current tab of window 1
            set URL to "{url}"
        end tell
    end tell
    """
    run_applescript(nav_script)
    time.sleep(4)
    
    # Extrai links
    extract_script = """
    tell application "Safari"
        tell current tab of window 1
            set linkCount to (do JavaScript "document.links.length") as integer
            set res to ""
            repeat with i from 0 to linkCount - 1
                set h to (do JavaScript ("document.links[" & i & "].href"))
                set t to (do JavaScript ("document.links[" & i & "].innerText"))
                if h does not contain "duckduckgo.com" and (count of t) > 15 then
                    set res to res & h & "<<<SEP>>>" & t & "<<<ITEM>>>"
                end if
            end repeat
            return res
        end tell
    end tell
    """
    out, err = run_applescript(extract_script)
    if err or not out:
        print(f"  -> Erro ao extrair: {err}")
        return []
        
    items = []
    for raw in out.split("<<<ITEM>>>"):
        if not raw.strip():
            continue
        parts = raw.split("<<<SEP>>>")
        link_url = parts[0].strip()
        text = parts[1].strip() if len(parts) > 1 else ""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        # Filtros de exclusão (redes sociais e DDG)
        domain = urlparse(link_url).netloc.lower()
        if any(ign in domain for ign in ["youtube.com", "instagram.com", "tiktok.com", "twitter.com", "x.com", "facebook.com", "duckduckgo.com"]):
            continue
            
        source = lines[0] if len(lines) > 0 else domain
        title = lines[1] if len(lines) > 1 else lines[0] if lines else ""
        snippet = " ".join(lines[2:]) if len(lines) > 2 else ""
        
        # Detecta ano se houver
        year_match = re.search(r'\b(202[1-6])\b', text)
        year = year_match.group(1) if year_match else None
        
        items.append({
            "query": query,
            "aba": "news" if is_news else "web",
            "url": link_url,
            "source": source,
            "title": title,
            "snippet": snippet,
            "raw_text": text,
            "ano_detectado": year
        })
        
    print(f"  -> Encontrados {len(items)} links válidos de portais/jornais.")
    return items

def main():
    todas_urls = {}
    if os.path.exists(URLS_FILE):
        try:
            with open(URLS_FILE, "r", encoding="utf-8") as f:
                todas_urls = json.load(f)
        except Exception:
            todas_urls = {}

    print(f"Iniciando busca no DuckDuckGo para {len(QUERIES)} variações...")
    for q, is_news in QUERIES:
        results = load_ddg_and_extract(q, is_news)
        for r in results:
            u = r["url"]
            if u not in todas_urls:
                todas_urls[u] = r
            else:
                # enriquece se faltou snippet
                if not todas_urls[u].get("snippet") and r.get("snippet"):
                    todas_urls[u]["snippet"] = r["snippet"]
                    
    print(f"\nTotal de URLs únicas de notícias mapeadas: {len(todas_urls)}")
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(todas_urls, f, ensure_ascii=False, indent=2)

    # Processar com Defuddle para extrair texto integral limpo
    ja_processados = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        obj = json.loads(line)
                        ja_processados.add(obj.get("url"))
                    except:
                        pass

    print(f"Reportagens já lidas com defuddle: {len(ja_processados)}. Restantes: {len(todas_urls) - len(ja_processados)}")

    count = 0
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
        for u, meta in todas_urls.items():
            if u in ja_processados:
                continue
            count += 1
            print(f"\n[{count}/{len(todas_urls) - len(ja_processados)}] Lendo: {u}")
            print(f"  Título: {meta.get('title')[:80]}...")
            
            # Defuddle
            cmd = ["defuddle", "parse", u, "--md"]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                if proc.returncode == 403 or "403" in proc.stderr:
                    # Tentar com UA spoof
                    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                    proc = subprocess.run(["defuddle", "parse", u, "--md", "-u", ua], capture_output=True, text=True, timeout=25)
                
                md_content = proc.stdout.strip()
                if not md_content:
                    print(f"  -> Defuddle vazio ou falhou: {proc.stderr[:100]}")
                    md_content = meta.get("snippet", "")
                else:
                    print(f"  -> Sucesso! {len(md_content)} caracteres lidos.")
            except subprocess.TimeoutExpired:
                print("  -> Timeout no defuddle. Usando snippet.")
                md_content = meta.get("snippet", "")
            except Exception as e:
                print(f"  -> Erro ao rodar defuddle: {e}")
                md_content = meta.get("snippet", "")

            # Verifica filtro de ano (2021-2026)
            anos_encontrados = re.findall(r'\b(202[1-6]|201\d|200\d)\b', md_content + " " + meta.get("raw_text", ""))
            
            registro = {
                "url": u,
                "title": meta.get("title"),
                "source": meta.get("source"),
                "snippet": meta.get("snippet"),
                "query": meta.get("query"),
                "aba": meta.get("aba"),
                "texto_integral_md": md_content,
                "tamanho_texto": len(md_content),
                "anos_mencionados": list(set(anos_encontrados)),
                "ano_detectado": meta.get("ano_detectado")
            }
            out_f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            out_f.flush()
            time.sleep(1)

    print("\nColeta de reportagens do DuckDuckGo concluída!")

if __name__ == "__main__":
    main()
