(() => {
const D = window.DADOS;
// Cada página tem só parte dos blocos: o que não existir vira um elemento solto e é ignorado.
const $ = s => document.querySelector(s) || document.createElement('div');
const nf = new Intl.NumberFormat('en-US');
const n = x => x == null ? '–' : nf.format(Math.round(x));
const c = x => {
  if (x == null || x === 0) return x === 0 ? '0' : '–';
  if (x >= 1e6) return (x / 1e6).toLocaleString('en-US', {maximumFractionDigits: 1}) + 'M';
  if (x >= 1e4) return (x / 1e3).toLocaleString('en-US', {maximumFractionDigits: 0}) + 'K';
  return n(x);
};
const p = x => (x ?? 0).toLocaleString('en-US', {maximumFractionDigits: 1}) + '%';
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
$('#hero-lead').innerHTML = `Allow us to explain. We initiated this investigation with a question deceptively simple to articulate yet computationally arduous to measure: how does Brazil actually discuss giftedness? To address this with the empirical rigor it demands, we assembled 98,861 comments, 870 YouTube and TikTok videos (transcribed verbatim—yes, every single syllable), 708 posts with complete engagement metrics, and 1,264 news reports. A curious, statistically verifiable fact: between 2021 and 2026, annual headlines surged from 53 to 411. That represents an increase of 675%, or a 7.75-fold multiplication, if you appreciate formal mathematical elegance. The general public, however, remains hopelessly conflated between two entirely distinct phenomena sharing the same vocabulary: the superficial fascination with an IQ number, and the urgent search for answers regarding neurodivergence and genuine psychological distress.`;
const ME = D.medicao;
const somaM = (campo, redes) => redes.reduce((a, r) => a + (ME[r][campo] || 0), 0);
const faixa = [
  ['74.3M', 'measured reach in video views', `TikTok 39.5M · YouTube 30.7M · Instagram 3.8M · X 360K`],
  ['29.4M', 'potential audience on Instagram', `aggregate reach across 87 monitored specialized profiles (with 207K likes and 17K comments)`],
  ['4.4M', 'likes recorded', `TikTok 2.9M · YouTube 1.4M · Instagram 207K · X 2,293`],
  ['192K', 'comments & replies', `YouTube 113K · TikTok 61K · Instagram 17K · X 1,257 replies`],
];
$('#faixa').innerHTML = faixa.map(([a, b, d]) => `<div><b>${a}</b><span>${b}</span><small>${d}</small></div>`).join('');
$('#carimbo').textContent = `Temporal scope: 2021 to 2026 · Data collected through October 27, 2026 · Generated on ${D.gerado_em}`;

/* 00 fontes */
const R = Object.fromEntries(D.redes.map(r => [r.rede, r]));
const semM = 'no metrics';
const linhaF = (nome, papel, itens, r) => `<tr><td><b>${nome}</b></td><td>${papel}</td><td class="n">${itens}</td><td class="n">${r.views != null ? c(r.views) + ' views' : r.seguidores ? c(r.seguidores) + ' seguidores*' : semM}</td><td class="n">${r.likes != null ? c(r.likes) : semM}</td><td class="n">${r.coments != null ? c(r.coments) : semM}</td></tr>`;
$('#tab-fontes').innerHTML = `<thead><tr><th>Source</th><th>Function & Role</th><th class="n">Items</th><th class="n">Reach</th><th class="n">Likes</th><th class="n">Comments</th></tr></thead><tbody>` +
  linhaF('YouTube', 'In-depth explanations and long-form video', `${n(ME.YouTube.itens)} videos`, ME.YouTube) +
  linhaF('TikTok', 'Short-form video, viral identity & traits', `${n(ME.TikTok.itens)} videos`, ME.TikTok) +
  linhaF('Instagram', 'Clinicians, families & celebrity stories', `${n(ME.Instagram.itens)} posts`, ME.Instagram) +
  linhaF('X', 'Journalism, debate & rapid reaction', `${n(ME.X.itens)} posts`, ME.X) +
  linhaF('Imprensa', 'Portals, newspapers & academic journals', `${n(N.reportagens_classificadas)} reports · ${n(N.revistas_artigos)} journal articles`, ME.Imprensa) +
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
    ['YouTube', 'Educates & entertains', ME.YouTube, 'videos'],
    ['TikTok', 'Forms identity', ME.TikTok, 'videos'],
    ['Instagram', 'Clinical clinic & showcase', ME.Instagram, 'posts'],
    ['X', 'Rapid reaction', ME.X, 'posts'],
    ['Press', 'Sets public agenda', ME.Imprensa, 'reports'],
  ];
  const mx = {views: Math.max(ME.YouTube.views, ME.TikTok.views, ME.Instagram.seguidores), likes: Math.max(ME.YouTube.likes, ME.TikTok.likes), coments: Math.max(ME.YouTube.coments, ME.TikTok.coments)};
  const bol = (v, m, rot, cor, anel) => v == null
    ? `<div class="bol"><i style="width:26px;height:26px;border:1px dashed var(--cinza2)"></i><b class="mu">sem métrica</b><span>${rot}</span></div>`
    : `<div class="bol"><i style="width:${Math.max(8, 60 * Math.sqrt(v / m))}px;height:${Math.max(8, 60 * Math.sqrt(v / m))}px;${anel ? 'border:3px solid ' + cor : 'background:' + cor}"></i><b>${c(v)}</b><span>${rot}</span></div>`;
  $('#fontes-visual').innerHTML = F.map(([rede, papel, r, un]) => `<article class="fcard">
    <span class="fic" style="background:${COR_REDE[rede]}">${ico(rede, 30, 'var(--bg)')}</span>
    <h3>${rede}</h3><div class="fpapel">${papel}</div>
    <div class="fitens"><b>${n(r.itens)}</b><span>${un}</span></div>
    <div class="bols">${bol(r.views ?? (r.seguidores || null), mx.views, r.seguidores ? 'followers' : 'views', COR_REDE[rede], !!r.seguidores)}${bol(r.likes, mx.likes, 'likes', COR_REDE[rede])}${bol(r.coments, mx.coments, rede === 'X' ? 'replies' : 'comments', COR_REDE[rede])}</div>
  </article>`).join('');
  const dom = (nome, campo, redes) => {
    const tot = redes.reduce((a, r) => a + (ME[r][campo] || 0), 0);
    return `<div class="dom"><span>${nome}</span><div>${redes.filter(r => ME[r][campo]).map(r => { const p = 100 * ME[r][campo] / tot; return `<i style="width:${p}%;background:${COR_REDE[r]}" title="${r} ${Math.round(p)}%">${p >= 7 ? r + ' ' + Math.round(p) + '%' : ''}</i>`; }).join('')}</div></div>`;
  };
  $('#fontes-dominio').innerHTML = dom('Reach', 'views', ['TikTok', 'YouTube']) + dom('Likes', 'likes', ['TikTok', 'YouTube', 'Instagram']) + dom('Comments', 'coments', ['YouTube', 'TikTok', 'Instagram', 'X']);
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
  ['2021', 'IQ Becomes a Spectacle', '47%', 'of comments are memes regarding one\'s own IQ', 'Mensa resumes in-person supervised testing'],
  ['2022', 'Mensa Turns 20 in Brazil', '131', 'headlines, more than double 2021', 'School accommodation becomes mainstream press focus'],
  ['2023', 'TikTok Discovers Giftedness', '3.7M', 'views on viral video dissecting sensory overload', 'Giftedness transforms into an online identity'],
  ['2024', 'Adults Discover Themselves', '1.9M', 'views on \"The Truth About IQ Tests\"', 'Late adult diagnosis captures serious journalistic attention'],
  ['2025', 'Celebrities & ADHD Intersection', '18.8K', 'YouTube comments in a single calendar year', 'Dual exceptionality enters broader public discourse'],
  ['2026', 'Federal Law & The Child Prodigy', '411', 'headlines, setting an all-time dataset record', 'Law 15,436 enacted and gifted youth speaks at Federal Senate'],
];
$('#atos').innerHTML = ATOS.map(([a, t, num, leg, fato]) => `<article class="ano-card">
  <div class="ano-img"><img src="img/ano${a}.jpg" alt="" loading="lazy" onerror="this.src='img/capa.jpg'"><span>${a}</span></div>
  <div class="ano-txt"><h3>${t}</h3><div class="ano-num"><b>${num}</b><span>${leg}</span></div><p>${fato}</p></div>
</article>`).join('');

/* o Congresso em síntese */
$('#congresso').innerHTML = `<div class="cong-top"><div><b>18</b><span>of the 21 legislative proposals found in Congress were drafted in 2026</span></div>
  <div class="cong-funil" aria-label="21 propostas, 1 lei">${Array.from({length: 21}, (_, i) => `<i class="${i ? '' : 'lei'}"></i>`).join('')}<span><b>21 proposals, 1 federal law</b> (Federal Law 15,436, June 2026, enacted with vetoes)</span></div></div>
  <div class="cong-pautas">${[
    ['5', 'The School System', 'Student identification, monitoring, and specialized support', 'M22 10L12 5 2 10l10 5 10-5z M6 12v5c3 2 9 2 12 0v-5'],
    ['4', 'Broad Inclusion', 'Neurodiversity rights, inclusive education fund, legal oversight', 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.9 M16 3.1a4 4 0 0 1 0 7.8'],
    ['3', 'National Policy', 'Federal registry, comprehensive data systems; 1 enacted into law', 'M3 22h18 M6 18v-7 M10 18v-7 M14 18v-7 M18 18v-7 M12 2l8 5H4z'],
    ['3', 'Legislative Debate', 'Senate public hearings and motions challenging Ministry mandates', 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z M8 9h8 M8 13h5'],
    ['2', 'Public Healthcare', 'Neuropsychological assessments and mental health outpatient centers', 'M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 12 5a5.5 5.5 0 0 0-10 3.5c0 2.3 1.5 4 3 5.5l7 7z'],
    ['2', 'National Visibility', 'National Giftedness Day and the Violet August campaign', 'M8 2v4 M16 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z'],
  ].map(([q, t, d, ic]) => `<div class="pauta"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ic}"/></svg></span><b>${q}</b><h4>${t}</h4><p>${d}</p></div>`).join('')}</div>`;



/* 02 temas */
const T = D.temas.filter(t => t.tema !== 'outro').concat(D.temas.filter(t => t.tema === 'outro'));
const mxT = Math.max(...T.map(t => Math.max(t.pct_comentarios, t.pct_videos, t.pct_reportagens, t.pct_views)));
const bar = (v, cls = '') => `<div class="cel"><div class="barra ${cls}" style="width:${70 * v / mxT}px"></div>${p(v)}</div>`;
$('#tab-temas2').innerHTML = `<thead><tr><th>Theme</th><th>Comments</th><th>Videos</th><th>Video Views</th><th>Press Reports</th><th class="n">Likes / Comment</th></tr></thead><tbody>` +
  T.map(t => `<tr><td>${esc(t.rotulo)}</td><td>${bar(t.pct_comentarios)}</td><td>${bar(t.pct_videos, 'b2')}</td><td>${bar(t.pct_views, 'b2')}</td><td>${bar(t.pct_reportagens, 'b3')}</td><td class="n">${t.likes_por_comentario.toLocaleString('en-US')}</td></tr>`).join('') + '</tbody>';
const tv = Object.fromEntries(D.temas.map(t => [t.tema, t]));
$('#temas-lead').innerHTML = `Validity of IQ Tests: <span>${p(tv.validade_testes_qi.pct_comentarios)}</span> of comments vs. <span>${p(tv.validade_testes_qi.pct_reportagens)}</span> of press reports. Education & Schooling: <span>${p(tv.educacao_escola.pct_reportagens)}</span> of press coverage vs. <span>${p(tv.educacao_escola.pct_comentarios)}</span> of public comments.`;

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
}).join('') + `<div class="legenda"><span style="--c:var(--neg)">Detractor</span><span style="--c:var(--neu)">Neutral</span><span style="--c:var(--pos)">Supporter</span></div>
<p class="leitura">In user comments, <b>${p(100 * 894 / 1461)}</b> of those citing Mensa criticize it, almost invariably citing one of two arguments: the perception of an elitist club or the premise that psychometric testing fails to quantify intelligence. In journalistic coverage, however, an entirely different pattern emerges. Mensa is cited primarily as a neutral authoritative source, with merely <b>1</b> negative headline out of ${n(408)} total reports: precisely 0.25%. Statistically speaking, that is functionally zero.</p>`;
hb('#mensa-temas', D.mensa.temas_comentarios.map(t => [t.rotulo, t.pct]), p);
const MC = D.mensa.canal;
$('#mensa-canais').innerHTML = `<dl style="display:grid;grid-template-columns:1fr auto;gap:8px 12px;font-size:15px">
<dt>Official YouTube Channel</dt><dd class="n">${MC.videos} videos · ${n(MC.views)} views</dd>
${D.mensa.redes.map(r => `<dt>${r.rede} @${esc(r.handle)}</dt><dd class="n">${r.posts} posts · ${n(r.likes)} likes${r.seguidores ? ' · ' + c(r.seguidores) + ' followers' : ''}</dd>`).join('')}
</dl><p class="nota">O vídeo mais visto do canal tem ${n(MC.melhor_views)} views ("${esc(MC.melhor)}"). For comparative calibration: a single third-party logic quiz video easily surpasses 1 million views.</p>`;
$('#tab-mensa-videos').innerHTML = `<thead><tr><th>Video</th><th>Channel</th><th>Year</th><th>Theme</th><th class="n">Views</th></tr></thead><tbody>` +
  D.mensa.videos_top.map(v => `<tr><td><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titulo)}</a></td><td>${esc(v.canal)}</td><td>${v.ano}</td><td>${esc(v.tema)}</td><td class="n">${n(v.views)}</td></tr>`).join('') + '</tbody>';

/* 04 influenciadores */
const CAT = {psicologo: 'Psychologist', medico: 'Physician / Neurologist', entidade_instituicao: 'Institution', entidade: 'Institution', superdotado_criador: 'Gifted Creator', ator_celebridade: 'Celebrity', educador_pesquisador: 'Educator / Researcher', outro: 'Other'};
/* fichas: nomes relevantes com foto e a rede onde atuam */
(() => {
  const P = ((D.mapa || {}).pessoas || []).slice();
  const eng = p => p.likes + p.coments + p.views / 20;
  const foco = P.filter(p => p.foco);
  const orgs = ((D.mapa || {}).orgs || []).map(o => ({...o, cluster: o.papel, isOrg: true}));
  const lista = [...foco, ...orgs, ...P.filter(p => !p.foco).sort((a, b) => eng(b) - eng(a))].slice(0, 32);
  let filtro = 'All';
  const ficha = p => `<a class="ficha" href="mapa.html#foco">
    ${foto(p.id, p.nome, 'g')}
    <div class="fn">${esc(p.nome)}</div>
    <div class="fp">${esc(p.cluster || p.papel || '')}</div>
    <div class="fr">${Object.keys(p.redes || {}).map(r => `<span title="${r}" style="color:${COR_REDE[r]}">${ico(r, 16)}</span>`).join('')}</div>
    <div class="fm">${p.seguidores ? c(p.seguidores) + ' followers' : p.views ? c(p.views) + ' views' : c(p.likes) + ' likes'}</div></a>`;
  function render() {
    const L = filtro === 'All' ? lista : filtro === 'Organizations' ? orgs : lista.filter(p => (p.redes || {})[filtro]);
    $('#fichas').innerHTML = L.map(ficha).join('');
    document.querySelectorAll('#fichas-abas button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === filtro));
  }
  $('#fichas-abas').innerHTML = ['All', 'Instagram', 'TikTok', 'YouTube', 'Organizations'].map(f => `<button data-f="${f}">${f}</button>`).join('');
  $('#fichas-abas').onclick = e => { if (e.target.dataset.f) { filtro = e.target.dataset.f; render(); } };
  render();
})();
const REDES = ['TikTok', 'YouTube', 'Instagram', 'X'];
const NOTA_INF = {
  TikTok: 'Ordered by views. Reach = cumulative views across on-topic videos; comments = count reported by TikTok platform.',
  YouTube: 'Ordered by views. Subscribers = channel subscriber count on the date of harvesting.',
  Instagram: 'Ordered by likes. Instagram restricts view telemetry on image posts; reach represents follower base. Comments = harvested comments.',
  X: 'Data extraction from X returned zero for native like and repost counts. Outlets and institutions are listed solely by topical post volume.',
};
function tabInf(rede) {
  const L = D.influenciadores[rede];
  $('#tab-inf').innerHTML = `<thead><tr><th>#</th><th>Profile</th>${rede === 'Instagram' ? '<th>Category</th>' : ''}<th class="n">Content Count</th><th class="n">Followers</th><th class="n">Views</th><th class="n">Likes</th><th class="n">Comments</th></tr></thead><tbody>` +
    L.map((x, i) => `<tr><td>${i + 1}</td><td><b>${rede === 'YouTube' ? '' : '@'}${esc(x.autor)}</b></td>${rede === 'Instagram' ? `<td>${esc(CAT[x.categoria] || '–')}</td>` : ''}<td class="n">${n(x.itens)}</td><td class="n">${c(x.seguidores)}</td><td class="n">${c(x.views)}</td><td class="n">${rede === 'X' ? '–' : c(x.likes)}</td><td class="n">${rede === 'X' ? '–' : c(x.comentarios)}</td></tr>`).join('') + '</tbody>';
  $('#inf-nota').textContent = NOTA_INF[rede];
  document.querySelectorAll('#abas-inf button').forEach(b => b.setAttribute('aria-selected', b.dataset.r === rede));
}
$('#abas-inf').innerHTML = REDES.map(r => `<button role="tab" data-r="${r}">${r}</button>`).join('');
$('#abas-inf').onclick = e => { if (e.target.dataset.r) tabInf(e.target.dataset.r); };
tabInf('TikTok');
$('#tab-multi').innerHTML = `<thead><tr><th>Profile</th><th>Platforms (Posts)</th><th class="n">Followers</th><th class="n">Views</th><th class="n">Likes</th><th class="n">Comments</th></tr></thead><tbody>` +
  D.multirrede.map(x => `<tr><td><b>${esc(x.autor)}</b></td><td>${Object.entries(x.redes).map(([r, k]) => `<span class="chip">${r} ${k}</span>`).join('')}</td><td class="n">${c(x.seguidores)}</td><td class="n">${c(x.views)}</td><td class="n">${c(x.likes)}</td><td class="n">${c(x.comentarios)}</td></tr>`).join('') + '</tbody>';

/* 05 clusters */
$('#cl').innerHTML = D.clusters.map((k, i) => {
  const tr = Object.entries(k.perfil).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const IMG_CL = {'Clínica e avaliação': 'cl_clinica', 'QI como espetáculo': 'cl_espetaculo', 'Neurodivergência e podcasts': 'cl_neuro', 'Educação, famílias e direitos': 'cl_educacao', 'Descoberta adulta': 'cl_adulto', 'Mensa e mídia': 'cl_midia'};
  return `<div class="cl"><div class="cl-img"><img src="img/${IMG_CL[k.nome.nome] || 'capa'}.jpg" alt="" loading="lazy" onerror="this.src='img/capa.jpg'"></div><div class="n">Cluster ${i + 1} · ${k.n} creators</div><h3>${esc(k.nome.nome)}</h3><p style="font-size:15px;color:var(--ink2)">${esc(k.nome.desc)}</p>
  <div class="m"><div><b>${c(k.views)}</b><span>views</span></div><div><b>${c(k.likes)}</b><span>likes</span></div><div><b>${c(k.comentarios)}</b><span>comments</span></div></div>
  <div class="mini">${tr.map(([g, v]) => `<div>${esc(D.grupos[g])}</div><div class="tr"><i style="width:${v}%"></i></div><div class="v">${Math.round(v)}%</div>`).join('')}</div>
  <div class="avs">${k.membros.map(m => `<span class="av-m" title="${esc(m.autor)} · ${n(m.likes)} likes · ${n(m.views)} views · ${n(m.comentarios)} comments">${foto(m.id, m.autor)}<small>${esc(String(m.autor).replace(/^@/, '').slice(0, 16))}</small></span>`).join('')}</div>
  <div style="font-size:13px;color:var(--muted)">${Object.entries(k.redes).sort((a, b) => b[1] - a[1]).map(([r, q]) => `${r} ${q}`).join(' · ')} posts</div></div>`;
}).join('');
$('#cl-nota').textContent = `Critério: ${D.clusters_base.criadores} criadores com ${D.clusters_base.minimo_itens} ou mais conteúdos sobre o tema (com menos que isso, não dá para medir vocabulário com segurança). As barras mostram o percentual dos conteúdos do grupo que usam termos de cada assunto. Toque ou passe o mouse sobre um perfil para ver curtidas, views e comments.`;

/* 06 comments */
const NV = D.nuvem;
const FONTES_NV = {todas: 'All Sources', youtube: 'YouTube Comments', instagram: 'Instagram Comments', tiktok: 'TikTok Speech & Captions', x: 'X Posts & Replies'};
const temasNv = [['todos', 'All Themes']].concat(Object.keys(D.rotulos_tema).filter(k => k !== 'outro').map(k => [k, D.rotulos_tema[k]]));
const filtroNv = {fonte: 'todas', tema: 'todos', ano: 'todos'};
function nuvem() {
  const {fonte, tema, ano} = filtroNv;
  const L = (fonte === 'youtube' ? (NV.youtube && NV.youtube[tema + '|' + ano]) : (NV[fonte] && NV[fonte][ano])) || [];
  if (L.length < 5) {
    $('#nuvem').innerHTML = `<p class="nota" style="margin:auto">Insufficient textual density exists within this specific cross-section to generate recurring bi-grams. Drawing inferences from miniature samples is an empirical catastrophe that we adamantly avoid. Select another year, theme, or platform.</p>`;
  } else {
    const mx = L[0][1], mn = L[L.length - 1][1];
    // embaralha de forma estavel para a nuvem nao virar lista ordenada
    const ord = L.map((x, i) => [x, i]).sort((a, b) => ((a[1] * 37) % 11) - ((b[1] * 37) % 11));
    $('#nuvem').innerHTML = ord.map(([[t, q], i]) => `<span class="${i < 3 ? 't1' : i < 8 ? 't2' : ''}" style="font-size:${16 + 34 * Math.sqrt((q - mn) / Math.max(1, mx - mn))}px" title="${n(q)} ${fonte === 'tiktok' ? 'videos' : 'texts'}">${esc(t)}<sup>${n(q)}</sup></span>`).join('');
  }
  const periodo = ano === 'todos' ? ', 2021 to 2026' : ', ' + ano;
  $('#nuvem-nota').textContent = `${FONTES_NV[fonte]}${fonte === 'youtube' && tema !== 'todos' ? ', theme "' + D.rotulos_tema[tema] + '"' : ''}${periodo}. The 20 most frequent adjacent word pairs (bi-grams); the superscript number indicates how many distinct ${fonte === 'tiktok' ? 'videos' : 'texts'} contain the pair. Stop words, punctuation, numerals, and interface artifacts were rigorously purged.`;
  $('#filtro-tri').hidden = fonte !== 'youtube';
  document.querySelectorAll('#filtro-fonte button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === fonte));
  document.querySelectorAll('#filtro-tri button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === tema));
  document.querySelectorAll('#filtro-tri-ano button').forEach(b => b.setAttribute('aria-pressed', b.dataset.a === ano));
}
$('#filtro-fonte').innerHTML = Object.entries(FONTES_NV).map(([f, l]) => `<button data-f="${f}">${l}</button>`).join('');
$('#filtro-fonte').onclick = e => { if (e.target.dataset.f) { filtroNv.fonte = e.target.dataset.f; nuvem(); } };
$('#filtro-tri').innerHTML = temasNv.map(([k, l]) => `<button data-k="${k}">${esc(l)}</button>`).join('');
$('#filtro-tri').onclick = e => { if (e.target.dataset.k) { filtroNv.tema = e.target.dataset.k; nuvem(); } };
$('#filtro-tri-ano').innerHTML = ['todos', ...D.anual.anos.map(String)].map(a => `<button data-a="${a}">${a === 'todos' ? 'All Years' : a}</button>`).join('');
$('#filtro-tri-ano').onclick = e => { if (e.target.dataset.a) { filtroNv.ano = e.target.dataset.a; nuvem(); } };
nuvem();
const fonteLink = e => e.url ? ` · <a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.onde || 'ver o post')} ↗</a>` : '';
$('#vozes').innerHTML = D.vozes.filter(v => v.exemplos.length).map(v => `<div class="card voz"><div class="voz-cab"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_TEMA[v.tema] || ''}"/></svg></span><h4>${esc(v.rotulo)}</h4></div>${v.exemplos.map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} likes · YouTube · ${e.ano}${fonteLink(e)}</small></blockquote>`).join('')}</div>`).join('');
$('#vozes-ig').innerHTML = D.vozes_instagram.slice(0, 6).map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} likes · Instagram${fonteLink(e)}</small></blockquote>`).join('');

const heat = (v, mx) => `background:color-mix(in srgb, var(--accent) ${Math.round(85 * v / mx)}%, transparent)`;
const G = Object.keys(D.grupos).filter(k => k !== 'humor' || true);
const CL = D.comentarios_lexico, cmx = Math.max(...Object.values(CL).flatMap(o => Object.values(o)));
$('#tab-com-lex').innerHTML = `<thead><tr><th>Assunto</th>${Object.keys(CL).map(r => `<th class="n">${r}</th>`).join('')}</tr></thead><tbody>` +
  G.map(g => `<tr><td>${esc(D.grupos[g])}</td>${Object.values(CL).map(o => `<td class="h" style="${heat(o[g], cmx)}">${Math.round(o[g])}%</td>`).join('')}</tr>`).join('') + '</tbody>';

/* 07 redes */
const PAPEL = {
  YouTube: ['The Lecture Hall and the Stage', 'Long-form video dedicated to thorough explanation and entertainment. IQ validity debates and logic puzzles command the largest aggregate viewership, and this platform hosts the highest comment density.'],
  TikTok: ['Where Giftedness Becomes Identity', 'The highest aggregate reach across the dataset. Psychologists and neurodiversity creators enumerate diagnostic checklists, prompting instant user recognition. Distribution is heavily skewed: a tiny percentile of profiles commands the majority of impressions.'],
  Instagram: ['Clinical Consulting Room and Showcase', 'Healthcare clinicians, advocacy institutes, and parents. Discussions center around childhood accommodation, schooling, and adult celebrity discovery memoirs.'],
  X: ['Real-Time Journalistic Discourse', 'News reporting URLs, political arguments, and immediate reactions. Displays substantially higher proportional discourse regarding Mensa and federal legislation than any video-centric network.'],
};
$('#cards-redes').innerHTML = D.redes.map(r => `<div class="card rede"><div class="rede-cab"><span class="fic" style="background:${COR_REDE[r.rede]};width:48px;height:48px;border-radius:14px">${ico(r.rede, 24, 'var(--bg)')}</span><h3>${r.rede}</h3></div><div class="q">${PAPEL[r.rede][0]}</div><p style="font-size:15px;color:var(--ink2);margin-bottom:12px">${PAPEL[r.rede][1]}</p><dl>
  <dt>Topical content items</dt><dd>${n(r.itens)}</dd><dt>Monitored profiles & channels</dt><dd>${n(r.autores)}</dd>
  <dt>Total reach (views)</dt><dd>${r.views_total ? c(r.views_total) : '–'}</dd>
  <dt>Total likes</dt><dd>${r.rede === 'X' ? 'sem métrica' : c(r.likes_total)}</dd>
  <dt>Total comments</dt><dd>${r.rede === 'X' ? n(N.x_respostas) + ' resp.' : c(r.comentarios_total)}</dd>
  <dt>Median likes per post</dt><dd>${r.rede === 'X' ? '–' : n(r.likes_mediana)}</dd>
  <dt>Top 5 profiles share of likes</dt><dd>${r.rede === 'X' ? '–' : p(r.concentracao_top5)}</dd></dl></div>`).join('');
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

/* vídeos: o iframe só entra quando a pessoa clica */
function embed(v) {
  if (v.rede === 'YouTube') return `https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0`;
  if (v.rede === 'TikTok') return `https://www.tiktok.com/embed/v2/${v.id}`;
  return `https://www.instagram.com/p/${v.id}/embed/`;
}
function cartaoVideo(v, comInfo = true) {
  const vert = v.rede !== 'YouTube';
  const big = v.views ? `${c(v.views)}<small>views</small>` : `${c(v.likes)}<small>curtidas</small>`;
  // capas guardadas junto do site (o claude.ai bloqueia imagens de outros sites); Instagram usa uma ilustração
  const capa = v.rede === 'Instagram' ? 'img/espetaculo.jpg' : `img/capas/${esc(v.id)}.jpg`;
  const thumb = ` thumb" style="background-image:url(${capa})`;
  return `<button class="tela${vert ? ' vert' : ''}${thumb}" data-src="${esc(embed(v))}" aria-label="Assistir: ${esc(v.titulo)}"><span class="rede-tag">${v.rede}</span><span class="play"></span><span class="big">${big}</span></button>` +
    (comInfo ? `<div class="info"><b>${esc(v.titulo)}</b><p>${esc(v.contexto)}</p><div class="met">${esc(v.autor)} · ${v.ano} · ${v.views ? c(v.views) + ' views · ' : ''}${c(v.likes)} likes · ${c(v.comentarios)} comments · <a class="abrir" href="${esc(v.url)}" target="_blank" rel="noopener">abrir ↗</a></div></div>` : '');
}
document.addEventListener('click', e => {
  const t = e.target.closest('.tela[data-src]');
  if (!t) return;
  t.innerHTML = `<iframe src="${t.dataset.src}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen loading="lazy" title="Vídeo"></iframe>`;
  t.removeAttribute('data-src');
});
$('#videos').innerHTML = D.videos_impacto.map(v => `<div class="vid">${cartaoVideo(v)}</div>`).join('');
$('#video-mensa').innerHTML = cartaoVideo(D.video_mensa);

/* temas no tempo */
const ST = D.serie_temas, SA = ST.semestres;
const temasSerie = Object.keys(D.rotulos_tema).filter(k => k !== 'outro');
let temaSel = 'saude_mental_neuro';
/* temas no tempo: doze pequenos gráficos, comments e reportagens */
(() => {
  const nome = {entretenimento_humor: 'Humor', validade_testes_qi: 'Validade do QI', experiencia_pessoal: 'Experiência pessoal', diagnostico_avaliacao: 'Diagnóstico', saude_mental_neuro: 'Saúde mental', elitismo_arrogancia: 'Elitismo', caracteristicas_sinais: 'Sinais', elogio_admiracao: 'Elogio', mensa_sociedade: 'A Mensa', educacao_escola: 'Escola', politica_publica: 'Política pública', custo_acesso: 'Custo e acesso'};
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toLocaleString('en-US', {maximumFractionDigits: 1});
  const cls = v => v >= 2 ? 'sobe' : v <= -2 ? 'desce' : 'igual';
  const L = temasSerie.map(k => {
    const cm = ST.comentarios[k].pct.map(v => v ?? 0), rp = ST.reportagens[k].pct.map(v => v ?? 0);
    return {k, cm, rp, dc: cm[5] - cm[0], dr: rp[5] - rp[0]};
  }).sort((a, b) => Math.abs(b.dc) + Math.abs(b.dr) - Math.abs(a.dc) - Math.abs(a.dr));
  $('#multiplos').innerHTML = L.map(({k, cm, rp, dc, dr}) => {
    const mx = Math.max(1, ...cm, ...rp), x = i => 6 + 228 * i / 5, y = v => (96 - 86 * v / mx).toFixed(1);
    const pts = a => a.map((v, i) => x(i) + ',' + y(v)).join(' ');
    return `<article class="mult"><div class="mult-cab"><span class="mic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_TEMA[k] || ''}"/></svg></span><h4>${esc(nome[k] || D.rotulos_tema[k])}</h4><span>até ${Math.round(mx)}%</span></div>
      <svg viewBox="0 0 240 104" role="img" aria-label="${esc(D.rotulos_tema[k])}: comments de ${p(cm[0])} para ${p(cm[5])}, reportagens de ${p(rp[0])} para ${p(rp[5])}">
        <line x1="6" y1="96" x2="234" y2="96" stroke="var(--line)"/>
        <polyline points="${pts(rp)}" fill="none" stroke="var(--spark)" stroke-width="2.5" stroke-linejoin="round"/>
        <polyline points="${pts(cm)}" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linejoin="round"/>
        <circle cx="${x(5)}" cy="${y(cm[5])}" r="4" fill="var(--accent)"/><circle cx="${x(5)}" cy="${y(rp[5])}" r="4" fill="var(--spark)"/>
      </svg>
      <div class="mult-anos"><span>2021</span><span>2026</span></div>
      <div class="mult-d"><div><b class="${cls(dc)}">${fmt(dc)}</b><span>comments, p.p.</span></div><div><b class="${cls(dr)}">${fmt(dr)}</b><span>reportagens, p.p.</span></div></div>
    </article>`;
  }).join('');
  const seta = {cima: 'M12 19V5 M5 12l7-7 7 7', baixo: 'M12 5v14 M5 12l7 7 7-7'};
  const ch = (k, campo, txt) => {
    const it = L.find(x => x.k === k), v = it[campo];
    return `<div class="chip-t"><span class="pic" style="background:${v >= 0 ? 'var(--spark)' : 'var(--neg)'}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${v >= 0 ? seta.cima : seta.baixo}"/></svg></span><div><b class="${cls(v)}">${fmt(v)} p.p.</b><span>${txt}</span></div></div>`;
  };
  $('#temas-chips').innerHTML = ch('entretenimento_humor', 'dc', 'de piada sobre QI nos comments') + ch('politica_publica', 'dr', 'de política pública nas reportagens') + ch('mensa_sociedade', 'dr', 'de Mensa como tema principal das reportagens');
})();
const seta = d => d > 0.5 ? `<span class="seta-up">▲ ${d.toLocaleString('en-US', {maximumFractionDigits: 1})}</span>` : d < -0.5 ? `<span class="seta-dn">▼ ${Math.abs(d).toLocaleString('en-US', {maximumFractionDigits: 1})}</span>` : '<span style="color:var(--muted)">=</span>';
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
  $('#duv-lead').innerHTML = `Em <span>${p(100 * DV.com_duvida / DV.amostra)}</span> dos comments que perguntam ou desabafam há uma dúvida ou angústia real. As mais comuns: <span>${esc(t1.titulo)}</span> (${p(t1.pct)}) e <span>${esc(t2.titulo)}</span> (${p(t2.pct)}).`;
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
$('#duv').innerHTML = C.map(x => `<div class="card"><div class="duv-cab"><span class="pic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONE_DUV[x.chave] || ''}"/></svg></span><div class="pct">${p(x.pct)}</div></div><h3>${esc(x.titulo)}</h3><p class="desc">${esc(x.desc)} · ${n(x.n)} comments · ${n(x.likes)} aggregate likes</p>
    ${x.exemplos.map(e => `<blockquote>"${esc(e.texto)}"<small>${n(e.likes)} likes · ${e.fonte}${fonteLink(e)}</small></blockquote>`).join('')}<div class="fundo" style="width:${x.pct * 2.5}%"></div></div>`).join('');
  $('#duv-nota').textContent = `Amostra de ${n(DV.amostra)} comments classificados pela nossa IA (${Object.entries(DV.amostra_fonte).map(([f, q]) => n(q) + ' do ' + f).join(', ')}); ${n(DV.com_duvida)} expressam dúvida ou angústia. Percentuais sobre esses ${n(DV.com_duvida)}. Comentários sem autor; trechos com números, links ou marcações foram excluídos.`;
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
