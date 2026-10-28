(() => {
const D = window.DADOS, MP = D.mapa;
// elementos que esta seção não tem (fichas, tema) viram um nó solto e são ignorados
const $ = s => document.querySelector(s) || document.createElement('div');
const nf = new Intl.NumberFormat('en-US');
const n = x => x == null ? '–' : nf.format(Math.round(x));
const c = x => x == null ? '–' : x >= 1e6 ? (x / 1e6).toLocaleString('en-US', {maximumFractionDigits: 1}) + 'M' : x >= 1e4 ? Math.round(x / 1e3) + 'K' : n(x);
const esc = s => String(s ?? '').replace(/[&<>"]/g, m => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[m]));
const NOME = {views: 'reach', likes: 'likes', coments: 'comments'};
let M = 'likes';
try { M = localStorage.getItem('medida-mapa') || 'likes'; } catch (e) {}
const raiz = document.documentElement;
try { const t = localStorage.getItem('tema'); if (t) raiz.dataset.theme = t; } catch (e) {}
const cor = v => getComputedStyle(raiz).getPropertyValue(v).trim();
const CL = [...new Set(MP.pessoas.map(p => p.cluster))];
// paleta original do site: só verdes, limão e menta (laranja fica para valores negativos)
const PALETA = ['#34d399', '#c4f25a', '#2dd4bf', '#86efac', '#a3e635', '#5eead4', '#d9f99d'];
const corCl = nome => PALETA[Math.max(0, CL.indexOf(nome)) % PALETA.length];

const PESSOA = Object.fromEntries(MP.pessoas.map(p => [p.id, p]));
const G = MP.grupos;

/* foto: arquivo local, depois foto pública da rede, depois iniciais */
function avatar(id, nome, cls = '') {
  const ini = esc(String(nome).replace(/^@|^Dra?\.\s*/i, '').split(/[\s._]+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join(''));
  const src = (D.foto_de || {})[id];
  return src ? `<span class="av ${cls}"><img src="${src}" alt="" loading="lazy" onerror="this.parentNode.textContent='${ini}'"></span>` : `<span class="av ${cls}">${ini}</span>`;
}
function metricas(o) {
  return `<div class="met">${['views', 'likes', 'coments'].map(k => `<div class="${k === M ? 'on' : ''}"><b>${k === 'views' && !o.views && o.seguidores ? c(o.seguidores) : c(o[k])}</b><span>${k === 'views' ? (!o.views && o.seguidores ? 'followers' : 'views') : k === 'likes' ? 'likes' : 'comments'}</span></div>`).join('')}</div>`;
}
function postHtml(p, quem) {
  if (!p) return '';
  return `<div class="post"><a href="${esc(p.url)}" target="_blank" rel="noopener">"${esc(p.texto)}"</a><small>${quem ? 'Published by ' + esc(quem) + ' · ' : ''}${p.rede || ''} ${p.ano || ''} · ${p.views ? c(p.views) + ' views · ' : ''}${c(p.likes)} likes · ${c(p.coments)} comments</small></div>`;
}
function card(o, extra = '') {
  return `<article class="pcard${o.foco ? ' foco' : ''}"><div class="pcab">${avatar(o.id, o.nome)}<div><div class="pnome">${esc(o.nome)}</div><div class="ppapel">${esc(o.papel || '')}${o.n ? ' · ' + o.n + ' posts' : ''}</div></div></div>${metricas(o)}${extra}</article>`;
}

/* perfis em foco por rede */
let redeFoco = 'Instagram';
function foco() {
  $('#abas-foco').innerHTML = Object.keys(MP.foco_rede).map(r => `<button data-r="${r}" aria-pressed="${r === redeFoco}">${r}</button>`).join('');
  $('#cards-foco').innerHTML = MP.foco_rede[redeFoco].map(o => card(o, postHtml(o.post))).join('');
}
$('#abas-foco').onclick = e => { if (e.target.dataset.r) { redeFoco = e.target.dataset.r; foco(); } };
function orgs() { $('#cards-orgs').innerHTML = MP.orgs.map(o => card(o, `<div>${Object.entries(o.redes).map(([r, q]) => `<span class="chip">${r} ${q}</span>`).join('')}</div>` + postHtml(o.post))).join(''); }
function famosos() {
  $('#cards-famosos').innerHTML = MP.famosos.map(o => `<article class="pcard"><div class="pcab">${avatar(o.id, o.nome)}<div><div class="pnome">${esc(o.nome)}</div><div class="ppapel">${esc(o.papel)}</div></div></div>${metricas(o.post)}${postHtml(o.post, o.publicado_por)}</article>`).join('');
  $('#famosos-nota').textContent = `Also featured in mainstream press reports without dedicated topical social posts: ${MP.famosos_imprensa.join(', ')}.`;
  $('#refs').innerHTML = MP.sem_dados.map(r => `<div class="ref">${avatar(r.id, r.nome, 'g')}<div><div class="pnome">${esc(r.nome)}</div><div class="ppapel">${esc(r.papel)} · pioneering reference figure</div><p class="post" style="margin-top:6px">${esc(r.nota)}${r.citacao ? ` <a href="${esc(r.citacao.url)}" target="_blank" rel="noopener">Watch PodPeople episode</a> (${c(r.citacao.views)} views, ${c(r.citacao.likes)} curtidas, ${c(r.citacao.coments)} comments).` : ''}</p></div></div>`).join('');
}

/* por tema */
const TEMAS = Object.keys(MP.tema_top).filter(g => g !== 'outros');
let temaSel = 'neuro';
const CORES_TEMAS = {
  qi_teste: '#10b981',
  infancia: '#34d399',
  neuro: '#2dd4bf',
  genio: '#84cc16',
  diagnostico: '#06b6d4',
  adulto: '#14b8a6',
  escola: '#a3e635',
  politica: '#059669',
  mensa: '#22c55e',
  elitismo: '#65a30d',
  humor: '#4ade80',
  outros: '#64748b'
};
// cor fixa por tema; "sem tema específico" fica no cinza
const corTema = g => CORES_TEMAS[g] || PALETA[(Math.max(0, TEMAS.indexOf(g)) + 3) % PALETA.length];
function porTema() {
  $('#abas-tema').innerHTML = TEMAS.map(g => `<button data-g="${g}" aria-pressed="${g === temaSel}">${esc(G[g])}</button>`).join('');
  const L = [...MP.tema_top[temaSel]].sort((a, b) => b[M] - a[M]).slice(0, 8);
  $('#cards-tema').innerHTML = L.map(x => { const p = PESSOA[x.id]; return p ? card({...p, views: x.views, likes: x.likes, coments: x.coments, papel: p.rede + ' · ' + p.cluster, n: null}) : ''; }).join('');
}
$('#abas-tema').onclick = e => { if (e.target.dataset.g) { temaSel = e.target.dataset.g; porTema(); } };

/* dica flutuante */
const dica = $('#dica');
const mostra = (ev, html) => { dica.innerHTML = html; dica.hidden = false; dica.style.left = Math.min(innerWidth - 270, ev.clientX + 14) + 'px'; dica.style.top = (ev.clientY + 14) + 'px'; };
const esconde = () => { dica.hidden = true; };

/* grafo */
// no celular os gráficos ficam em pé e com menos nós, para o texto continuar legível
const movel = () => innerWidth < 640;
let sim;
function grafo() {
  const svg = d3.select('#g-grafo'); svg.selectAll('*').remove();
  const mv = movel(), W = mv ? 440 : 1100, H = mv ? 600 : 720, k = mv ? .6 : 1;
  svg.attr('viewBox', `0 0 ${W} ${H}`);
  let pessoas = [...MP.pessoas].sort((a, b) => (b.likes + b.coments + b.views / 20) - (a.likes + a.coments + a.views / 20)).slice(0, mv ? 24 : 40);
  const val = p => p[M] || (M === 'views' ? (p.seguidores || 0) / 5 : 0);
  const mx = d3.max(pessoas, val) || 1;
  const r = d3.scaleSqrt().domain([0, mx]).range(mv ? [6, 24] : [7, 34]);
  // só entra no grafo quem tem ligação com algum tema (sem ponto solto)
  const links = [];
  // conecta criadores aos temas com afinidade relevante
  pessoas.forEach(p => Object.entries(p.temas).forEach(([g, s]) => { if (g !== 'outros' && s >= .15) links.push({source: p.id, target: 't:' + g, w: s}); }));
  // Garante que nenhum tema fique solto/órfão: conecta aos perfis com maior presença no tema
  TEMAS.forEach(g => {
    if (!links.some(l => l.target === 't:' + g)) {
      const afins = pessoas.map(p => ({id: p.id, w: p.temas[g] || 0})).filter(x => x.w > 0).sort((a, b) => b.w - a.w);
      if (afins.length) {
        afins.slice(0, 2).forEach(af => links.push({source: af.id, target: 't:' + g, w: Math.max(0.12, af.w)}));
      } else {
        const topC = (MP.tema_top[g] || [])[0];
        if (topC && (PESSOA[topC.id] || pessoas.some(p => p.id === topC.id))) {
          links.push({source: topC.id, target: 't:' + g, w: 0.15});
        }
      }
    }
  });
  const ligados = new Set(links.map(l => l.source));
  pessoas = pessoas.filter(p => ligados.has(p.id));
  const nodes = [
    ...TEMAS.map((g, i) => ({id: 't:' + g, tipo: 'tema', nome: G[g], x: W / 2 + (mv ? 140 : 260) * Math.cos(2 * Math.PI * i / TEMAS.length), y: H / 2 + 220 * Math.sin(2 * Math.PI * i / TEMAS.length)})),
    ...pessoas.map(p => ({id: p.id, tipo: 'p', p, raio: r(val(p))})),
  ];
  const defs = svg.append('defs');
  pessoas.forEach(p => {
    const id = 'av-' + p.id.replace(/[^a-z0-9]/gi, '');
    const pat = defs.append('pattern').attr('id', id).attr('width', 1).attr('height', 1).attr('patternContentUnits', 'objectBoundingBox');
    const loc = (D.foto_de || {})[p.id];
    // se a foto não carregar, o disco fica na cor do cluster (não some no fundo)
    pat.append('rect').attr('width', 1).attr('height', 1).attr('fill', corCl(p.cluster));
    if (loc) pat.append('image').attr('href', loc).attr('width', 1).attr('height', 1).attr('preserveAspectRatio', 'xMidYMid slice');
  });
  const lk = svg.append('g').attr('stroke', cor('--cinza')).selectAll('line').data(links).join('line').attr('stroke-width', d => 1 + 3 * d.w).attr('stroke-opacity', .7);
  const nd = svg.append('g').selectAll('g').data(nodes).join('g').style('cursor', 'grab');
  nd.filter(d => d.tipo === 'tema').append('circle').attr('r', 30).attr('fill', cor('--surface2')).attr('stroke', cor('--ink2')).attr('stroke-width', 1.5);
  nd.filter(d => d.tipo === 'tema').append('text').text(d => d.nome.split(' ')[0].replace(/,$/, '')).attr('text-anchor', 'middle').attr('dy', 4).attr('font-size', 12).attr('font-weight', 700).attr('fill', cor('--ink'));
  const pn = nd.filter(d => d.tipo === 'p');
  pn.append('circle').attr('r', d => d.raio).attr('fill', d => `url(#av-${d.id.replace(/[^a-z0-9]/gi, '')})`).attr('stroke', d => corCl(d.p.cluster)).attr('stroke-width', d => d.p.foco ? 5 : 3).attr('stroke-opacity', 1);
  // nó sem ligação: fica visível e com contorno, mesmo sem foto
  pn.filter(d => d.raio > 16 || d.p.foco).append('text').text(d => d.p.nome.replace(/^@/, '')).attr('text-anchor', 'middle').attr('dy', d => d.raio + 14).attr('font-size', 12).attr('font-weight', 600).attr('fill', cor('--ink')).attr('stroke', cor('--bg')).attr('stroke-width', 3).attr('paint-order', 'stroke');
  pn.on('mousemove', (ev, d) => mostra(ev, `<b>${esc(d.p.nome)}</b><br>${esc(d.p.cluster)}<br>${c(d.p.views)} views · ${c(d.p.likes)} likes · ${c(d.p.coments)} comments`)).on('mouseleave', esconde);
  if (sim) sim.stop();
  sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(d => k * (90 + 60 * (1 - d.w))).strength(d => .2 + .5 * d.w))
    .force('charge', d3.forceManyBody().strength(d => d.tipo === 'tema' ? -500 : -140))
    .force('colide', d3.forceCollide(d => (d.tipo === 'tema' ? 34 : d.raio) + 4))
    .force('x', d3.forceX(W / 2).strength(mv ? .05 : .09)).force('y', d3.forceY(H / 2).strength(mv ? .04 : .1)).force('centro', d3.forceCenter(W / 2, H / 2))
    .on('tick', () => {
      nodes.forEach(d => { const rr = d.tipo === 'tema' ? 32 : d.raio; d.x = Math.max(rr, Math.min(W - rr, d.x)); d.y = Math.max(rr, Math.min(H - rr - 14, d.y)); });
      lk.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nd.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  nd.call(d3.drag().on('start', (ev, d) => { if (!ev.active) sim.alphaTarget(.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; }).on('end', (ev, d) => { if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));
  $('#leg-cl').innerHTML = CL.map(nome => `<span style="--c:${corCl(nome)}">${esc(nome)}</span>`).join('');
}

/* treemap */
let temaTree = 'todos';

function atualizaFiltroTemaTree(totTema, totGeral) {
  const container = $('#filtro-tema-tree');
  if (!container) return;
  const temasOrdenados = [...TEMAS].sort((a, b) => (totTema[b] || 0) - (totTema[a] || 0));
  let html = `<button data-tema="todos" aria-pressed="${temaTree === 'todos'}">Todos os temas</button>`;
  temasOrdenados.forEach(g => {
    const val = totTema[g] || 0;
    if (val <= 0 && temaTree !== g) return;
    const pct = totGeral > 0 ? Math.round(100 * val / totGeral) : 0;
    html += `<button data-tema="${g}" aria-pressed="${temaTree === g}">${esc(G[g])}${pct > 0 ? ` <span style="opacity:.7;font-size:11px">(${pct}%)</span>` : ''}</button>`;
  });
  container.innerHTML = html;
}

$('#filtro-tema-tree').onclick = e => {
  const btn = e.target.closest('button');
  if (!btn || !btn.dataset.tema) return;
  const novoTema = btn.dataset.tema;
  temaTree = (temaTree === novoTema && novoTema !== 'todos') ? 'todos' : novoTema;
  treemap();
};

function treemap() {
  const svg = d3.select('#g-tree'); svg.selectAll('*').remove();
  const W = movel() ? 440 : 1100, H = movel() ? 720 : 560;
  svg.attr('viewBox', `0 0 ${W} ${H}`);
  const idx = {views: 'views', likes: 'likes', coments: 'coments'}[M];
  const totTema = {};
  MP.fluxos.forEach(f => { totTema[f.grupo] = (totTema[f.grupo] || 0) + (f[idx] || 0); });
  const totGeral = d3.sum(Object.values(totTema)) || 1;

  atualizaFiltroTemaTree(totTema, totGeral);
  const corT = g => CORES_TEMAS[g] || corTema(g);

  if (temaTree !== 'todos' && MP.tema_top[temaTree]) {
    // MODO ZOOM: detalhamento de um único tema
    const g = temaTree;
    const nomeTema = G[g] || g;
    const valTema = totTema[g] || 0;
    const pctGeral = Math.round(100 * valTema / totGeral);

    $('#h-tree').innerHTML = `${esc(nomeTema)}: <em>${c(valTema)} ${NOME[M] === 'alcance' ? 'views' : NOME[M]}</em> (${pctGeral}% da conversa total) <small style="display:block;font-size:13px;font-weight:400;margin-top:4px;color:var(--muted)">Mostrando os principais criadores deste assunto · Clique em "Todos os temas" para voltar</small>`;

    const tops = [...(MP.tema_top[g] || [])].sort((a, b) => b[idx] - a[idx]);
    const somaTops = d3.sum(tops, t => t[idx] || 0);
    const resto = Math.max(0, valTema - somaTops);

    const children = tops.filter(t => (t[idx] || 0) > 0).map(t => {
      const p = PESSOA[t.id] || {nome: t.id, id: t.id};
      return {
        name: p.nome,
        id: t.id,
        value: t[idx],
        g,
        totalTema: valTema,
        rede: p.rede || '',
        cluster: p.cluster || '',
        outros: false
      };
    });

    if (resto > 0) {
      children.push({
        name: 'Demais criadores e menções somadas',
        id: 'outros',
        value: resto,
        g,
        totalTema: valTema,
        rede: '',
        cluster: '',
        outros: true
      });
    }

    const root = d3.hierarchy({children}).sum(d => d.value || 0).sort((a, b) => b.value - a.value);
    d3.treemap().size([W, H]).paddingInner(4).paddingOuter(4).round(true)(root);

    const fol = svg.selectAll('g.f').data(root.leaves()).join('g').attr('class', 'f').style('cursor', 'pointer');

    fol.append('rect')
      .attr('x', d => d.x0).attr('y', d => d.y0)
      .attr('width', d => Math.max(0, d.x1 - d.x0)).attr('height', d => Math.max(0, d.y1 - d.y0))
      .attr('rx', 4).attr('ry', 4)
      .attr('fill', d => d.data.outros ? cor('--surface2') : corT(g))
      .attr('fill-opacity', d => d.data.outros ? 0.6 : 0.88)
      .attr('stroke', d => d.data.outros ? cor('--line') : cor('--surface'))
      .attr('stroke-width', 2)
      .on('mousemove', (ev, d) => {
        const pctTema = Math.round(100 * d.value / valTema);
        mostra(ev, `<b>${esc(d.data.name)}</b><br>${d.data.rede ? esc(d.data.rede) + ' · ' + esc(d.data.cluster) + '<br>' : ''}<b>${c(d.value)}</b> ${NOME[M] === 'alcance' ? 'views' : NOME[M]}<br><b>${pctTema}%</b> de ${esc(nomeTema)}`);
      })
      .on('mouseleave', esconde);

    fol.each(function(d) {
      const gEl = d3.select(this);
      const w = d.x1 - d.x0;
      const h = d.y1 - d.y0;
      if (w < 60 || h < 26) return;

      const pct = Math.round(100 * d.value / valTema);
      const isOutros = d.data.outros;
      const textColor = isOutros ? cor('--ink') : '#ffffff';
      const textShadow = isOutros ? 'none' : '0 1px 3px rgba(0,0,0,0.85)';

      if (h >= 64 && w >= 110) {
        gEl.append('text')
          .attr('x', d.x0 + 10).attr('y', d.y0 + 22)
          .attr('font-size', w > 190 ? 16 : 13).attr('font-weight', 800)
          .attr('fill', textColor).style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(d.data.name.replace(/^@/, ''));

        if (d.data.rede || d.data.cluster) {
          gEl.append('text')
            .attr('x', d.x0 + 10).attr('y', d.y0 + 38)
            .attr('font-size', 11).attr('font-weight', 500)
            .attr('fill', isOutros ? cor('--ink2') : 'rgba(255,255,255,0.8)').style('pointer-events', 'none')
            .text(`${d.data.rede ? d.data.rede + ' · ' : ''}${d.data.cluster}`);
        }

        gEl.append('text')
          .attr('x', d.x0 + 10).attr('y', d.y0 + Math.min(h - 10, 58))
          .attr('font-size', 13).attr('font-weight', 700)
          .attr('fill', isOutros ? cor('--accent') : '#fef08a').style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(`${c(d.value)} (${pct}%)`);
      } else if (h >= 40 && w >= 75) {
        gEl.append('text')
          .attr('x', d.x0 + 8).attr('y', d.y0 + 17)
          .attr('font-size', 12).attr('font-weight', 700)
          .attr('fill', textColor).style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(d.data.name.replace(/^@/, ''));

        gEl.append('text')
          .attr('x', d.x0 + 8).attr('y', d.y0 + 32)
          .attr('font-size', 11).attr('font-weight', 600)
          .attr('fill', isOutros ? cor('--accent') : '#fef08a').style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(`${c(d.value)} · ${pct}%`);
      } else {
        gEl.append('text')
          .attr('x', d.x0 + 6).attr('y', d.y0 + 17)
          .attr('font-size', 11).attr('font-weight', 600)
          .attr('fill', textColor).style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(d.data.name.replace(/^@/, ''));
      }
    });

  } else {
    // MODO GERAL: todos os temas
    const children = TEMAS.map(g => {
      const tops = [...(MP.tema_top[g] || [])].sort((a, b) => b[idx] - a[idx]).slice(0, 5);
      const soma = d3.sum(tops, t => t[idx] || 0);
      const totalDoTema = totTema[g] || 0;
      const kids = tops.filter(t => (t[idx] || 0) > 0).map(t => ({
        name: (PESSOA[t.id] || {nome: t.id}).nome,
        id: t.id,
        value: t[idx],
        g,
        totalTema: totalDoTema,
        outros: false
      }));
      const resto = totalDoTema - soma;
      if (resto > 0) {
        kids.push({name: 'outros', id: 'outros', value: resto, g, totalTema: totalDoTema, outros: true});
      }
      return {name: G[g] || g, g, valueTema: totalDoTema, children: kids};
    }).filter(t => t.children.length);

    const root = d3.hierarchy({children}).sum(d => d.value || 0).sort((a, b) => b.value - a.value);
    
    // paddingTop(32) DEPOIS de paddingOuter para garantir 32px de respiro no topo de cada tema
    d3.treemap()
      .size([W, H])
      .paddingOuter(4)
      .paddingInner(3)
      .paddingTop(d => d.depth === 1 ? 34 : 4)
      .round(true)(root);

    const tot = root.value || 1;
    const top = root.children[0];
    $('#h-tree').innerHTML = `${esc(top.data.name)} é o tema mais expressivo: <em>${Math.round(100 * top.value / tot)}%</em> da conversa <small style="display:block;font-size:13px;font-weight:400;margin-top:4px;color:var(--muted)">Clique no título de um tema para isolá-lo e ver detalhes de todos os criadores</small>`;

    const grp = svg.selectAll('g.t').data(root.children).join('g').attr('class', 't');

    grp.append('rect')
      .attr('x', d => d.x0).attr('y', d => d.y0)
      .attr('width', d => Math.max(0, d.x1 - d.x0)).attr('height', d => Math.max(0, d.y1 - d.y0))
      .attr('rx', 4).attr('ry', 4)
      .attr('fill', cor('--surface2'))
      .attr('stroke', cor('--line'))
      .attr('stroke-width', 1);

    grp.append('rect')
      .attr('x', d => d.x0).attr('y', d => d.y0)
      .attr('width', d => Math.max(0, d.x1 - d.x0)).attr('height', 30)
      .attr('rx', 4).attr('ry', 4)
      .attr('fill', d => corT(d.data.g))
      .attr('fill-opacity', 0.22)
      .style('cursor', 'pointer')
      .on('click', (ev, d) => { temaTree = d.data.g; treemap(); })
      .on('mousemove', (ev, d) => {
        mostra(ev, `<b>${esc(d.data.name)}</b><br>${c(d.value)} ${NOME[M] === 'alcance' ? 'views' : NOME[M]} (${Math.round(100 * d.value / tot)}% da conversa)<br><em>Clique para detalhar este tema</em>`);
      })
      .on('mouseleave', esconde);

    grp.append('text')
      .attr('x', d => d.x0 + 8).attr('y', d => d.y0 + 20)
      .text(d => {
        const w = d.x1 - d.x0;
        const pct = Math.round(100 * d.value / tot);
        // só escreve o que cabe na faixa (≈7px por letra em 13px)
        const cabe = t => t.length * 7.2 + 16 < w;
        const cheio = `${d.data.name} · ${pct}%`, curto = `${d.data.name.split(/[,·]/)[0]} · ${pct}%`;
        const palavra = `${d.data.name.split(/[ ,·]/)[0]} · ${pct}%`;
        return cabe(cheio) ? cheio : cabe(curto) ? curto : cabe(palavra) ? palavra : w > 40 ? `${pct}%` : '';
      })
      .attr('font-size', 13).attr('font-weight', 800)
      .attr('fill', cor('--ink'))
      .style('pointer-events', 'none');

    grp.filter(d => (d.x1 - d.x0) > d.data.name.length * 7.2 + 110).append('text')
      .attr('x', d => d.x1 - 8).attr('y', d => d.y0 + 20)
      .attr('text-anchor', 'end')
      .attr('font-size', 11).attr('font-weight', 600)
      .attr('fill', cor('--ink2')).style('opacity', 0.75)
      .text('detalhar →')
      .style('cursor', 'pointer')
      .on('click', (ev, d) => { temaTree = d.data.g; treemap(); });

    const fol = svg.selectAll('g.f').data(root.leaves()).join('g').attr('class', 'f').style('cursor', 'pointer');

    fol.append('rect')
      .attr('x', d => d.x0).attr('y', d => d.y0)
      .attr('width', d => Math.max(0, d.x1 - d.x0)).attr('height', d => Math.max(0, d.y1 - d.y0))
      .attr('rx', 3).attr('ry', 3)
      .attr('fill', d => d.data.outros ? cor('--surface') : corT(d.data.g))
      .attr('fill-opacity', d => d.data.outros ? 0.35 : 0.82)
      .attr('stroke', cor('--bg'))
      .attr('stroke-width', 1.5)
      .on('click', (ev, d) => { temaTree = d.data.g; treemap(); })
      .on('mousemove', (ev, d) => {
        const pctDoTema = d.data.totalTema ? Math.round(100 * d.value / d.data.totalTema) : 0;
        const pctTotal = Math.round(100 * d.value / tot);
        mostra(ev, `<b>${esc(d.data.name)}</b> em <i>${esc(G[d.data.g] || d.data.g)}</i><br><b>${c(d.value)}</b> ${NOME[M] === 'alcance' ? 'views' : NOME[M]}<br>${pctDoTema}% deste tema · ${pctTotal}% do total<br><em>Clique para detalhar o tema</em>`);
      })
      .on('mouseleave', esconde);

    fol.each(function(d) {
      const gEl = d3.select(this);
      const w = d.x1 - d.x0;
      const h = d.y1 - d.y0;
      if (w < 48 || h < 22) return;

      const isOutros = d.data.outros;
      const textColor = isOutros ? cor('--ink2') : '#ffffff';
      const textShadow = isOutros ? 'none' : '0 1px 2px rgba(0,0,0,0.9)';
      const maxChars = Math.max(3, Math.floor((w - 10) / 7.2));
      const nomeLimpo = d.data.name.replace(/^@/, '');
      const nomeExibido = nomeLimpo.length > maxChars ? nomeLimpo.slice(0, maxChars - 1) + '…' : nomeLimpo;

      if (h >= 44 && w >= 65) {
        gEl.append('text')
          .attr('x', d.x0 + 6).attr('y', d.y0 + 16)
          .attr('font-size', 11).attr('font-weight', 700)
          .attr('fill', textColor).style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(nomeExibido);

        gEl.append('text')
          .attr('x', d.x0 + 6).attr('y', d.y0 + 30)
          .attr('font-size', 10).attr('font-weight', 600)
          .attr('fill', isOutros ? cor('--ink2') : '#fef08a').style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(c(d.value));
      } else {
        gEl.append('text')
          .attr('x', d.x0 + 5).attr('y', d.y0 + Math.min(16, h - 6))
          .attr('font-size', 10).attr('font-weight', 600)
          .attr('fill', textColor).style('text-shadow', textShadow).style('pointer-events', 'none')
          .text(nomeExibido);
      }
    });
  }
}

/* sankey */
function sankey() {
  const svg = d3.select('#g-sankey'); svg.selectAll('*').remove();
  const W = 1100, H = 600;
  const nos = new Map(), lig = new Map();
  const no = (id, nome, nivel) => { if (!nos.has(id)) nos.set(id, {id, nome, nivel}); return id; };
  const add = (a, b, v) => { const k = a + '>' + b; lig.set(k, (lig.get(k) || 0) + v); };
  MP.fluxos.forEach(f => {
    if (f.grupo === 'outros' || !f[M]) return;
    const r = no('r:' + f.rede, f.rede, 0), t = no('t:' + f.grupo, G[f.grupo], 1), k = no('c:' + f.cluster, f.cluster, 2);
    add(r, t, f[M]); add(t, k, f[M]);
  });
  const graph = {nodes: [...nos.values()].map(d => ({...d})), links: [...lig].map(([k, v]) => { const [s, t] = k.split('>'); return {source: s, target: t, value: v}; })};
  const sk = d3.sankey().nodeId(d => d.id).nodeWidth(14).nodePadding(10).extent([[1, 6], [W - 1, H - 6]]);
  const {nodes, links} = sk(graph);
  const corNo = d => d.nivel === 0 ? cor('--ink2') : d.nivel === 1 ? corTema(d.id.slice(2)) : corCl(d.nome);
  svg.append('g').attr('fill', 'none').selectAll('path').data(links).join('path').attr('d', d3.sankeyLinkHorizontal())
    .attr('stroke', d => corNo(d.source.nivel === 0 ? d.target : d.source)).attr('stroke-opacity', .35).attr('stroke-width', d => Math.max(1, d.width))
    .on('mousemove', (ev, d) => mostra(ev, `${esc(d.source.nome)} → ${esc(d.target.nome)}<br>${c(d.value)} ${NOME[M] === 'alcance' ? 'views' : NOME[M]}`)).on('mouseleave', esconde);
  svg.append('g').selectAll('rect').data(nodes).join('rect').attr('x', d => d.x0).attr('y', d => d.y0).attr('width', d => d.x1 - d.x0).attr('height', d => Math.max(1, d.y1 - d.y0)).attr('fill', corNo);
  svg.append('g').selectAll('text').data(nodes).join('text')
    .attr('x', d => d.x0 < W / 2 ? d.x1 + 6 : d.x0 - 6).attr('y', d => (d.y0 + d.y1) / 2).attr('dy', '0.35em')
    .attr('text-anchor', d => d.x0 < W / 2 ? 'start' : 'end').attr('font-size', 13).attr('font-weight', 600).attr('fill', cor('--ink'))
    .text(d => (d.y1 - d.y0) > 9 ? `${d.nome} · ${c(d.value)}` : '');
}

/* sunburst */
function sunburst() {
  const svg = d3.select('#g-sun'); svg.selectAll('*').remove();
  const R = 290;
  const arv = d3.rollup(MP.fluxos.filter(f => f[M] > 0), v => d3.sum(v, f => f[M]), f => f.rede, f => f.cluster, f => f.grupo);
  const conv = (m, nome) => ({name: nome, children: [...m].map(([k, v]) => v instanceof Map ? conv(v, k) : {name: k, value: v})});
  const root = d3.hierarchy(conv(arv, 'total')).sum(d => d.value || 0).sort((a, b) => b.value - a.value);
  d3.partition().size([2 * Math.PI, R])(root);
  const arco = d3.arc().startAngle(d => d.x0).endAngle(d => d.x1).innerRadius(d => d.y0 * .98 + (d.depth === 1 ? 40 : 0)).outerRadius(d => d.y1 - 2).padAngle(.004);
  const corS = d => d.depth === 1 ? cor('--ink2') : d.depth === 2 ? corCl(d.data.name) : corTema(d.data.name);
  const tot = root.value;
  svg.append('g').selectAll('path').data(root.descendants().filter(d => d.depth)).join('path').attr('d', arco).attr('fill', corS)
    .attr('fill-opacity', d => d.depth === 3 ? .7 : .95)
    .on('mousemove', (ev, d) => {
      const cam = d.ancestors().reverse().slice(1).map(a => a.depth === 3 ? (G[a.data.name] || a.data.name) : a.data.name).join(' → ');
      mostra(ev, `<b>${esc(cam)}</b><br>${c(d.value)} · ${Math.round(100 * d.value / tot)}% do total`);
      $('#sun-det').innerHTML = `<b>${esc(cam)}</b><br>${c(d.value)} ${NOME[M] === 'alcance' ? 'views' : NOME[M]}, ${Math.round(100 * d.value / tot)}% do total`;
    }).on('mouseleave', esconde);
  svg.append('text').attr('text-anchor', 'middle').attr('dy', -4).attr('font-size', 26).attr('font-weight', 800).attr('fill', cor('--ink')).attr('font-family', 'Saira Condensed, sans-serif').text(c(tot));
  svg.append('text').attr('text-anchor', 'middle').attr('dy', 16).attr('font-size', 12).attr('fill', cor('--muted')).text(NOME[M] === 'alcance' ? 'views' : NOME[M]);
}

function tudo() {
  document.querySelectorAll('#medida button').forEach(b => b.setAttribute('aria-pressed', b.dataset.m === M));
  grafo(); treemap();
}
let eraMovel = movel();
addEventListener('resize', () => { if (movel() !== eraMovel) { eraMovel = movel(); tudo(); } });
$('#medida').onclick = e => { if (!e.target.dataset.m) return; M = e.target.dataset.m; try { localStorage.setItem('medida-mapa', M); } catch (er) {} tudo(); };
tudo();
})();
