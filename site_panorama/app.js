(() => {
const D = window.DADOS;
// Cada página tem só parte dos blocos: o que não existir vira um elemento solto e é ignorado.
const $ = s => document.querySelector(s) || document.createElement('div');
const nf = new Intl.NumberFormat('pt-BR');
const n = x => x == null ? '–' : nf.format(Math.round(x));
const c = x => {
  if (x == null || x === 0) return x === 0 ? '0' : '–';
  if (x >= 1e6) return (x / 1e6).toLocaleString('pt-BR', {maximumFractionDigits: 1}) + ' mi';
  if (x >= 1e4) return (x / 1e3).toLocaleString('pt-BR', {maximumFractionDigits: 0}) + ' mil';
  return n(x);
};
const p = x => (x ?? 0).toLocaleString('pt-BR', {maximumFractionDigits: 1}) + '%';
const esc = s => String(s ?? '').replace(/[&<>"]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const N = D.numeros;

/* tema claro/escuro */
const raiz = document.documentElement;
try { const t = localStorage.getItem('tema'); if (t) raiz.dataset.theme = t; } catch (e) {}
$('#tema-btn').onclick = () => {
  const escuro = raiz.dataset.theme ? raiz.dataset.theme === 'dark' : !matchMedia('(prefers-color-scheme: light)').matches;
  raiz.dataset.theme = escuro ? 'light' : 'dark';
  try { localStorage.setItem('tema', raiz.dataset.theme); } catch (e) {}
  desenharLinha();
};

/* abertura */
const manch = D.anual['Manchetes (Google Notícias)'];
$('#hero-lead').innerHTML = `Eu queria responder a uma pergunta simples de enunciar e trabalhosa de medir: como o Brasil fala sobre superdotação? Para isso, eu reuni 98.861 comentários, 870 vídeos do YouTube e do TikTok (transcritos palavra por palavra; todos), 708 posts com métricas e 1.264 reportagens. Os números dizem o seguinte: entre 2021 e 2026, as manchetes por ano passaram de 53 para 411. Isso é um aumento de 675%, ou 7,75 vezes, se você preferir a forma multiplicativa. O público, por sua vez, mistura duas coisas diferentes sob a mesma palavra: o fascínio pelo número do QI e a busca por respostas sobre neurodivergência e sofrimento real. Não são a mesma coisa. Confundi-las é um erro, e os dados mostram exatamente onde ele acontece.`;
const ME = D.medicao;
const somaM = (campo, redes) => redes.reduce((a, r) => a + (ME[r][campo] || 0), 0);
const faixa = [
  ['74,3 mi', 'alcance medido em visualizações', `TikTok 39,5 mi · YouTube 30,7 mi · Instagram 3,8 mi · X 360 mil`],
  ['29,4 mi', 'audiência potencial no Instagram', `alcance nos 87 perfis especializados monitorados (com 207 mil curtidas e 17 mil comentários)`],
  ['4,4 mi', 'curtidas', `TikTok 2,9 mi · YouTube 1,4 mi · Instagram 207 mil · X 2.293`],
  ['192 mil', 'comentários', `YouTube 113 mil · TikTok 61 mil · Instagram 17 mil · X 1.257 respostas`],
];
$('#faixa').innerHTML = faixa.map(([a, b, d]) => `<div><b>${a}</b><span>${b}</span><small>${d}</small></div>`).join('');
$('#carimbo').textContent = `Recorte temporal: 2021 a 2026 · dados coletados até 27/10/2026 · página gerada em ${D.gerado_em}`;

/* 00 fontes */
const R = Object.fromEntries(D.redes.map(r => [r.rede, r]));
const semM = 'sem métrica';
const linhaF = (nome, papel, itens, r) => `<tr><td><b>${nome}</b></td><td>${papel}</td><td class="n">${itens}</td><td class="n">${r.views != null ? c(r.views) + ' views' : r.seguidores ? c(r.seguidores) + ' seguidores*' : semM}</td><td class="n">${r.likes != null ? c(r.likes) : semM}</td><td class="n">${r.coments != null ? c(r.coments) : semM}</td></tr>`;
$('#tab-fontes').innerHTML = `<thead><tr><th>Fonte</th><th>O que representa</th><th class="n">Itens</th><th class="n">Alcance</th><th class="n">Curtidas</th><th class="n">Comentários</th></tr></thead><tbody>` +
  linhaF('YouTube', 'Explicação e entretenimento em vídeo longo', `${n(ME.YouTube.itens)} vídeos`, ME.YouTube) +
  linhaF('TikTok', 'Vídeo curto, autoidentificação e viralização', `${n(ME.TikTok.itens)} vídeos`, ME.TikTok) +
  linhaF('Instagram', 'Profissionais de saúde, famílias e celebridades', `${n(ME.Instagram.itens)} posts`, ME.Instagram) +
  linhaF('X', 'Imprensa, debate e reação rápida', `${n(ME.X.itens)} posts`, ME.X) +
  linhaF('Imprensa', 'Portais, jornais e revistas', `${n(N.reportagens_classificadas)} reportagens · ${n(N.revistas_artigos)} artigos de revista`, ME.Imprensa) +
  `</tbody>`;


/* ícones de rede e fotos de perfil (arquivo local; sem foto, as iniciais) */
const ICONE = {
  YouTube: 'M2 7a3 3 0 0 1 3-3h14a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3z M10 9l5 3-5 3z',
  TikTok: 'M9 18V5l12-2v13 M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0z M21 16a3 3 0 1 1-6 0 3 3 0 0 1 6 0z',
  Instagram: 'M3 7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4z M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M17.5 6.5h.01',
  X: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z M8 9h8 M8 13h5',
  Imprensa: 'M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0v-9 M18 14h-8 M15 18h-5 M10 6h8v4h-8z',
};
const COR_REDE = {YouTube: 'var(--accent)', TikTok: 'var(--spark)', Instagram: 'var(--accent2)', X: 'var(--neu)', Imprensa: 'var(--muted)'};
const ico = (rede, tam = 18, cor = 'currentColor') => `<svg width="${tam}" height="${tam}" viewBox="0 0 24 24" fill="none" stroke="${cor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${ICONE[rede] || ''}"/></svg>`;
const ICONE_TEMA = {
  entretenimento_humor: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M8 14s1.5 2 4 2 4-2 4-2 M9 9h.01 M15 9h.01',
  experiencia_pessoal: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  elogio_admiracao: 'M12 2l3 6.3 7 1-5 4.8 1.2 6.9-6.2-3.3L5.8 21 7 14.1 2 9.3l7-1z',
  validade_testes_qi: 'M9 11l3 3 8-8 M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9',
  diagnostico_avaliacao: 'M9 2h6v4H9z M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2 M9 13l2 2 4-4',
  saude_mental_neuro: 'M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 12 5a5.5 5.5 0 0 0-10 3.5c0 2.3 1.5 4 3 5.5l7 7z',
  caracteristicas_sinais: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z M21 21l-4.3-4.3',
  elitismo_arrogancia: 'M2 18l3-10 5 5 2-8 2 8 5-5 3 10z',
  educacao_escola: 'M22 10L12 5 2 10l10 5 10-5z M6 12v5c3 2 9 2 12 0v-5',
  mensa_sociedade: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M2 12h20',
  politica_publica: 'M3 22h18 M6 18v-7 M10 18v-7 M14 18v-7 M18 18v-7 M12 2l8 5H4z',
  custo_acesso: 'M12 1v22 M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
};
const AV = {};
((D.mapa || {}).pessoas || []).forEach(p => { AV[p.id] = p.avatar; });
const chaveNome = t => String(t || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
function foto(id, nome, cls = '') {
  const ini = esc(String(nome).replace(/^@|^Dra?\.\s*/i, '').split(/[\s._]+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join(''));
  const src = (D.foto_de || {})[id];
  return src ? `<span class="ft ${cls}"><img src="${src}" alt="" loading="lazy" onerror="this.parentNode.textContent='${ini}'"></span>` : `<span class="ft ${cls}">${ini}</span>`;
}


/* 00 panorama em síntese: cinco fontes, cinco papéis */
(() => {
  const F = [
    ['YouTube', 'Explica e diverte', ME.YouTube, 'vídeos'],
    ['TikTok', 'Vira identidade', ME.TikTok, 'vídeos'],
    ['Instagram', 'Consultório e vitrine', ME.Instagram, 'posts'],
    ['X', 'Reação rápida', ME.X, 'posts'],
    ['Imprensa', 'Pauta o tema', ME.Imprensa, 'reportagens'],
  ];
  const mx = {views: Math.max(ME.YouTube.views, ME.TikTok.views, ME.Instagram.seguidores), likes: Math.max(ME.YouTube.likes, ME.TikTok.likes), coments: Math.max(ME.YouTube.coments, ME.TikTok.coments)};
  const bol = (v, m, rot, cor, anel) => v == null
    ? `<div class="bol"><i style="width:26px;height:26px;border:1px dashed var(--cinza2)"></i><b class="mu">sem métrica</b><span>${rot}</span></div>`
    : `<div class="bol"><i style="width:${Math.max(8, 60 * Math.sqrt(v / m))}px;height:${Math.max(8, 60 * Math.sqrt(v / m))}px;${anel ? 'border:3px solid ' + cor : 'background:' + cor}"></i><b>${c(v)}</b><span>${rot}</span></div>`;
  $('#fontes-visual').innerHTML = F.map(([rede, papel, r, un]) => `<article class="fcard">
    <span class="fic" style="background:${COR_REDE[rede]}">${ico(rede, 30, 'var(--bg)')}</span>
    <h3>${rede}</h3><div class="fpapel">${papel}</div>
    <div class="fitens"><b>${n(r.itens)}</b><span>${un}</span></div>
    <div class="bols">${bol(r.views ?? (r.seguidores || null), mx.views, r.seguidores ? 'seguidores' : 'views', COR_REDE[rede], !!r.seguidores)}${bol(r.likes, mx.likes, 'curtidas', COR_REDE[rede])}${bol(r.coments, mx.coments, rede === 'X' ? 'respostas' : 'comentários', COR_REDE[rede])}</div>
  </article>`).join('');
  const dom = (nome, campo, redes) => {
    const tot = redes.reduce((a, r) => a + (ME[r][campo] || 0), 0);
    return `<div class="dom"><span>${nome}</span><div>${redes.filter(r => ME[r][campo]).map(r => { const p = 100 * ME[r][campo] / tot; return `<i style="width:${p}%;background:${COR_REDE[r]}" title="${r} ${Math.round(p)}%">${p >= 7 ? r + ' ' + Math.round(p) + '%' : ''}</i>`; }).join('')}</div></div>`;
  };
  $('#fontes-dominio').innerHTML = dom('Alcance', 'views', ['TikTok', 'YouTube']) + dom('Curtidas', 'likes', ['TikTok', 'YouTube', 'Instagram']) + dom('Comentários', 'coments', ['YouTube', 'TikTok', 'Instagram', 'X']);
})();

/* 01 anual */
const A = D.anual, anos = A.anos;
let sm = `<div></div>` + anos.map(a => `<div class="h">${a}</div>`).join('');
for (const [k, v] of Object.entries(A)) {
  if (k === 'anos') continue;
  const mx = Math.max(...v) || 1;
  sm += `<div class="lab">${esc(k)}</div>` + v.map(x => `<div class="col${x === mx ? ' max' : ''}"><span>${c(x)}</span><i style="height:${Math.max(1, 40 * x / mx)}px"></i></div>`).join('');
}
$('#anual').innerHTML = sm;

function desenharLinha() {
  // no celular o gráfico fica mais estreito e alto, para o texto não encolher
  const mv = innerWidth < 640, M = D.mensal, v = M.manchetes, W = mv ? 420 : 1000, H = mv ? 240 : 220, pl = 36, pb = 26, pt = 14;
  $('#linha-mensal').setAttribute('viewBox', `0 0 ${W} ${H}`);
  const mx = Math.max(...v), cor = getComputedStyle(raiz).getPropertyValue('--accent').trim();
  const x = i => pl + (W - pl - 8) * i / (v.length - 1), y = val => pt + (H - pt - pb) * (1 - val / mx);
  let s = '';
  for (let g = 0; g <= mx; g += 20) s += `<line x1="${pl}" x2="${W}" y1="${y(g)}" y2="${y(g)}" stroke="var(--line)"/><text x="${pl - 6}" y="${y(g) + 4}" text-anchor="end" font-size="11" fill="var(--muted)">${g}</text>`;
  M.meses.forEach((m, i) => { if (m.endsWith('-01')) s += `<text x="${x(i)}" y="${H - 6}" font-size="12" fill="var(--muted)">${m.slice(0, 4)}</text><line x1="${x(i)}" x2="${x(i)}" y1="${pt}" y2="${H - pb}" stroke="var(--line)" stroke-dasharray="2 4"/>`; });
  const pts = v.map((val, i) => `${x(i)},${y(val)}`).join(' ');
  s += `<polygon points="${pl},${y(0)} ${pts} ${x(v.length - 1)},${y(0)}" fill="${cor}" opacity=".15"/><polyline points="${pts}" fill="none" stroke="${cor}" stroke-width="2.5"/>`;
  const im = v.indexOf(mx);
  s += `<circle cx="${x(im)}" cy="${y(mx)}" r="5" fill="var(--spark)"/><text x="${x(im) - 8}" y="${y(mx) + 4}" text-anchor="end" font-size="13" font-weight="700" fill="var(--ink)">${mx} em ${M.meses[im].split('-').reverse().join('/')}</text>`;
  $('#linha-mensal').innerHTML = s;
}
desenharLinha();
let linhaMovel = innerWidth < 640;
addEventListener('resize', () => { if ((innerWidth < 640) !== linhaMovel) { linhaMovel = !linhaMovel; desenharLinha(); } });

const ATOS = [
  ['2021', 'O QI vira jogo', '47%', 'dos comentários são piada sobre o próprio QI', 'A Mensa retoma os testes presenciais'],
  ['2022', 'A Mensa faz 20 anos', '131', 'manchetes, mais que o dobro de 2021', 'A escola vira a pauta dos portais'],
  ['2023', 'O TikTok descobre o tema', '3,7 mi', 'views no vídeo sobre sobrecarga sensorial', 'Superdotação vira identidade'],
  ['2024', 'Adultos se descobrem', '1,9 mi', 'views em "A verdade sobre testes de QI"', 'A descoberta tardia ganha a imprensa'],
  ['2025', 'Celebridades e TDAH', '18,8 mil', 'comentários no YouTube no ano', 'Dupla excepcionalidade entra no debate'],
  ['2026', 'A lei e a criança-símbolo', '411', 'manchetes, recorde do período', 'Lei 15.436 e criança no Senado'],
];
$('#atos').innerHTML = ATOS.map(([a, t, num, leg, fato]) => `<article class="ano-card">
  <div class="ano-img"><img src="img/ano${a}.jpg" alt="" loading="lazy" onerror="this.src='img/capa.jpg'"><span>${a}</span></div>
  <div class="ano-txt"><h3>${t}</h3><div class="ano-num"><b>${num}</b><span>${leg}</span></div><p>${fato}</p></div>
</article>`).join('');

/* o Congresso em síntese */
$('#congresso').innerHTML = `<div class="cong-top"><div><b>18</b><span>das 21 propostas encontradas na Câmara e no Senado são de 2026</span></div>
  <div class="cong-funil" aria-label="21 propostas, 1 lei">${Array.from({length: 21}, (_, i) => `<i class="${i ? '' : 'lei'}"></i>`).join('')}<span><b>21 propostas, 1 lei</b> (Lei 15.436, junho de 2026, sancionada com vetos)</span></div></div>
  <div class="cong-pautas">${[
    ['5', 'A escola', 'Identificar, acompanhar e apoiar o aluno', 'M22 10L12 5 2 10l10 5 10-5z M6 12v5c3 2 9 2 12 0v-5'],
    ['4', 'Inclusão ampla', 'Neurodiversidade, fundo de educação inclusiva, procuradoria', 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.9 M16 3.1a4 4 0 0 1 0 7.8'],
    ['3', 'Política nacional', 'Política, cadastro de estudantes e dados; uma virou lei', 'M3 22h18 M6 18v-7 M10 18v-7 M14 18v-7 M18 18v-7 M12 2l8 5H4z'],
    ['3', 'Debate e disputa', 'Audiências no Senado e pedido para sustar portaria do MEC', 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z M8 9h8 M8 13h5'],
    ['2', 'Saúde pelo SUS', 'Avaliação neuropsicológica e centros de saúde mental', 'M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 12 5a5.5 5.5 0 0 0-10 3.5c0 2.3 1.5 4 3 5.5l7 7z'],
    ['2', 'Visibilidade', 'Dia nacional e Agosto Violeta', 'M8 2v4 M16 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z'],
  ].map(([q, t, d, ic]) => `<div class="pauta"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ic}"/></svg></span><b>${q}</b><h4>${t}</h4><p>${d}</p></div>`).join('')}</div>`;



/* 02 temas */
const T = D.temas.filter(t => t.tema !== 'outro').concat(D.temas.filter(t => t.tema === 'outro'));
const mxT = Math.max(...T.map(t => Math.max(t.pct_comentarios, t.pct_videos, t.pct_reportagens, t.pct_views)));
const bar = (v, cls = '') => `<div class="cel"><div class="barra ${cls}" style="width:${70 * v / mxT}px"></div>${p(v)}</div>`;
$('#tab-temas2').innerHTML = `<thead><tr><th>Tema</th><th>Comentários</th><th>Vídeos</th><th>Views dos vídeos</th><th>Reportagens</th><th class="n">Curtidas/coment.</th></tr></thead><tbody>` +
  T.map(t => `<tr><td>${esc(t.rotulo)}</td><td>${bar(t.pct_comentarios)}</td><td>${bar(t.pct_videos, 'b2')}</td><td>${bar(t.pct_views, 'b2')}</td><td>${bar(t.pct_reportagens, 'b3')}</td><td class="n">${t.likes_por_comentario.toLocaleString('pt-BR')}</td></tr>`).join('') + '</tbody>';
const tv = Object.fromEntries(D.temas.map(t => [t.tema, t]));
$('#temas-lead').innerHTML = `Validade dos testes de QI: <span>${p(tv.validade_testes_qi.pct_comentarios)}</span> dos comentários e <span>${p(tv.validade_testes_qi.pct_reportagens)}</span> das reportagens. Educação e escola: <span>${p(tv.educacao_escola.pct_reportagens)}</span> das reportagens e <span>${p(tv.educacao_escola.pct_comentarios)}</span> dos comentários.`;

/* 03 Mensa */
const hb = (el, rows, fmt = n, mx) => {
  mx = mx || Math.max(...rows.map(r => r[1]));
  $(el).innerHTML = rows.map(([l, v]) => `<div>${esc(l)}</div><div class="tr"><i style="width:${100 * v / mx}%"></i></div><div class="v">${fmt(v)}</div>`).join('');
};
hb('#membros', D.mensa.membros.map(m => [m.ano, m.membros]));
$('#membros-nota').textContent = D.mensa.membros.map(m => `${m.ano}: ${m.nota}`).join(' · ');
hb('#presenca', Object.entries(D.mensa.presenca).sort((a, b) => b[1] - a[1]), p, 100);
const cores = {detrator: 'var(--neg)', neutro: 'var(--neu)', apoiador: 'var(--pos)'};
$('#postura').innerHTML = Object.entries(D.mensa.postura).map(([fonte, o]) => {
  const tot = o.detrator + o.neutro + o.apoiador;
  return `<div style="display:grid;grid-template-columns:130px 1fr 70px;gap:12px;align-items:center;margin:8px 0"><div>${fonte}</div><div class="stack">${['detrator', 'neutro', 'apoiador'].map(k => `<i style="width:${100 * o[k] / tot}%;background:${cores[k]}">${o[k] / tot > .08 ? p(100 * o[k] / tot) : ''}</i>`).join('')}</div><div class="v" style="text-align:right;color:var(--muted)">${n(tot)}</div></div>`;
}).join('') + `<div class="legenda"><span style="--c:var(--neg)">Detrator</span><span style="--c:var(--neu)">Neutro</span><span style="--c:var(--pos)">Apoiador</span></div>
<p class="leitura">Nos comentários, <b>${p(100 * 894 / 1461)}</b> de quem cita a Mensa a critica, em geral por um de dois motivos: a ideia de clube de arrogância ou a tese de que o teste não mede inteligência. Na imprensa, o quadro é outro. A Mensa aparece como fonte neutra, e só <b>1</b> das ${n(408)} reportagens que a citam é negativa: uma em 408, ou 0,25%. Estatisticamente, isso é quase zero.</p>`;
hb('#mensa-temas', D.mensa.temas_comentarios.map(t => [t.rotulo, t.pct]), p);
const MC = D.mensa.canal;
$('#mensa-canais').innerHTML = `<dl style="display:grid;grid-template-columns:1fr auto;gap:8px 12px;font-size:15px">
<dt>Canal no YouTube</dt><dd class="n">${MC.videos} vídeos · ${n(MC.views)} views</dd>
${D.mensa.redes.map(r => `<dt>${r.rede} @${esc(r.handle)}</dt><dd class="n">${r.posts} posts · ${n(r.likes)} curtidas${r.seguidores ? ' · ' + c(r.seguidores) + ' seguidores' : ''}</dd>`).join('')}
</dl><p class="nota">O vídeo mais visto do canal tem ${n(MC.melhor_views)} views ("${esc(MC.melhor)}"). Para efeito de comparação, um único vídeo de quiz de QI feito por terceiros passa de 1 milhão.</p>`;
$('#tab-mensa-videos').innerHTML = `<thead><tr><th>Vídeo</th><th>Canal</th><th>Ano</th><th>Tema</th><th class="n">Views</th></tr></thead><tbody>` +
  D.mensa.videos_top.map(v => `<tr><td><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titulo)}</a></td><td>${esc(v.canal)}</td><td>${v.ano}</td><td>${esc(v.tema)}</td><td class="n">${n(v.views)}</td></tr>`).join('') + '</tbody>';

/* 04 influenciadores */
const CAT = {psicologo: 'Psicólogo(a)', medico: 'Médico(a)', entidade_instituicao: 'Instituição', entidade: 'Instituição', superdotado_criador: 'Pessoa com AH/SD', ator_celebridade: 'Celebridade', educador_pesquisador: 'Educador(a)', outro: 'Outro'};
/* fichas: nomes relevantes com foto e a rede onde atuam */
(() => {
  const P = ((D.mapa || {}).pessoas || []).slice();
  const eng = p => p.likes + p.coments + p.views / 20;
  const foco = P.filter(p => p.foco);
  const orgs = ((D.mapa || {}).orgs || []).map(o => ({...o, cluster: o.papel, isOrg: true}));
  const lista = [...foco, ...orgs, ...P.filter(p => !p.foco).sort((a, b) => eng(b) - eng(a))].slice(0, 32);
  let filtro = 'Todas';
  const ficha = p => `<a class="ficha" href="mapa.html#foco">
    ${foto(p.id, p.nome, 'g')}
    <div class="fn">${esc(p.nome)}</div>
    <div class="fp">${esc(p.cluster || p.papel || '')}</div>
    <div class="fr">${Object.keys(p.redes || {}).map(r => `<span title="${r}" style="color:${COR_REDE[r]}">${ico(r, 16)}</span>`).join('')}</div>
    <div class="fm">${p.seguidores ? c(p.seguidores) + ' seguidores' : p.views ? c(p.views) + ' views' : c(p.likes) + ' curtidas'}</div></a>`;
  function render() {
    const L = filtro === 'Todas' ? lista : filtro === 'Organizações' ? orgs : lista.filter(p => (p.redes || {})[filtro]);
    $('#fichas').innerHTML = L.map(ficha).join('');
    document.querySelectorAll('#fichas-abas button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === filtro));
  }
  $('#fichas-abas').innerHTML = ['Todas', 'Instagram', 'TikTok', 'YouTube', 'Organizações'].map(f => `<button data-f="${f}">${f}</button>`).join('');
  $('#fichas-abas').onclick = e => { if (e.target.dataset.f) { filtro = e.target.dataset.f; render(); } };
  render();
})();
const REDES = ['TikTok', 'YouTube', 'Instagram', 'X'];
const NOTA_INF = {
  TikTok: 'Ordenado por visualizações. Alcance = soma de views dos vídeos do tema; comentários = número exibido pelo TikTok.',
  YouTube: 'Ordenado por visualizações. Seguidores = inscritos do canal no dia da coleta.',
  Instagram: 'Ordenado por curtidas. O Instagram não mostra views de todos os posts; o alcance é o número de seguidores. Comentários = comentários coletados.',
  X: 'A coleta do X não trouxe curtidas, respostas nem repostagens. Listamos só veículos e instituições, por número de posts sobre o tema.',
};
function tabInf(rede) {
  const L = D.influenciadores[rede];
  $('#tab-inf').innerHTML = `<thead><tr><th>#</th><th>Perfil</th>${rede === 'Instagram' ? '<th>Categoria</th>' : ''}<th class="n">Conteúdos</th><th class="n">Seguidores</th><th class="n">Views</th><th class="n">Curtidas</th><th class="n">Comentários</th></tr></thead><tbody>` +
    L.map((x, i) => `<tr><td>${i + 1}</td><td><b>${rede === 'YouTube' ? '' : '@'}${esc(x.autor)}</b></td>${rede === 'Instagram' ? `<td>${esc(CAT[x.categoria] || '–')}</td>` : ''}<td class="n">${n(x.itens)}</td><td class="n">${c(x.seguidores)}</td><td class="n">${c(x.views)}</td><td class="n">${rede === 'X' ? '–' : c(x.likes)}</td><td class="n">${rede === 'X' ? '–' : c(x.comentarios)}</td></tr>`).join('') + '</tbody>';
  $('#inf-nota').textContent = NOTA_INF[rede];
  document.querySelectorAll('#abas-inf button').forEach(b => b.setAttribute('aria-selected', b.dataset.r === rede));
}
$('#abas-inf').innerHTML = REDES.map(r => `<button role="tab" data-r="${r}">${r}</button>`).join('');
$('#abas-inf').onclick = e => { if (e.target.dataset.r) tabInf(e.target.dataset.r); };
tabInf('TikTok');
$('#tab-multi').innerHTML = `<thead><tr><th>Perfil</th><th>Redes (conteúdos)</th><th class="n">Seguidores</th><th class="n">Views</th><th class="n">Curtidas</th><th class="n">Comentários</th></tr></thead><tbody>` +
  D.multirrede.map(x => `<tr><td><b>${esc(x.autor)}</b></td><td>${Object.entries(x.redes).map(([r, k]) => `<span class="chip">${r} ${k}</span>`).join('')}</td><td class="n">${c(x.seguidores)}</td><td class="n">${c(x.views)}</td><td class="n">${c(x.likes)}</td><td class="n">${c(x.comentarios)}</td></tr>`).join('') + '</tbody>';

/* 05 clusters */
$('#cl').innerHTML = D.clusters.map((k, i) => {
  const tr = Object.entries(k.perfil).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const IMG_CL = {'Clínica e avaliação': 'cl_clinica', 'QI como espetáculo': 'cl_espetaculo', 'Neurodivergência e podcasts': 'cl_neuro', 'Educação, famílias e direitos': 'cl_educacao', 'Descoberta adulta': 'cl_adulto', 'Mensa e mídia': 'cl_midia'};
  return `<div class="cl"><div class="cl-img"><img src="img/${IMG_CL[k.nome.nome] || 'capa'}.jpg" alt="" loading="lazy" onerror="this.src='img/capa.jpg'"></div><div class="n">Cluster ${i + 1} · ${k.n} criadores</div><h3>${esc(k.nome.nome)}</h3><p style="font-size:15px;color:var(--ink2)">${esc(k.nome.desc)}</p>
  <div class="m"><div><b>${c(k.views)}</b><span>views</span></div><div><b>${c(k.likes)}</b><span>curtidas</span></div><div><b>${c(k.comentarios)}</b><span>comentários</span></div></div>
  <div class="mini">${tr.map(([g, v]) => `<div>${esc(D.grupos[g])}</div><div class="tr"><i style="width:${v}%"></i></div><div class="v">${Math.round(v)}%</div>`).join('')}</div>
  <div class="avs">${k.membros.map(m => `<span class="av-m" title="${esc(m.autor)} · ${n(m.likes)} curtidas · ${n(m.views)} views · ${n(m.comentarios)} comentários">${foto(m.id, m.autor)}<small>${esc(String(m.autor).replace(/^@/, '').slice(0, 16))}</small></span>`).join('')}</div>
  <div style="font-size:13px;color:var(--muted)">${Object.entries(k.redes).sort((a, b) => b[1] - a[1]).map(([r, q]) => `${r} ${q}`).join(' · ')} conteúdos</div></div>`;
}).join('');
$('#cl-nota').textContent = `Critério: ${D.clusters_base.criadores} criadores com ${D.clusters_base.minimo_itens} ou mais conteúdos sobre o tema (com menos que isso, não dá para medir vocabulário com segurança). As barras mostram o percentual dos conteúdos do grupo que usam termos de cada assunto. Toque ou passe o mouse sobre um perfil para ver curtidas, views e comentários.`;

/* 06 comentários */
const NV = D.nuvem;
const FONTES_NV = {todas: 'Todas as fontes', youtube: 'Comentários do YouTube', instagram: 'Comentários do Instagram', tiktok: 'Falas e legendas do TikTok', x: 'Posts e respostas no X'};
const temasNv = [['todos', 'Todos os temas']].concat(Object.keys(D.rotulos_tema).filter(k => k !== 'outro').map(k => [k, D.rotulos_tema[k]]));
const filtroNv = {fonte: 'todas', tema: 'todos', ano: 'todos'};
function nuvem() {
  const {fonte, tema, ano} = filtroNv;
  const L = (fonte === 'youtube' ? NV.youtube[tema + '|' + ano] : NV[fonte][ano]) || [];
  if (L.length < 5) {
    $('#nuvem').innerHTML = `<p class="nota" style="margin:auto">Neste recorte há poucos textos para formar pares repetidos, e conclusões tiradas de amostras minúsculas são exatamente o tipo de coisa que tentamos evitar. Escolha outro ano, tema ou fonte.</p>`;
  } else {
    const mx = L[0][1], mn = L[L.length - 1][1];
    // embaralha de forma estável para a nuvem não virar lista ordenada
    const ord = L.map((x, i) => [x, i]).sort((a, b) => ((a[1] * 37) % 11) - ((b[1] * 37) % 11));
    $('#nuvem').innerHTML = ord.map(([[t, q], i]) => `<span class="${i < 3 ? 't1' : i < 8 ? 't2' : ''}" style="font-size:${16 + 34 * Math.sqrt((q - mn) / Math.max(1, mx - mn))}px" title="${n(q)} ${fonte === 'tiktok' ? 'vídeos' : fonte === 'todas' ? 'textos' : 'comentários'}">${esc(t)}<sup>${n(q)}</sup></span>`).join('');
  }
  const periodo = ano === 'todos' ? ', 2021 a 2026' : ', ' + ano;
  $('#nuvem-nota').textContent = `${FONTES_NV[fonte]}${fonte === 'youtube' && tema !== 'todos' ? ', tema "' + D.rotulos_tema[tema] + '"' : ''}${periodo}. As 20 duplas de palavras vizinhas mais frequentes; o número é quantos ${fonte === 'tiktok' ? 'vídeos' : fonte === 'todas' || fonte === 'x' ? 'textos' : 'comentários'} usam a dupla. ${fonte === 'tiktok' ? 'O TikTok não teve comentários coletados: aqui está o que os criadores dizem. ' : ''}${fonte === 'todas' ? 'Junta comentários do YouTube e do Instagram, falas do TikTok e posts e respostas do X. ' : ''}${fonte === 'youtube' ? 'Datas aproximadas por ano. ' : ''}Palavras vazias, números e texto de interface ficaram de fora.`;
  $('#filtro-tri').hidden = fonte !== 'youtube';
  document.querySelectorAll('#filtro-fonte button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === fonte));
  document.querySelectorAll('#filtro-tri button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === tema));
  document.querySelectorAll('#filtro-tri-ano button').forEach(b => b.setAttribute('aria-pressed', b.dataset.a === ano));
}
$('#filtro-fonte').innerHTML = Object.entries(FONTES_NV).map(([f, l]) => `<button data-f="${f}">${l}</button>`).join('');
$('#filtro-fonte').onclick = e => { if (e.target.dataset.f) { filtroNv.fonte = e.target.dataset.f; nuvem(); } };
$('#filtro-tri').innerHTML = temasNv.map(([k, l]) => `<button data-k="${k}">${esc(l)}</button>`).join('');
$('#filtro-tri').onclick = e => { if (e.target.dataset.k) { filtroNv.tema = e.target.dataset.k; nuvem(); } };
$('#filtro-tri-ano').innerHTML = ['todos', ...D.anual.anos.map(String)].map(a => `<button data-a="${a}">${a === 'todos' ? 'Todos os anos' : a}</button>`).join('');
$('#filtro-tri-ano').onclick = e => { if (e.target.dataset.a) { filtroNv.ano = e.target.dataset.a; nuvem(); } };
nuvem();
const fonteLink = e => e.url ? ` · <a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.onde || 'ver o post')} ↗</a>` : '';
$('#vozes').innerHTML = D.vozes.filter(v => v.exemplos.length).map(v => `<div class="card voz"><div class="voz-cab"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_TEMA[v.tema] || ''}"/></svg></span><h4>${esc(v.rotulo)}</h4></div>${v.exemplos.map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} curtidas · YouTube · ${e.ano}${fonteLink(e)}</small></blockquote>`).join('')}</div>`).join('');
$('#vozes-ig').innerHTML = D.vozes_instagram.slice(0, 6).map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} curtidas · Instagram${fonteLink(e)}</small></blockquote>`).join('');

const heat = (v, mx) => `background:color-mix(in srgb, var(--accent) ${Math.round(85 * v / mx)}%, transparent)`;
const G = Object.keys(D.grupos).filter(k => k !== 'humor' || true);
const CL = D.comentarios_lexico, cmx = Math.max(...Object.values(CL).flatMap(o => Object.values(o)));
$('#tab-com-lex').innerHTML = `<thead><tr><th>Assunto</th>${Object.keys(CL).map(r => `<th class="n">${r}</th>`).join('')}</tr></thead><tbody>` +
  G.map(g => `<tr><td>${esc(D.grupos[g])}</td>${Object.values(CL).map(o => `<td class="h" style="${heat(o[g], cmx)}">${Math.round(o[g])}%</td>`).join('')}</tr>`).join('') + '</tbody>';

/* 07 redes */
const PAPEL = {
  YouTube: ['A sala de aula e o palco', 'Vídeo longo para explicar e para divertir. Quizzes e debates sobre a validade do QI levam as maiores audiências, e é aqui que o público mais escreve.'],
  TikTok: ['Onde o tema vira identidade', 'O maior alcance da base. Psicólogos e perfis de neurodiversidade listam "sinais" e o público se reconhece. A distribuição é muito concentrada: poucos perfis respondem por quase tudo.'],
  Instagram: ['Consultório e vitrine', 'Profissionais de saúde, institutos e famílias. Mais fala sobre infância, escola e diagnóstico, e celebridades que contam a própria descoberta.'],
  X: ['A imprensa em tempo real', 'Links de reportagens, debate político e reação às notícias. Fala mais de Mensa e de leis do que as outras redes.'],
};
$('#cards-redes').innerHTML = D.redes.map(r => `<div class="card rede"><div class="rede-cab"><span class="fic" style="background:${COR_REDE[r.rede]};width:48px;height:48px;border-radius:14px">${ico(r.rede, 24, 'var(--bg)')}</span><h3>${r.rede}</h3></div><div class="q">${PAPEL[r.rede][0]}</div><p style="font-size:15px;color:var(--ink2);margin-bottom:12px">${PAPEL[r.rede][1]}</p><dl>
  <dt>Conteúdos sobre o tema</dt><dd>${n(r.itens)}</dd><dt>Perfis e canais</dt><dd>${n(r.autores)}</dd>
  <dt>Alcance (views)</dt><dd>${r.views_total ? c(r.views_total) : '–'}</dd>
  <dt>Curtidas</dt><dd>${r.rede === 'X' ? 'sem métrica' : c(r.likes_total)}</dd>
  <dt>Comentários</dt><dd>${r.rede === 'X' ? n(N.x_respostas) + ' resp.' : c(r.comentarios_total)}</dd>
  <dt>Curtidas, mediana</dt><dd>${r.rede === 'X' ? '–' : n(r.likes_mediana)}</dd>
  <dt>Top 5 perfis = % das curtidas</dt><dd>${r.rede === 'X' ? '–' : p(r.concentracao_top5)}</dd></dl></div>`).join('');
const LX = Object.fromEntries(D.redes.map(r => [r.rede, r.lexico]));
LX['Imprensa (títulos)'] = D.redes_lexico_imprensa;
const lmx = Math.max(...Object.values(LX).flatMap(o => Object.values(o)));
$('#tab-lex').innerHTML = `<thead><tr><th>Assunto</th>${Object.keys(LX).map(r => `<th class="n">${r}</th>`).join('')}</tr></thead><tbody>` +
  G.map(g => `<tr><td>${esc(D.grupos[g])}</td>${Object.values(LX).map(o => `<td class="h" style="${heat(o[g], lmx)}">${Math.round(o[g])}%</td>`).join('')}</tr>`).join('') + '</tbody>';

const TV = ['educacao_escola', 'diagnostico_avaliacao', 'caracteristicas_sinais', 'saude_mental_neuro', 'experiencia_pessoal', 'mensa_sociedade', 'elogio_admiracao', 'politica_publica', 'validade_testes_qi'];
const CURTO = {educacao_escola: 'Escola', diagnostico_avaliacao: 'Diagnóstico', caracteristicas_sinais: 'Sinais', saude_mental_neuro: 'Saúde mental', experiencia_pessoal: 'Experiência', mensa_sociedade: 'Mensa', elogio_admiracao: 'Elogio', politica_publica: 'Política', validade_testes_qi: 'Validade do QI'};
$('#tab-veic').innerHTML = `<thead><tr><th>Veículo</th><th class="n">Reportagens</th><th class="n">Cita a Mensa</th>${TV.map(t => `<th class="n">${CURTO[t]}</th>`).join('')}</tr></thead><tbody>` +
  D.veiculos.map(v => `<tr><td><b>${esc(v.veiculo)}</b></td><td class="n">${v.reportagens}</td><td class="h" style="${heat(v.mensa, 100)}">${Math.round(v.mensa)}%</td>${TV.map(t => `<td class="h" style="${heat(v.temas[t] || 0, 45)}">${v.temas[t] ? Math.round(v.temas[t]) + '%' : '·'}</td>`).join('')}</tr>`).join('') + '</tbody>';
const EQ = Object.keys(D.enquadramentos);
$('#tab-rev').innerHTML = `<thead><tr><th>Revista</th><th class="n">Artigos</th>${EQ.map(e => `<th class="n">${esc(D.enquadramentos[e])}</th>`).join('')}</tr></thead><tbody>` +
  D.revistas.map(r => `<tr><td><b>${esc(r.revista)}</b></td><td class="n">${r.artigos}</td>${EQ.map(e => `<td class="h" style="${heat(r.enquadramento[e], 50)}">${Math.round(r.enquadramento[e])}%</td>`).join('')}</tr>`).join('') + '</tbody>';
// rodape mantido limpo conforme solicitacao
const elRodape = $('#rodape');
if (elRodape) elRodape.textContent = '';

/* vídeos: incorporados diretamente com lazy loading */
function embed(v) {
  if (v.rede === 'YouTube') return `https://www.youtube-nocookie.com/embed/${v.id}?rel=0`;
  if (v.rede === 'TikTok') return `https://www.tiktok.com/embed/v2/${v.id}`;
  return `https://www.instagram.com/p/${v.id}/embed/`;
}
function cartaoVideo(v, comInfo = true) {
  const vert = v.rede !== 'YouTube';
  const big = v.views ? `${c(v.views)}<small>views</small>` : `${c(v.likes)}<small>curtidas</small>`;
  const src = embed(v);
  return `<div class="tela${vert ? ' vert' : ''}"><iframe src="${esc(src)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy" title="${esc(v.titulo)}"></iframe><span class="rede-tag">${v.rede}</span><span class="big">${big}</span></div>` +
    (comInfo ? `<div class="info"><b>${esc(v.titulo)}</b><p>${esc(v.contexto)}</p><div class="met">${esc(v.autor)} · ${v.ano} · ${v.views ? c(v.views) + ' views · ' : ''}${c(v.likes)} curtidas · ${c(v.comentarios)} comentários · <a class="abrir" href="${esc(v.url)}" target="_blank" rel="noopener">abrir ↗</a></div></div>` : '');
}
$('#videos').innerHTML = D.videos_impacto.map(v => `<div class="vid">${cartaoVideo(v)}</div>`).join('');
$('#video-mensa').innerHTML = cartaoVideo(D.video_mensa);

/* temas no tempo */
const ST = D.serie_temas, SA = ST.semestres;
const temasSerie = Object.keys(D.rotulos_tema).filter(k => k !== 'outro');
let temaSel = 'saude_mental_neuro';
/* temas no tempo: doze pequenos gráficos, comentários e reportagens */
(() => {
  const nome = {entretenimento_humor: 'Humor', validade_testes_qi: 'Validade do QI', experiencia_pessoal: 'Experiência pessoal', diagnostico_avaliacao: 'Diagnóstico', saude_mental_neuro: 'Saúde mental', elitismo_arrogancia: 'Elitismo', caracteristicas_sinais: 'Sinais', elogio_admiracao: 'Elogio', mensa_sociedade: 'A Mensa', educacao_escola: 'Escola', politica_publica: 'Política pública', custo_acesso: 'Custo e acesso'};
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toLocaleString('pt-BR', {maximumFractionDigits: 1});
  const cls = v => v >= 2 ? 'sobe' : v <= -2 ? 'desce' : 'igual';
  const L = temasSerie.map(k => {
    const cm = ST.comentarios[k].pct.map(v => v ?? 0), rp = ST.reportagens[k].pct.map(v => v ?? 0);
    return {k, cm, rp, dc: cm[5] - cm[0], dr: rp[5] - rp[0]};
  }).sort((a, b) => Math.abs(b.dc) + Math.abs(b.dr) - Math.abs(a.dc) - Math.abs(a.dr));
  $('#multiplos').innerHTML = L.map(({k, cm, rp, dc, dr}) => {
    const mx = Math.max(1, ...cm, ...rp), x = i => 6 + 228 * i / 5, y = v => (96 - 86 * v / mx).toFixed(1);
    const pts = a => a.map((v, i) => x(i) + ',' + y(v)).join(' ');
    return `<article class="mult"><div class="mult-cab"><span class="mic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_TEMA[k] || ''}"/></svg></span><h4>${esc(nome[k] || D.rotulos_tema[k])}</h4><span>até ${Math.round(mx)}%</span></div>
      <svg viewBox="0 0 240 104" role="img" aria-label="${esc(D.rotulos_tema[k])}: comentários de ${p(cm[0])} para ${p(cm[5])}, reportagens de ${p(rp[0])} para ${p(rp[5])}">
        <line x1="6" y1="96" x2="234" y2="96" stroke="var(--line)"/>
        <polyline points="${pts(rp)}" fill="none" stroke="var(--spark)" stroke-width="2.5" stroke-linejoin="round"/>
        <polyline points="${pts(cm)}" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linejoin="round"/>
        <circle cx="${x(5)}" cy="${y(cm[5])}" r="4" fill="var(--accent)"/><circle cx="${x(5)}" cy="${y(rp[5])}" r="4" fill="var(--spark)"/>
      </svg>
      <div class="mult-anos"><span>2021</span><span>2026</span></div>
      <div class="mult-d"><div><b class="${cls(dc)}">${fmt(dc)}</b><span>comentários, p.p.</span></div><div><b class="${cls(dr)}">${fmt(dr)}</b><span>reportagens, p.p.</span></div></div>
    </article>`;
  }).join('');
  const seta = {cima: 'M12 19V5 M5 12l7-7 7 7', baixo: 'M12 5v14 M5 12l7 7 7-7'};
  const ch = (k, campo, txt) => {
    const it = L.find(x => x.k === k), v = it[campo];
    return `<div class="chip-t"><span class="pic" style="background:${v >= 0 ? 'var(--spark)' : 'var(--neg)'}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${v >= 0 ? seta.cima : seta.baixo}"/></svg></span><div><b class="${cls(v)}">${fmt(v)} p.p.</b><span>${txt}</span></div></div>`;
  };
  $('#temas-chips').innerHTML = ch('entretenimento_humor', 'dc', 'de piada sobre QI nos comentários') + ch('politica_publica', 'dr', 'de política pública nas reportagens') + ch('mensa_sociedade', 'dr', 'de Mensa como tema principal das reportagens');
})();
const seta = d => d > 0.5 ? `<span class="seta-up">▲ ${d.toLocaleString('pt-BR', {maximumFractionDigits: 1})}</span>` : d < -0.5 ? `<span class="seta-dn">▼ ${Math.abs(d).toLocaleString('pt-BR', {maximumFractionDigits: 1})}</span>` : '<span style="color:var(--muted)">=</span>';
const VAR = temasSerie.map(k => {
  const a = ST.comentarios[k].pct, b = ST.reportagens[k].pct;
  return {k, c0: a[0], c1: a[5], r0: b[0], r1: b[5], dc: a[5] - a[0], dr: b[5] - b[0]};
}).sort((u, v) => Math.abs(v.dc) + Math.abs(v.dr) - Math.abs(u.dc) - Math.abs(u.dr));
$('#tab-var').innerHTML = `<thead><tr><th>Tema</th><th class="n">Comentários 2021</th><th class="n">2026</th><th class="n">Variação (p.p.)</th><th class="n">Reportagens 2021</th><th class="n">2026</th><th class="n">Variação (p.p.)</th></tr></thead><tbody>` +
  VAR.map(r => `<tr><td><a href="#serie" data-k="${r.k}" class="ver-serie">${esc(D.rotulos_tema[r.k])}</a></td><td class="n">${p(r.c0)}</td><td class="n">${p(r.c1)}</td><td class="n">${seta(r.dc)}</td><td class="n">${p(r.r0)}</td><td class="n">${p(r.r1)}</td><td class="n">${seta(r.dr)}</td></tr>`).join('') + '</tbody>';
$('#tab-var').onclick = e => { const a = e.target.closest('.ver-serie'); if (a) { e.preventDefault(); serie(a.dataset.k); $('#serie').scrollIntoView({behavior: 'smooth', block: 'center'}); } };

/* dúvidas e angústias */
const DV = D.duvidas;
if (DV && DV.categorias.length) {
  const C = DV.categorias, t1 = C[0], t2 = C[1];
  $('#duv-lead').innerHTML = `Em <span>${p(100 * DV.com_duvida / DV.amostra)}</span> dos comentários que perguntam ou desabafam há uma dúvida ou angústia real. As mais comuns: <span>${esc(t1.titulo)}</span> (${p(t1.pct)}) e <span>${esc(t2.titulo)}</span> (${p(t2.pct)}).`;
  hb('#duv-barras', C.map(x => [x.titulo, x.pct]), p);
  const fontes = Object.keys(DV.por_fonte);
  const tot = Object.fromEntries(fontes.map(f => [f, Object.values(DV.por_fonte[f]).reduce((a, b) => a + b, 0) || 1]));
  $('#tab-duv-fonte').innerHTML = `<thead><tr><th>Dúvida</th>${fontes.map(f => `<th class="n">${f}</th>`).join('')}</tr></thead><tbody>` +
    C.map(x => `<tr><td>${esc(x.titulo)}</td>${fontes.map(f => { const v = 100 * (DV.por_fonte[f][x.chave] || 0) / tot[f]; return `<td class="h" style="${heat(v, 40)}">${Math.round(v)}%</td>`; }).join('')}</tr>`).join('') + '</tbody>';
  const dif = C.map(x => [x.titulo, 100 * (DV.por_fonte.Instagram[x.chave] || 0) / tot.Instagram - 100 * (DV.por_fonte.YouTube[x.chave] || 0) / tot.YouTube]).sort((a, b) => b[1] - a[1]);
  $('#duv-fonte-nota').textContent = `Percentual das dúvidas de cada rede. O Instagram concentra mais "${dif[0][0]}" e "${dif[1][0]}"; o YouTube, mais "${dif[dif.length - 1][0]}" e "${dif[dif.length - 2][0]}".`;
  const ICONE_DUV = {
  sofrimento_mental: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M16 16s-1.5-2-4-2-4 2-4 2 M9 9h.01 M15 9h.01',
  tdah_autismo_ou_sd: 'M12 2a7 7 0 0 0-7 7c0 3 2 4 2 7h10c0-3 2-4 2-7a7 7 0 0 0-7-7z M9 21h6 M10 17v4 M14 17v4',
  solidao_nao_se_encaixa: 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1',
  sera_que_sou: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3 M12 17h.01',
  teste_qi_vale: 'M9 11l3 3 8-8 M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9',
  duvida_sobre_filho: 'M9 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M17 11a2 2 0 1 0 0-4 2 2 0 0 0 0 4z M3 21v-3a5 5 0 0 1 10 0v3 M14 21v-2a3 3 0 0 1 6 0v2',
  potencial_frustrado: 'M3 17l6-6 4 4 8-8 M21 7v6 M21 7h-6',
  escola_e_bullying: 'M22 10L12 5 2 10l10 5 10-5z M6 12v5c3 2 9 2 12 0v-5',
  como_avaliar_custo: 'M12 1v22 M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
  como_entrar_mensa: 'M3 21h18 M5 21V8l7-5 7 5v13 M9 21v-6h6v6',
};
$('#duv').innerHTML = C.map(x => `<div class="card"><div class="duv-cab"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_DUV[x.chave] || ''}"/></svg></span><div class="pct">${p(x.pct)}</div></div><h3>${esc(x.titulo)}</h3><p class="desc">${esc(x.desc)} · ${n(x.n)} comentários · ${n(x.likes)} curtidas somadas</p>
    ${x.exemplos.map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} curtidas · ${e.fonte}${fonteLink(e)}</small></blockquote>`).join('')}<div class="fundo" style="width:${x.pct * 2.5}%"></div></div>`).join('');
  $('#duv-nota').textContent = `Amostra de ${n(DV.amostra)} comentários classificados pela nossa IA (${Object.entries(DV.amostra_fonte).map(([f, q]) => n(q) + ' do ' + f).join(', ')}); ${n(DV.com_duvida)} expressam dúvida ou angústia. Percentuais sobre esses ${n(DV.com_duvida)}. Comentários sem autor; trechos com números, links ou marcações foram excluídos.`;
} else {
  $('#duv-lead').textContent = 'Classificação em andamento.';
}

/* fundo da abertura: rede de neurônios em verde */
const cv = document.querySelector('#rede-neural');
if (cv) {
const ctx = cv.getContext('2d');
let pts = [], W = 0, H = 0;
function tam() {
  const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
  W = r.width; H = r.height; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0);
  const q = Math.round(W * H / 14000);
  pts = Array.from({length: q}, () => ({x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25}));
}
const parado = matchMedia('(prefers-reduced-motion: reduce)').matches;
function quadro() {
  const a = getComputedStyle(raiz).getPropertyValue('--accent').trim();
  ctx.clearRect(0, 0, W, H);
  for (const q of pts) { q.x += q.vx; q.y += q.vy; if (q.x < 0 || q.x > W) q.vx *= -1; if (q.y < 0 || q.y > H) q.vy *= -1; }
  ctx.strokeStyle = a; ctx.fillStyle = a;
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
    const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y, d = dx * dx + dy * dy;
    if (d < 13000) { ctx.globalAlpha = .28 * (1 - d / 13000); ctx.beginPath(); ctx.moveTo(pts[i].x, pts[i].y); ctx.lineTo(pts[j].x, pts[j].y); ctx.stroke(); }
  }
  ctx.globalAlpha = .7;
  for (const q of pts) { ctx.beginPath(); ctx.arc(q.x, q.y, 1.6, 0, 7); ctx.fill(); }
  ctx.globalAlpha = 1;
  if (!parado) requestAnimationFrame(quadro);
}
tam(); quadro(); addEventListener('resize', () => { tam(); if (parado) quadro(); });
}
})();
