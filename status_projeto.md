# Status do projeto: Mensa, altas habilidades e superdotação no Brasil

Data do relatório: 26/10/2026. Este documento diz o que está pronto, o que está desatualizado e o que falta para concluir.

## 1. Onde estamos

O projeto está na fase de classificação e validação. A coleta está encerrada, e as análises anteriores precisam ser refeitas em parte porque a postura sobre a Mensa foi corrigida.

## 2. O que está pronto

**Coleta** (servidor 76.13.226.191, pasta `~/mensa-ah-sd/`)
- Comentários do YouTube: 80.809 comentários de 262 vídeos com comentários disponíveis. Autores anonimizados (hash com sal guardado só no servidor).
- Métricas de 353 vídeos: visualizações, curtidas, comentários, data, duração, canal (coletadas pela máquina do usuário).
- Reportagens: 1.196 manchetes do Google Notícias e 1.043 textos completos.
- Revistas: 20 títulos, 953 links, 895 textos lidos, 210 com o tema pelo filtro de palavras.
- Projetos de lei: 10 na Câmara e 6 no Senado com o tema.

**Classificação com o JEV** (`typesafe/jev-1.13`, pela OpenRouter)
- **Tema de todos os 80.809 comentários**: 65.265 classificados pelo JEV e 15.544 pela regra "texto sem palavras", que vai para "outro". Nenhum falhou.
- **Tema das reportagens** (1.264) e dos vídeos (353), na mesma taxonomia de 12 temas.
- **Postura sobre a Mensa**, agora só para itens que citam a Mensa (regra simples por palavra). Não há mais a categoria "não se aplica" nem postura para comentários que tratam só de QI.
  - Comentários: 1.461, sendo 894 detratores, 291 neutros e 276 apoiadores.
  - Vídeos: 143, sendo 86 neutros, 50 apoiadores e 7 detratores.
  - Reportagens: 408, sendo 341 neutras, 66 apoiadoras e 1 detratora.

**Análises**
- Codebook com a definição de cada tema, gerada a partir de amostras (`codebook_comentarios.md`). Foi escrito sobre a taxonomia anterior, com 8.543 comentários.
- Análise temporal por mês e tema, em CSV.
- Lacunas entre demanda e oferta por tema.
- Correlações entre temas, em trimestres.

**Amostra para validação**
- `validacao/amostra_rotulagem.csv`, com 275 itens. Você preenche as colunas humanas.

## 3. O que está desatualizado

Estes documentos usam a postura antiga, que incluía "não se aplica" e rótulos para comentários que não citam a Mensa. Os números de postura por ano e por fonte precisam ser recalculados:

- `panorama_youtube_midia_superdotacao.md`: tabela de postura por ano, percentuais de detratores e a seção sobre reportagens.
- `relacoes_publicas_mensa_protagonista.md`: os argumentos sobre o descompasso entre mídia e público se apoiam nesses percentuais.
- `validacao/amostra_rotulagem.csv`: a coluna de postura do JEV é a antiga. Precisa ser regerada antes da revisão.

A análise de lacunas e as correlações usaram os 8.543 comentários com tema. Com os 80.809, a distribuição muda, e precisa ser refeita.

## 4. O que falta para concluir

Em ordem:

1. **Nuvem de bigramas com filtros**. Feito em 26/10: o script rodou (80.809 comentários, 217 mil bigramas únicos, top 1.500). Saídas em `dados/bigramas_comentarios.json` e `.csv`, e a página `dados/nuvem_bigramas.html` com filtros por tema, postura, ano e idioma. Ao rodar, corrigi um bug no `bigramas.py` (o contador `por` era `defaultdict(Counter)` e quebrava no `+= 1`). A correção está só na cópia local; o script no servidor ainda tem o bug.
2. **Decisão sobre termos do tema na nuvem**. Termos como "qi", "superdotado" e "altas habilidades" aparecem em quase todos os bigramas. Hoje eles ficam na nuvem, porque removê-los apaga o conteúdo ("QI alto", "altas habilidades" e "superdotado mensa"). Confirme se prefere mantê-los ou removê-los.
3. **Regerar a amostra de validação** (feito em 26/10). `validacao/amostra_rotulagem.csv` tem 275 itens: 195 comentários (15 por tema, de 13 temas, sem a regra "texto sem palavras"), 40 vídeos e 40 reportagens. Postura agora vem da v3. A versão anterior ficou em `validacao/amostra_rotulagem_pre_v3.csv`. Atenção: 247 dos 275 itens têm postura "nao_cita_mensa", então a revisão de postura cobre pouco. Vale decidir se a amostra deve ter mais itens que citam a Mensa.
4. **Revisão humana da amostra**. Você preenche as colunas de tema e postura. Depois calculo concordância (percentual e kappa) por tema e postura. Sem essa etapa, a precisão dos rótulos continua desconhecida.
5. **Atualizar os documentos da seção 3** com os números corrigidos. Se a concordância mostrar erro sistemático, corrijo os rótulos antes de recalcular.
6. **Decidir se o codebook deve ser refeito** sobre os 80.809 comentários, e não só sobre os 8.543.

**Temas múltiplos (26/10)**. A API do JEV só aceita perguntas de escolha única (`choice`). Para permitir vários temas por item, usei as probabilidades que o JEV já devolveu: entram todos os temas com probabilidade ≥ 0,2, além do principal. Saídas: `dados/temas_multi_comentarios.csv` (80.809 linhas) e `dados/temas_multi_videos.csv` (353). Em média há 1,43 tema por comentário e 1,40 por vídeo. Ainda não foram validados por humanos. O limiar 0,2 é uma escolha minha, e o JEV tende a puxar "entretenimento_humor" (44% dos comentários, contra 34% como tema principal).

## 5. Riscos e pontos de atenção

- **Chave da OpenRouter**: está no servidor com permissão 600. A cópia do `.env` que está nesta pasta do Drive pode ser apagada depois do uso.
- **Dicionário de pseudônimos** (`restrito/dicionario_hash_nome.json`): tem cerca de 60 mil autores. Não deve ser publicado.
- **Textos de reportagens** (`restrito/`): são de veículos. Uso só para pesquisa.
- **Validade dos rótulos**: o JEV não foi validado contra rótulos humanos. Os percentuais são de distribuição, não de acerto, até a etapa 4.
- **Correlações**: com 13 trimestres, são indícios, não achados.
- **Instagram, TikTok e X** continuam fora do escopo.

## 6. Próxima ação sugerida

Concluir a nuvem (item 1) e regerar a amostra (item 3), para que a revisão humana possa começar. Enquanto isso, eu atualizo os documentos da seção 3.
