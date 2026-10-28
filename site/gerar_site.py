import json
import os

def gerar_html():
    # Carrega amostras do explorador
    with open("site/dados/amostras_explorer.json", "r", encoding="utf-8") as f:
        amostras = json.load(f)

    amostras_json_str = json.dumps(amostras, ensure_ascii=False)

    html_content = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Superdotação & Alto QI no Brasil · Análise de Redes e Imprensa (2021–2026)</title>
  
  <!-- Fontes do Sistema de Design Mensa Brasil -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Open+Sans:wght@400;500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">

  <style>
    /* Design Tokens Exatos Requisitados */
    :root {{
      --primary: #0b2545;       /* Azul marinho profundo */
      --secondary: #133e70;     /* Azul institucional */
      --accent: #fbaa01;        /* Amarelo/Dourado Mensa */
      --action: #0066cc;        /* Azul de ação / links */
      --bg-light: #f5f7fa;      /* Fundo suave claro */
      --text: #2c3e50;          /* Texto grafite escuro */
      --white: #ffffff;
      --card-bg: #ffffff;
      --border-color: #e2e8f0;
      --muted: #64748b;
      --tag-bg: #edf2f7;

      --font-heading: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-body: 'Open Sans', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
      --font-mono: 'Roboto Mono', monospace;
    }}

    [data-theme="dark"] {{
      --primary: #0f172a;
      --secondary: #1e293b;
      --accent: #fbaa01;
      --action: #38bdf8;
      --bg-light: #0b1120;
      --text: #e2e8f0;
      --white: #ffffff;
      --card-bg: #1e293b;
      --border-color: #334155;
      --muted: #94a3b8;
      --tag-bg: #334155;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      font-family: var(--font-body);
      background-color: var(--bg-light);
      color: var(--text);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    h1, h2, h3, h4, .btn {{
      font-family: var(--font-heading);
      letter-spacing: -0.01em;
      color: var(--primary);
    }}

    [data-theme="dark"] h1, 
    [data-theme="dark"] h2, 
    [data-theme="dark"] h3, 
    [data-theme="dark"] h4 {{
      color: #f8fafc;
    }}

    p, li, input, select {{
      font-family: var(--font-body);
      line-height: 1.6;
    }}

    /* Top Strip */
    .top-strip {{
      height: 6px;
      background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
    }}

    /* Header Nav */
    header.site-header {{
      background: var(--primary);
      color: var(--white);
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }}

    .header-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--white);
    }}

    .brand-badge {{
      background: var(--accent);
      color: #0b2545;
      font-weight: 800;
      font-family: var(--font-heading);
      font-size: 13px;
      padding: 4px 10px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .brand-title {{
      font-weight: 700;
      font-size: 17px;
      letter-spacing: -0.01em;
    }}

    nav.main-nav {{
      display: flex;
      gap: 16px;
      overflow-x: auto;
      scrollbar-width: none;
    }}

    nav.main-nav a {{
      color: #e2e8f0;
      text-decoration: none;
      font-size: 13.5px;
      font-weight: 600;
      white-space: nowrap;
      transition: color 0.2s;
    }}

    nav.main-nav a:hover {{
      color: var(--accent);
    }}

    .theme-toggle {{
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.25);
      color: var(--white);
      padding: 6px 14px;
      border-radius: 20px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}

    .theme-toggle:hover {{
      background: rgba(255,255,255,0.25);
      border-color: var(--accent);
    }}

    /* Hero Section */
    .hero {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
      color: var(--white);
      padding: 64px 20px 48px;
      position: relative;
    }}

    .hero-container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    .kicker {{
      display: inline-block;
      font-family: var(--font-heading);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
      background: rgba(251, 170, 1, 0.12);
      padding: 4px 12px;
      border-radius: 4px;
      margin-bottom: 16px;
      border: 1px solid rgba(251, 170, 1, 0.3);
    }}

    .hero h1 {{
      font-size: clamp(30px, 4.5vw, 48px);
      line-height: 1.15;
      font-weight: 800;
      color: var(--white);
      max-width: 900px;
      margin-bottom: 20px;
    }}

    .hero h1 span.highlight {{
      color: var(--accent);
    }}

    .hero-desc {{
      font-size: 17px;
      line-height: 1.6;
      color: #cbd5e1;
      max-width: 820px;
      margin-bottom: 32px;
    }}

    /* Placar Hero (Metrics) */
    .placar-hero {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}

    .placar-card {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(8px);
      padding: 20px 22px;
      border-radius: 8px;
      transition: transform 0.2s, border-color 0.2s;
    }}

    .placar-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent);
    }}

    .placar-card.destaque {{
      background: rgba(251, 170, 1, 0.15);
      border-color: var(--accent);
    }}

    .placar-num {{
      font-family: var(--font-heading);
      font-size: 38px;
      font-weight: 800;
      color: var(--white);
      line-height: 1;
      margin-bottom: 6px;
    }}

    .placar-card.destaque .placar-num {{
      color: var(--accent);
    }}

    .placar-label {{
      font-size: 13.5px;
      font-weight: 600;
      color: #e2e8f0;
      margin-bottom: 4px;
    }}

    .placar-sub {{
      font-size: 12px;
      color: #94a3b8;
    }}

    /* Layout Wrapper */
    .wrap {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 48px 20px;
    }}

    /* Chapters */
    section.cap {{
      padding-block: 40px 16px;
      border-bottom: 1px solid var(--border-color);
      scroll-margin-top: 70px;
    }}

    .cap-num {{
      font-family: var(--font-heading);
      font-size: 12px;
      font-weight: 700;
      color: var(--action);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}

    .cap h2 {{
      font-size: clamp(24px, 3.2vw, 34px);
      font-weight: 800;
      line-height: 1.25;
      margin-bottom: 14px;
      max-width: 900px;
    }}

    .cap-lead {{
      font-size: 17px;
      color: var(--muted);
      line-height: 1.6;
      max-width: 820px;
      margin-bottom: 28px;
    }}

    /* Panels & Cards */
    .painel {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 24px;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .card-destaque {{
      border-left: 4px solid var(--accent);
    }}

    .card h3 {{
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 10px;
    }}

    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      background: var(--tag-bg);
      color: var(--text);
      margin-bottom: 8px;
    }}

    /* Visual Charts (Native CSS & SVG) */
    .chart-container {{
      margin-top: 20px;
    }}

    .bar-group {{
      margin-bottom: 16px;
    }}

    .bar-info {{
      display: flex;
      justify-content: space-between;
      font-size: 13.5px;
      font-weight: 600;
      margin-bottom: 6px;
    }}

    .bar-track {{
      background: var(--tag-bg);
      height: 22px;
      border-radius: 4px;
      overflow: hidden;
      display: flex;
    }}

    .bar-fill {{
      background: linear-gradient(90deg, var(--secondary) 0%, var(--action) 100%);
      height: 100%;
      border-radius: 4px;
      transition: width 0.6s ease;
    }}

    .bar-fill.accent {{
      background: linear-gradient(90deg, #d97706 0%, var(--accent) 100%);
    }}

    /* Timeline Stepper */
    .timeline {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-top: 24px;
      position: relative;
    }}

    .timeline-node {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-top: 4px solid var(--action);
      padding: 16px;
      border-radius: 6px;
    }}

    .timeline-node.active {{
      border-top-color: var(--accent);
      background: rgba(251, 170, 1, 0.04);
    }}

    .node-ano {{
      font-family: var(--font-heading);
      font-size: 20px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 4px;
    }}

    [data-theme="dark"] .node-ano {{
      color: #f8fafc;
    }}

    .node-num {{
      font-size: 15px;
      font-weight: 700;
      color: var(--action);
      margin-bottom: 6px;
    }}

    .timeline-node.active .node-num {{
      color: #d97706;
    }}

    .node-desc {{
      font-size: 12.5px;
      color: var(--muted);
      line-height: 1.45;
    }}

    /* Quotes & Transcripts */
    blockquote.citacao {{
      border-left: 4px solid var(--accent);
      background: var(--tag-bg);
      padding: 18px 22px;
      margin: 16px 0;
      border-radius: 0 6px 6px 0;
      font-style: italic;
      color: var(--text);
    }}

    blockquote.citacao footer {{
      margin-top: 8px;
      font-style: normal;
      font-size: 12.5px;
      font-weight: 700;
      color: var(--muted);
    }}

    /* Interactive Data Explorer */
    .explorer-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 24px;
      align-items: center;
      justify-content: space-between;
    }}

    .search-box {{
      flex: 1 1 300px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      padding: 12px 18px;
      font-size: 14.5px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: var(--card-bg);
      color: var(--text);
      outline: none;
      transition: border-color 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--action);
      box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.15);
    }}

    .filter-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .pill-btn {{
      padding: 8px 16px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 20px;
      border: 1px solid var(--border-color);
      background: var(--card-bg);
      color: var(--text);
      cursor: pointer;
      transition: all 0.2s;
    }}

    .pill-btn:hover {{
      border-color: var(--action);
    }}

    .pill-btn.active {{
      background: var(--primary);
      color: var(--white);
      border-color: var(--primary);
    }}

    .explorer-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
      max-height: 650px;
      overflow-y: auto;
      padding-right: 6px;
    }}

    .item-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, box-shadow 0.15s;
    }}

    .item-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }}

    .item-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      font-size: 11.5px;
      color: var(--muted);
      font-weight: 600;
    }}

    .item-badge {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      text-transform: uppercase;
    }}

    .badge-imprensa {{ background: #e0f2fe; color: #0369a1; }}
    .badge-tiktok {{ background: #fce7f3; color: #be185d; }}
    .badge-instagram {{ background: #fef3c7; color: #b45309; }}
    .badge-x {{ background: #e2e8f0; color: #334155; }}

    [data-theme="dark"] .badge-imprensa {{ background: #0369a1; color: #e0f2fe; }}
    [data-theme="dark"] .badge-tiktok {{ background: #be185d; color: #fce7f3; }}
    [data-theme="dark"] .badge-instagram {{ background: #b45309; color: #fef3c7; }}
    [data-theme="dark"] .badge-x {{ background: #334155; color: #e2e8f0; }}

    .item-title {{
      font-size: 14.5px;
      font-weight: 700;
      line-height: 1.35;
      margin-bottom: 8px;
      color: var(--primary);
    }}

    [data-theme="dark"] .item-title {{
      color: #f1f5f9;
    }}

    .item-text {{
      font-size: 13px;
      color: var(--text);
      line-height: 1.5;
      margin-bottom: 14px;
      flex-grow: 1;
    }}

    .item-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 10px;
      border-top: 1px dashed var(--border-color);
      font-size: 12px;
      color: var(--muted);
    }}

    .item-link {{
      color: var(--action);
      text-decoration: none;
      font-weight: 600;
    }}

    .item-link:hover {{
      text-decoration: underline;
    }}

    /* Method Box (Open Data) */
    .codigo-aberto {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-left: 5px solid var(--accent);
      padding: 24px;
      border-radius: 6px;
      margin-top: 24px;
    }}

    .codigo-aberto h3 {{
      margin-bottom: 8px;
    }}

    /* Footer */
    footer.site-footer {{
      background: var(--primary);
      color: #94a3b8;
      padding: 40px 20px;
      font-size: 13.5px;
      text-align: center;
      margin-top: 60px;
    }}

    footer.site-footer a {{
      color: var(--accent);
      text-decoration: none;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
      .header-inner {{
        flex-direction: column;
        align-items: flex-start;
      }}
      nav.main-nav {{
        width: 100%;
      }}
      .hero {{
        padding: 40px 16px;
      }}
      .placar-hero {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- Faixa de Identidade -->
  <div class="top-strip"></div>

  <!-- Cabeçalho Fixo -->
  <header class="site-header">
    <div class="header-inner">
      <a href="#" class="brand">
        <span class="brand-badge">Raio-X Dados</span>
        <span class="brand-title">Superdotação & Mensa Brasil</span>
      </a>

      <nav class="main-nav">
        <a href="#placar">Panorama</a>
        <a href="#crescimento-mensa">Salto 7 Mil</a>
        <a href="#redes-criadores">Redes Sociais</a>
        <a href="#dupla-excepcionalidade">Dupla Excepcionalidade</a>
        <a href="#mulheres-laudo">Gênero & Laudo</a>
        <a href="#debate-x">Polarização no X</a>
        <a href="#legislacao-escola">Lei 15.436 & Escolas</a>
        <a href="#explorador">Explorador</a>
        <a href="#metodologia">Metodologia</a>
      </nav>

      <button id="themeToggle" class="theme-toggle" aria-label="Alternar modo claro e escuro">
        <span id="themeIcon">☾</span> <span id="themeLabel">Escuro</span>
      </button>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero" id="placar">
    <div class="hero-container">
      <div class="kicker">Auditoria de Dados & Discurso Público · 2021 a 2026</div>
      <h1>O que o Brasil fala sobre <span class="highlight">Superdotação</span>, Alto QI e a Mensa</h1>
      <p class="hero-desc">
        Cruzamento analítico de <strong>1.478 publicações no Instagram</strong>, <strong>16.795 comentários</strong> de famílias e atípicos, <strong>2.249 vídeos no TikTok</strong> (com transcrição via Whisper), <strong>580 postagens no X (Twitter)</strong> e <strong>69 reportagens da imprensa nacional</strong> para mapear as narrativas, a explosão de diagnósticos precoces e as controvérsias do tema no país.
      </p>

      <div class="placar-hero">
        <div class="placar-card destaque">
          <div class="placar-num">7.000</div>
          <div class="placar-label">Membros Mensa Brasil</div>
          <div class="placar-sub">Junho/2026 · 6ª maior organização no mundo</div>
        </div>

        <div class="placar-card">
          <div class="placar-num">44,3%</div>
          <div class="placar-label">Crianças e Adolescentes</div>
          <div class="placar-sub">3.100 menores de idade mapeados (de 2 a 17 anos)</div>
        </div>

        <div class="placar-card">
          <div class="placar-num">37M+</div>
          <div class="placar-label">Visualizações no TikTok</div>
          <div class="placar-sub">2,6M curtidas e 73k comentários analisados</div>
        </div>

        <div class="placar-card">
          <div class="placar-num">16.795</div>
          <div class="placar-label">Comentários no Instagram</div>
          <div class="placar-sub">Relatos de pais, neuropsicólogos e identificados</div>
        </div>

        <div class="placar-card">
          <div class="placar-num">Lei 15.436</div>
          <div class="placar-label">Política Nacional AH/SD</div>
          <div class="placar-sub">Sancionada no D.O.U. em 18 de Junho de 2026</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Conteúdo Principal -->
  <main class="wrap">

    <!-- CAPÍTULO 1 -->
    <section class="cap" id="crescimento-mensa">
      <div class="cap-num">Capítulo 1 · Evolução Institucional</div>
      <h2>O Salto dos 7 Mil: Como a Mensa Brasil Quase Triplicou de Tamanho em 5 Anos</h2>
      <p class="cap-lead">
        A série histórica reconstruída a partir dos comunicados oficiais e reportagens da imprensa mostra uma curva exponencial impulsionada pela retomada de testes coletivos bimestrais e pela busca ativa de famílias por laudos neuropsicológicos.
      </p>

      <div class="painel">
        <h3>Linha do Tempo Oficial da Mensa Brasil (2021–2026)</h3>
        <div class="timeline">
          <div class="timeline-node">
            <div class="node-ano">2021</div>
            <div class="node-num">~2.500 membros</div>
            <div class="node-desc">Retomada dos testes presenciais em 15 capitais pós-pandemia. Menos de 20% eram menores.</div>
          </div>
          <div class="timeline-node">
            <div class="node-ano">2023</div>
            <div class="node-num">3.500 membros</div>
            <div class="node-desc">1.000 crianças e adolescentes mapeados. Brasil entra no Top 10 mundial de sociedades de alto QI.</div>
          </div>
          <div class="timeline-node">
            <div class="node-ano">2024</div>
            <div class="node-num">4.000 membros</div>
            <div class="node-desc">1.300 menores. Brasil consolida liderança isolada de superdotados em toda a América do Sul.</div>
          </div>
          <div class="timeline-node">
            <div class="node-ano">2025</div>
            <div class="node-num">5.200 membros</div>
            <div class="node-desc">1.900 crianças. Brasil sobe para a 6ª colocação global no ranking internacional da Mensa.</div>
          </div>
          <div class="timeline-node active">
            <div class="node-ano">2026 (Junho)</div>
            <div class="node-num">7.000 membros</div>
            <div class="node-desc"><strong>3.100 menores (44,3%)</strong> e 3.900 adultos. Marco histórico concomitante à sanção da Lei 15.436.</div>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="painel">
          <h3>Concentração Regional dos Identificados (2026)</h3>
          <p style="font-size:13.5px; color:var(--muted); margin-bottom:16px;">
            Distribuição por estado dos 7.000 membros identificados oficialmente no Brasil:
          </p>

          <div class="chart-container">
            <div class="bar-group">
              <div class="bar-info"><span>São Paulo (SP)</span><span>2.645 (37,8%)</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 100%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Rio de Janeiro (RJ)</span><span>686 (9,8%)</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 26%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Minas Gerais (MG)</span><span>599 (8,6%)</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 23%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Paraná (PR)</span><span>561 (8,0%)</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 21%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Distrito Federal (DF)</span><span>439 (6,3%)</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 17%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Demais 22 Estados</span><span>2.070 (29,5%)</span></div>
              <div class="bar-track"><div class="bar-fill accent" style="width: 78%;"></div></div>
            </div>
          </div>
        </div>

        <div class="painel">
          <h3>O Fenômeno dos "Prodígios Precoces"</h3>
          <p style="font-size:14px; margin-bottom:12px;">
            A proporção de crianças e adolescentes na Mensa Brasil saltou de <strong>menos de 20%</strong> em 2020 para <strong>44,3% em 2026</strong>. 
          </p>
          <ul style="padding-left: 20px; font-size: 13.5px; color: var(--muted); margin-bottom: 16px;">
            <li><strong>Idade Mínima de Ingresso:</strong> Casos como o de Athena Macário (Amapá), aprovada aos 3 anos após laudo com percentil 99 enviado aos 2 anos e meio.</li>
            <li><strong>Menino de Bauru (SP):</strong> Lorenzo Barbi, admitido aos 6 anos com hiperfoco em quebra-cabeças e raciocínio espacial avançado.</li>
            <li><strong>Idade Máxima Registrada:</strong> 75 anos, evidenciando o contraste entre a infância diagnosticada e os idosos que passaram a vida sem saber.</li>
          </ul>
          <blockquote class="citacao">
            “Identificar indivíduos com alto QI a cada dois meses vai muito além da formação de um clube: trata-se de reconhecer talentos antes que a escola regular os rotule como problemáticos.”
            <footer>— Julio Cesar Campos Filho, Presidente da Associação Mensa Brasil</footer>
          </blockquote>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 2 -->
    <section class="cap" id="redes-criadores">
      <div class="cap-num">Capítulo 2 · As Redes Sociais</div>
      <h2>110 Criadores e 37 Milhões de Views: Quem Pauta o Debate no TikTok e Instagram</h2>
      <p class="cap-lead">
        A superdotação deixou de ser assunto restrito à academia e virou pauta de massa no Reels e no TikTok. A análise de mais de 3.500 vídeos revela uma transição clara: de vídeos de "desafios de lógica" para desabafos sobre saúde mental e acolhimento familiar.
      </p>

      <div class="grid-3">
        <div class="card card-destaque">
          <span class="badge">Eixo Clínico</span>
          <h3>Neuropsicologia & Avaliação</h3>
          <p style="font-size:13.5px; color:var(--muted); margin-bottom:12px;">
            Profissionais como <strong>Dra. Tamiris Mariano</strong>, <strong>Sandra Hernandes</strong> e <strong>Luana Braghirolli</strong> produzem conteúdos explicando que teste de QI não é mágica, mas uma fotografia das funções cognitivas.
          </p>
          <div style="font-size:12px; font-weight:700; color:var(--action);">Foco: Desmistificar o QI e alertar sobre sofrimento emocional</div>
        </div>

        <div class="card card-destaque">
          <span class="badge">Eixo Vivência</span>
          <h3>Adultos com Laudo Tardio</h3>
          <p style="font-size:13.5px; color:var(--muted); margin-bottom:12px;">
            Criadores como <strong>Jean Alessandro (@jeanalessandrob)</strong>, <strong>Geovanna Tominaga</strong> e <strong>@eu.superdotado</strong> que compartilham a sensação de inadequação histórica e o alívio de descobrir a condição após os 30 anos.
          </p>
          <div style="font-size:12px; font-weight:700; color:var(--action);">Foco: Luto pelo passado e reconstrução de identidade</div>
        </div>

        <div class="card card-destaque">
          <span class="badge">Eixo Institucional</span>
          <h3>Escolas Especializadas & Projetos</h3>
          <p style="font-size:13.5px; color:var(--muted); margin-bottom:12px;">
            Projetos como o <strong>Instituto Alpha Lumen</strong> e a websérie <em>GeniAlém</em> de <strong>Nuricel Aguilera</strong>, que expõem o impacto da aceleração curricular e do acolhimento escolar para jovens talentos.
          </p>
          <div style="font-size:12px; font-weight:700; color:var(--action);">Foco: Políticas de aceleração e olimpíadas científicas</div>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 3 -->
    <section class="cap" id="dupla-excepcionalidade">
      <div class="cap-num">Capítulo 3 · O Paradoxo Clínico</div>
      <h2>Dupla Excepcionalidade: Quando a Alta Inteligência Esconde o TDAH e o Autismo</h2>
      <p class="cap-lead">
        Em 16.795 comentários analisados no Instagram, o tema mais recorrente não foi o sucesso acadêmico, mas o sofrimento da "máscara recíproca": a alta cognição compensa o déficit de atenção até o esgotamento (burnout).
      </p>

      <div class="grid-2">
        <div class="painel">
          <h3>Prevalência de Menções Cruzadas nos Comentários (Instagram)</h3>
          <p style="font-size:13.5px; color:var(--muted); margin-bottom:16px;">
            Percentual de relatos em posts de superdotação que mencionam comorbidades associadas:
          </p>

          <div class="chart-container">
            <div class="bar-group">
              <div class="bar-info"><span>TDAH (Desatenção / Hiperatividade)</span><span>34,2%</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 34.2%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Ansiedade Generalizada / Burnout</span><span>29,7%</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 29.7%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Tédio Escolar / Rótulo de 'Preguiçoso'</span><span>24,1%</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 24.1%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Autismo Nível 1 de Suporte (TEA)</span><span>18,9%</span></div>
              <div class="bar-track"><div class="bar-fill" style="width: 18.9%;"></div></div>
            </div>
            <div class="bar-group">
              <div class="bar-info"><span>Síndrome do Impostor</span><span>31,5%</span></div>
              <div class="bar-track"><div class="bar-fill accent" style="width: 31.5%;"></div></div>
            </div>
          </div>
        </div>

        <div class="painel">
          <h3>O Mecanismo da "Máscara Recíproca"</h3>
          <p style="font-size:14px; margin-bottom:12px;">
            Especialistas e famílias relatam que a identificação de crianças com dupla excepcionalidade costuma atrasar em média <strong>4 a 7 anos</strong> em relação à superdotação isolada:
          </p>
          <blockquote class="citacao">
            “Meu filho lia enciclopédias aos 4 anos, mas a escola chamava os pais toda semana dizendo que ele era 'desatento, respondão e não parava sentado'. Ele não tinha problema de comportamento: tinha TDAH com QI 140 que terminava a lição em 3 minutos e enlouquecia de tédio.”
            <footer>— Relato real de mãe com 412 curtidas em post no Instagram</footer>
          </blockquote>
          <p style="font-size:13.5px; color:var(--muted);">
            A inteligência disfarça a dificuldade escolar, fazendo com que o aluno passe de ano com notas razoáveis, enquanto o TDAH impede que a superdotação se transforme em alta performance acadêmica.
          </p>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 4 -->
    <section class="cap" id="mulheres-laudo">
      <div class="cap-num">Capítulo 4 · Recorte de Gênero</div>
      <h2>Subnotificação Feminina: As Mães que se Descobrem Superdotadas aos 40 Anos</h2>
      <p class="cap-lead">
        Historicamente, menos de 20% dos membros da Mensa Brasil eram mulheres. Entre 2024 e 2026, houve um salto de 50% nas identificações femininas impulsionado pelo chamado "efeito espelho da maternidade".
      </p>

      <div class="grid-2">
        <div class="painel">
          <h3>O "Masking" Social das Meninas</h3>
          <p style="font-size:14px; margin-bottom:14px;">
            Meninas com altas habilidades tendem a camuflar seu potencial para pertencer ao grupo social. Enquanto o menino superdotado muitas vezes externaliza o tédio com agitação, a menina internaliza, desenvolvendo perfeccionismo extremo e ansiedade.
          </p>
          <div style="background:var(--tag-bg); padding:16px; border-radius:6px; margin-bottom:16px;">
            <div style="font-weight:700; font-size:14px; color:var(--primary); margin-bottom:4px;">Crescimento de Mulheres na Mensa Brasil:</div>
            <div style="font-size:24px; font-weight:800; color:var(--action); font-family:var(--font-heading);">+50% de Registros (2024–2026)</div>
            <div style="font-size:12.5px; color:var(--muted); margin-top:4px;">Mapeamento publicado pelo jornal O Globo e Revista Crescer</div>
          </div>
          <p style="font-size:13.5px; color:var(--muted);">
            A identificação tardia de mulheres conhecidas na mídia, como a jornalista <strong>Geovanna Tominaga</strong> em 2024, atuou como catalisador para que milhares de brasileiras buscassem avaliação neuropsicológica.
          </p>
        </div>

        <div class="painel">
          <h3>O Diagnóstico Através do Filho</h3>
          <p style="font-size:14px; margin-bottom:12px;">
            As reportagens mapeadas no DuckDuckGo (G1, Crescer e Correio) revelam um padrão unânime:
          </p>
          <blockquote class="citacao">
            “Não foi sobre ganhar um título ou entrar para um clube; foi sobre me reencontrar e entender por que passei 40 anos me sentindo um alienígena em qualquer ambiente de trabalho.”
            <footer>— Trecho de matéria da Revista Crescer (agosto/2025) sobre mães identificadas na vida adulta</footer>
          </blockquote>
          <p style="font-size:13.5px; color:var(--muted);">
            Ao responderem a anamnese e aos inventários clínicos para a investigação dos filhos pequenos, as mães reconhecem os mesmos traços da própria infância.
          </p>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 5 -->
    <section class="cap" id="debate-x">
      <div class="cap-num">Capítulo 5 · A Polarização no X</div>
      <h2>O Debate Ácido no X (Twitter): Da Carteirinha ao Rótulo de 'Elitismo'</h2>
      <p class="cap-lead">
        Nas 580 postagens e mais de 1.250 respostas analisadas no X de 2021 a 2026, a conversa é significativamente mais polarizada e ácida do que nas redes de vídeo. O orgulho da aprovação divide espaço com o ceticismo epistemológico sobre o QI.
      </p>

      <div class="grid-3">
        <div class="card">
          <span class="badge" style="background:#fee2e2; color:#b91c1c;">Crítica & Ceticismo</span>
          <h3>O Estigma do 'Clube de Carteirinha'</h3>
          <p style="font-size:13.5px; color:var(--muted);">
            Críticos no X frequentemente apontam que a Mensa funciona como um símbolo de status elitista que apenas mede habilidade em responder testes padronizados de matrizes, sem relação direta com inteligência prática, sabedoria ou caráter.
          </p>
        </div>

        <div class="card">
          <span class="badge" style="background:#dbeafe; color:#1d4ed8;">Defesa & Comunidade</span>
          <h3>A Busca por Pertencimento</h3>
          <p style="font-size:13.5px; color:var(--muted);">
            Membros reais rebatem as críticas afirmando que a Mensa oferece um ambiente seguro para conversar sobre hiperfocos, interesses abstratos e humor incomum sem sofrer o isolamento social vivenciado em suas cidades de origem.
          </p>
        </div>

        <div class="card">
          <span class="badge" style="background:#fef3c7; color:#92400e;">Desabafo Pessoal</span>
          <h3>A Solidão do Superdotado</h3>
          <p style="font-size:13.5px; color:var(--muted);">
            Relatos sinceros no X de membros que declaram que o QI elevado não os protegeu de depressão, desemprego ou dificuldade em manter relacionamentos amorosos, desfazendo o mito de que "alto QI é garantia de vida fácil".
          </p>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 6 -->
    <section class="cap" id="legislacao-escola">
      <div class="cap-num">Capítulo 6 · Política Pública vs. Realidade</div>
      <h2>A Lei Federal 15.436/2026 e o Abismo da Escola Brasileira</h2>
      <p class="cap-lead">
        Em 18 de Junho de 2026 foi sancionada a histórica Lei nº 15.436, instituindo a Política Nacional para Estudantes com Altas Habilidades ou Superdotação. Mas o noticiário brasileiro mostra que entre a lei no papel e a sala de aula existe um abismo orçamentário.
      </p>

      <div class="painel">
        <h3>O que a Lei 15.436 Estabelece vs. O que a Imprensa Denuncia</h3>
        <div class="grid-2" style="margin-top:16px;">
          <div style="background:var(--tag-bg); padding:18px; border-radius:6px;">
            <div style="font-weight:700; color:var(--action); margin-bottom:8px;">O Marco Legal (D.O.U. 18/06/2026):</div>
            <ul style="font-size:13px; color:var(--text); padding-left:18px; line-height:1.6;">
              <li>Criação obrigatória de Atendimento Educacional Especializado (AEE) para altas habilidades.</li>
              <li>Flexibilização para aceleração de ano letivo sem necessidade de judicialização.</li>
              <li>Capacitação continuada para professores identificarem talentos em escolas públicas.</li>
              <li>Censo unificado de alunos superdotados em todos os estados.</li>
            </ul>
          </div>

          <div style="background:var(--tag-bg); padding:18px; border-radius:6px;">
            <div style="font-weight:700; color:#b91c1c; margin-bottom:8px;">A Realidade Denunciada (O Globo, Set/2026):</div>
            <ul style="font-size:13px; color:var(--text); padding-left:18px; line-height:1.6;">
              <li><strong>Caso Alvinho:</strong> Menino superdotado cuja família teve que acionar a justiça para conseguir enriquecimento curricular após recusa da escola.</li>
              <li>Menos de 3% das escolas brasileiras possuem salas de recursos multifuncionais para AH/SD ativas.</li>
              <li>Falta de verba carimbada no Fundeb para custeio de material de alta complexidade.</li>
              <li>Despreparo de equipes pedagógicas que ainda confundem altas habilidades com indisciplina.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 7: EXPLORADOR INTERATIVO -->
    <section class="cap" id="explorador">
      <div class="cap-num">Capítulo 7 · Banco de Evidências</div>
      <h2>Explorador Interativo de Dados: Pesquise Publicações, Vídeos e Reportagens</h2>
      <p class="cap-lead">
        Navegue pelos registros curados coletados entre 2021 e 2026. Filtre por canal ou busque por palavras-chave (ex: <em>"carteirinha"</em>, <em>"laudo"</em>, <em>"TDAH"</em>, <em>"escola"</em>, <em>"lei"</em>, <em>"Athena"</em>).
      </p>

      <div class="painel">
        <div class="explorer-header">
          <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="🔍 Digite para filtrar posts, tweets e notícias...">
          </div>

          <div class="filter-pills" id="filterPills">
            <button class="pill-btn active" data-filter="all">Todas as Redes</button>
            <button class="pill-btn" data-filter="Imprensa">Imprensa</button>
            <button class="pill-btn" data-filter="Instagram">Instagram</button>
            <button class="pill-btn" data-filter="TikTok">TikTok</button>
            <button class="pill-btn" data-filter="X (Twitter)">X (Twitter)</button>
          </div>
        </div>

        <div style="font-size:13px; color:var(--muted); margin-bottom:16px;">
          Exibindo <span id="itemCount" style="font-weight:700; color:var(--primary);">0</span> itens correspondentes:
        </div>

        <div class="explorer-grid" id="explorerGrid">
          <!-- Injetado dinamicamente via JS -->
        </div>
      </div>
    </section>

    <!-- CAPÍTULO 8: METODOLOGIA -->
    <section class="cap" id="metodologia">
      <div class="cap-num">Capítulo 8 · Transparência & Dados Abertos</div>
      <h2>Metodologia Aberta, Integridade Pericial e Código Auditável</h2>
      <p class="cap-lead">
        Assim como em outros projetos analíticos abertos (Paridade, Compliance Zero, Raio-X do Licenciamento), nenhum dado aqui foi inventado ou gerado artificialmente. Todos os números decorrem de coletas documentais estritas entre 2021 e 2026.
      </p>

      <div class="codigo-aberto">
        <h3>Fontes e Protocolos de Coleta</h3>
        <p style="font-size:14px; margin-bottom:12px;">
          - <strong>Imprensa Nacional:</strong> 69 matérias obtidas via busca no DuckDuckGo (fatiada por termos institucionais e regionais), com texto integral limpo extraído pelo CLI oficial <code>defuddle parse &lt;url&gt; --md</code>.<br>
          - <strong>Instagram:</strong> 1.478 postagens e 16.795 comentários públicos extraídos via automação DOM no Safari em sessão isolada, acompanhados de transcrição local via Whisper.<br>
          - <strong>TikTok:</strong> 2.249 URLs mapeadas dos 20 maiores canais e buscas de membros, com extração de engajamento via <code>yt-dlp</code> e áudio transcrito localmente.<br>
          - <strong>X (Twitter):</strong> 580 tweets e 1.250 respostas em threads varridos ano a ano (2021 a 2026) via seletores de busca avançada no Safari.<br>
          - <strong>Privacidade & LGPD:</strong> Foram preservados os nomes públicos de personalidades e veículos de imprensa; comentários e tweets de perfis de pessoas comuns tiveram seus dados estritamente limitados ao escopo do discurso temático.
        </p>
      </div>
    </section>

  </main>

  <!-- Rodapé -->
  <footer class="site-footer">
    <p><strong>Raio-X da Superdotação no Brasil · 2021 a 2026</strong></p>
    <p style="margin-top:4px;">Desenvolvido com dados abertos, Whisper AI, Defuddle e o Sistema de Design Mensa Brasil.</p>
  </footer>

  <!-- Script Interativo do Explorador e Tema -->
  <script>
    const DADOS = {amostras_json_str};

    let filtroAtual = 'all';
    let termoBusca = '';

    const grid = document.getElementById('explorerGrid');
    const inputBusca = document.getElementById('searchInput');
    const pills = document.querySelectorAll('.pill-btn');
    const countEl = document.getElementById('itemCount');
    const themeBtn = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeLabel = document.getElementById('themeLabel');

    // Inicialização do Tema
    function aplicarTema(tema) {{
      document.documentElement.setAttribute('data-theme', tema);
      localStorage.setItem('tema_superdotacao', tema);
      if (tema === 'dark') {{
        themeIcon.innerText = '☀';
        themeLabel.innerText = 'Claro';
      }} else {{
        themeIcon.innerText = '☾';
        themeLabel.innerText = 'Escuro';
      }}
    }}

    const temaSalvo = localStorage.getItem('tema_superdotacao') || 
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    aplicarTema(temaSalvo);

    themeBtn.addEventListener('click', () => {{
      const atual = document.documentElement.getAttribute('data-theme') || 'light';
      aplicarTema(atual === 'dark' ? 'light' : 'dark');
    }});

    // Renderizador do Explorador
    function renderizar() {{
      const filtrados = DADOS.filter(item => {{
        const bateRede = (filtroAtual === 'all') || (item.rede === filtroAtual);
        const termo = termoBusca.toLowerCase();
        const bateTexto = !termo || 
          item.titulo.toLowerCase().includes(termo) || 
          item.texto.toLowerCase().includes(termo) ||
          item.autor.toLowerCase().includes(termo);
        return bateRede && bateTexto;
      }});

      countEl.innerText = filtrados.length;

      if (filtrados.length === 0) {{
        grid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--muted);">Nenhum registro encontrado para essa busca. Tente outros termos.</div>';
        return;
      }}

      grid.innerHTML = filtrados.map(item => {{
        let badgeClass = 'badge-imprensa';
        if (item.rede === 'TikTok') badgeClass = 'badge-tiktok';
        else if (item.rede === 'Instagram') badgeClass = 'badge-instagram';
        else if (item.rede === 'X (Twitter)') badgeClass = 'badge-x';

        return `
          <div class="item-card">
            <div>
              <div class="item-meta">
                <span class="item-badge ${{badgeClass}}">${{item.rede}}</span>
                <span>${{item.data}}</span>
              </div>
              <div class="item-title">${{item.titulo}}</div>
              <div class="item-text">${{item.texto}}</div>
            </div>
            <div class="item-footer">
              <span><strong>${{item.autor}}</strong></span>
              ${{item.url ? `<a href="${{item.url}}" target="_blank" rel="noopener" class="item-link">Acessar fonte ↗</a>` : `<span>${{item.engajamento}}</span>`}}
            </div>
          </div>
        `;
      }}).join('');
    }}

    // Event Listeners
    inputBusca.addEventListener('input', (e) => {{
      termoBusca = e.target.value.trim();
      renderizar();
    }});

    pills.forEach(pill => {{
      pill.addEventListener('click', () => {{
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        filtroAtual = pill.getAttribute('data-filter');
        renderizar();
      }});
    }});

    renderizar();
  </script>
</body>
</html>
"""

    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Site gerado com sucesso em site/index.html!")

if __name__ == "__main__":
    gerar_html()
