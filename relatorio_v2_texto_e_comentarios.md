# Mensa, altas habilidades e superdotação no Brasil: rodada 2 (texto completo e comentários)

Esta rodada substitui as limitações da rodada 1. Ela lê o texto integral das matérias e coleta os comentários do YouTube. O relatório da rodada 1 continua em `relatorio_primeira_rodada.md`.

## 1. O que mudou

- **Texto completo**: 1.043 de 1.196 matérias foram lidas na íntegra (87%). As demais estavam sem acesso (145, geralmente por bloqueio ou paywall) ou sem texto extraível (8). Os links do Google Notícias foram decodificados para o endereço original do veículo.
- **Comentários do YouTube**: coletados de 353 vídeos, com 11.801 comentários. Foram coletados a partir da sua máquina, porque o YouTube bloqueia comentários a partir do servidor. Os autores foram anonimizados no servidor e o arquivo bruto foi apagado da sua máquina.

## 2. Mensa nas matérias (texto completo)

- Das 1.043 matérias lidas, **354 mencionam a Mensa no corpo do texto**. Na rodada 1, só os títulos mostravam 48 menções. O título subestima a presença da Mensa nas matérias.
- Destas, a maioria é de notícia sobre crianças que entram na Mensa, com QI citado. Isso confirma o padrão da rodada 1.

## 3. Elitismo nas matérias

Medi o termo de elitismo de duas formas: uma busca ampla, que inclui "elite" e "privilegiado", e uma busca estrita, que usa só "elitista", "elitismo", "esnobe", "arrogante", "soberbo", "pretensioso", "prepotente", "pedante" e "clube/para ricos". A busca ampla pegava muito ruído, como "elite" em "elite mundial" e "superdotado" usado para jogador de futebol. Por isso uso a estrita.

- **Busca estrita**: 14 matérias de 1.043 usam algum dos termos. Só 3 mencionam a Mensa.
- **Lendo os 14 trechos**, a maioria não descreve a Mensa nem o movimento de superdotação como elitista. Eles são de três tipos:
  1. **Estigma sofrido por pessoas com altas habilidades**: a pessoa é vista como arrogante por saber demais ou por ter interesses diferentes. Aparece em G1 (2025-03-15), Revista Planeta (2025-02-26), O Globo (2024-12-16), Senado (2026-02-23), Correio Braziliense (2025-07-10), Tribuna Hoje (2025-04-10), Globo/Marie Claire (2023-09-24). É o caso mais frequente.
  2. **Argumento de política pública**: o termo "elitista" é usado para criticar seleção por talento ou acesso privado. Aparece em Congresso em Foco (2026-05-05 e 2026-09-01) e Assine Abril (2026-07-30).
  3. **Falsos positivos**: "despretensiosa", ou o termo usado para outro assunto.
- **Resultado**: nas matérias lidas, a crítica de elitismo à Mensa em si é praticamente ausente. O termo aparece mais como uma crítica à forma como a sociedade trata a pessoa com altas habilidades, e como uma crítica de política pública.

## 4. Elitismo nos comentários do YouTube

- Dos 11.801 comentários, **426 citam a Mensa**. Dos 2.280 que citam altas habilidades, superdotação, AH/SD, dupla excepcionalidade ou QI, **33 usam termo de arrogância** (1,4%).
- Com a busca estrita, **7 comentários** juntam Mensa e termo de elitismo. Os vídeos onde eles aparecem são críticos à Mensa: "Mi HORRIBLE EXPERIENCIA en MENSA" (54 comentários sobre a Mensa), "CORTES WINECAST - UM POUCO SOBRE A MENSA" e "Ho fatto il TEST DEL QI" (vídeo em italiano).
- Os comentários com mais curtidas que criticam a Mensa dizem coisas como "ambiente de elitismo agressivo", "gente chata e muito arrogante na Mensa" e "lucha de egos, narcisistas, elitistas". Os comentários de quem fez o teste são mistos: alguns relatam experiência positiva, outros relatam frustração e clima de competição.
- Os comentários com mais curtidas sobre altas habilidades são de pessoas que se identificam com o tema, relatando sofrimento, diagnóstico tardio e a sensação de serem vistas como arrogantes. Esse é o mesmo padrão encontrado nas matérias.

**Leitura geral**: em matérias e comentários, a palavra "arrogante" aparece muito mais como algo que as pessoas com altas habilidades dizem sofrer do que como uma crítica pública à Mensa. A crítica de elitismo à Mensa existe, mas é concentrada em poucos vídeos e comentários críticos, não no debate público amplo.

Estas leituras foram feitas por mim sobre amostras e trechos. Ainda não há codificação dupla nem medida de concordância. Para um número mais confiável, é preciso codificar uma amostra com critério fixo.

## 5. Limitações desta rodada

1. A busca de termos é grosseira. Ela detecta a palavra, não a intenção. Por isso a leitura dos trechos foi feita à mão.
2. Os comentários são só dos 353 vídeos encontrados na busca, que é enviesada para vídeos populares e de psicologia. Não representa o público todo.
3. A coleta pegou no máximo 150 comentários por vídeo (limite definido por mim na coleta). Em vídeos com mais comentários, a amostra foi a que o YouTube devolveu primeiro, geralmente as mais relevantes. Por isso o total de comentários é menor do que o real.
4. Não há medida de tom por IA, então o sentimento não foi quantificado.
5. Instagram, TikTok e X continuam de fora, como definido.

## 6. Arquivos

- `dados/artigos_completos.csv`: 1.043 matérias com contagem de menções e trechos de elitismo
- `restrito/artigos_texto_completo.json`: texto integral de cada matéria, com o link original. Os textos são de veículos e devem ser usados só para pesquisa.
- `dados/comentarios_youtube_tema.csv`: 11.801 comentários com autor anonimizado, link do vídeo, curtidas e indicadores
- `dados/analise_textos_saida.txt`: saída completa da análise
- `restrito/dicionario_hash_nome.json`: dicionário de pseudônimos, com cerca de 11 mil autores
