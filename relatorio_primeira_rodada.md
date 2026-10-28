# Mensa, altas habilidades e superdotação no Brasil: primeira rodada (2020 a 26/10/2026)

Primeira rodada de coleta com fontes gratuitas. Todo o processo rodou no servidor 76.13.226.191 (`~/mensa-ah-sd/`). Os dados ficam em `dados/` e o dicionário de pseudônimos em `restrito/`.

## 1. O que foi coletado

| Fonte | Método | Resultado bruto | Resultado usado | Observação |
|---|---|---|---|---|
| Google Notícias (RSS) | Busca semanal por 4 combinações de termos, 2020 a 2026 | 5.415 linhas | 1.196 manchetes únicas | Só título e veículo. Sem texto da matéria. |
| YouTube (busca) | 15 buscas, até 100 resultados cada | 1.139 vídeos | 363 vídeos sobre o tema | Sem data de publicação nem comentários (ver seção 4). |
| Câmara dos Deputados (API aberta) | Busca por 4 palavras-chave, por trimestre | 14 proposições | 10 com o tema | [Fonte](https://dadosabertos.camara.leg.br) |
| Senado Federal (dados abertos) | Busca por 4 palavras-chave | 7 matérias | 6 com o tema | [Fonte](https://legis.senado.leg.br/dadosabertos) |
| Reddit (RSS público) | 9 buscas | 6 posts | 6 posts | O endpoint JSON bloqueia IPs de servidor. |

Os termos usados foram "altas habilidades", "superdotação", "superdotado" e "Mensa" combinada com QI, inteligência e elitista.

## 2. Mídia: volume por ano

| Ano | Manchetes únicas com o tema | Mencionam a Mensa | Com termo de elitismo |
|---|---|---|---|
| 2020 | 13 | 1 | 0 |
| 2021 | 53 | 4 | 0 |
| 2022 | 131 | 3 | 0 |
| 2023 | 139 | 3 | 0 |
| 2024 | 156 | 3 | 0 |
| 2025 | 293 | 15 | 0 |
| 2026 (até 26/10) | 411 | 19 | 0 |

Cautela sobre a série: o crescimento de 2020 a 2026 pode refletir o aumento do número de páginas indexadas pelo Google Notícias, e não só mais cobertura do tema. A série só serve para ver a forma geral. Não serve para comparar anos com precisão.

### O que as manchetes sobre a Mensa dizem

Das 48 manchetes que citam a Mensa, a grande maioria é de histórias sobre crianças muito novas que entram na sociedade (muitas com idade de 2 a 8 anos e QI citado). Quase todas são replicadas por sites com o mesmo texto, como Só Notícia Boa e CPG Click Petróleo e Gás. Também aparecem notícias de testes de QI em cidades brasileiras (2025 e 2026) e uma matéria explicativa do Estadão, de 04/12/2023, intitulada "O que é Mensa, sociedade para quem tem QI alto na qual a criança de 2 anos Isla McNabb foi admitida" ([link](https://news.google.com/rss/articles/CBMijwFBVV95cUxOb0xfa2lrVHpsXzhGSC1MOEc5TDc2QXo4RExqLTV5YXQyU19QT0F4eG1UN2I1U0Q2b2N3UmZpalZMU0NzaEZjc3laQ1k0YzY4c3VBYzBITEUyei1FcWR5NGczMWpUc1FuRlhzdWpRa1VpYTNCUi0yb2VGWHZnY0c4VWIyYjBoLWZ2UEtBZGNYNNIBlAFBVV95cUxQbkZad1NicndhOVhWUGkxbzlRaXFjWlAzR2hPRkN2Z2xXbE9JSkFRSjlTWHRMS0tESXBiSDhqS1BDaXlmMWY0Y1pra0ZpSThoQjliMnc0NThJVjZCNkFRbGtBTk9nRHdsekxhVUY2WlFDbXE3anBocU05VHlEeGN3YVVybjZmS1RmMGVxN3RqejNFWjlH?oc=5)). Os links de cada manchete estão em `dados/noticias_unicas_tema.csv`. Os links do Google Notícias são redirecionamentos e podem exigir abrir no navegador para chegar à matéria original.

Ressalva: a lista de 1.196 manchetes ainda tem alguns falsos positivos. Um exemplo é uma matéria da Volvo sobre um carro "superdotado", que entrou por causa da palavra. Eles não foram removidos nesta rodada.

Nenhuma das 48 manchetes sobre a Mensa usa o vocabulário de elitismo ("elitista", "elitismo", "esnobe", "arrogante", "soberbo", "pretensioso"). A tendência do noticiário é celebrar, não criticar.

Veículos com mais manchetes sobre o tema: G1 (110), Terra (47), Só Notícia Boa (37), CPG Click Petróleo e Gás (26), Crescer (24), Correio Braziliense (22), CNN Brasil (19), O Globo (17).

## 3. Projetos de lei e proposições oficiais

**Câmara dos Deputados**: a busca retornou 14 proposições. Dez tratam de altas habilidades ou superdotação de forma explícita. As outras quatro (PL 1648/2026, PL 4727/2026, PL 4953/2026 e PL 5016/2026) apareceram por ligação com educação inclusiva ou neurodiversidade.

Principais proposições sobre altas habilidades ou superdotação (AH/SD):
- PL 108/2020: institui a Política Nacional de Incentivo ao Desenvolvimento da Pessoa com AH/SD
- PL 1053/2022: institui o Dia Nacional das Pessoas com AH/SD
- PL 1459/2025: institui Centros Psicopedagógicos em Saúde Mental para crianças e adolescentes com AH/SD e transtornos do neurodesenvolvimento, no SUS
- PL 5237/2026: altera a Lei 8.080/1990 (SUS) para garantir acesso à avaliação psicológica, neuropsicológica ou multiprofissional a pessoas com indícios de AH/SD
- PL 1171/2026: altera a LDB para instituir programa nacional de incentivo ao desenvolvimento acadêmico de estudantes com AH/SD
- PL 1981/2026: cria Centros de Apoio Pedagógico Especializado para estudantes com deficiência, transtornos globais do desenvolvimento e AH/SD
- PL 2962/2026, PL 4105/2026 e PL 4130/2026: alterações na LDB sobre acolhimento, identificação e acompanhamento de estudantes com AH/SD, inclusive em áreas rurais
- PRC 48/2026: cria a Procuradoria das Pessoas com Deficiência, Pessoas com Doenças Raras e Pessoas com AH/SD na Câmara

**Senado Federal**: a busca retornou 7 itens. Os principais:
- PL 1049/2026: institui a Política Nacional para Estudantes com AH/SD e cria o Cadastro Nacional desses estudantes, alterando a Lei 11.578/2007
- VET 33/2026: veto parcial ao PL 1049/2026
- PL 1487/2026: institui a Lei de Inclusão de Superdotados e de produção de dados e estudos longitudinais sobre a superdotação
- PL 2083/2026: institui o Agosto Violeta, o Dia Nacional das Pessoas com AH/SD e a Semana Nacional de Conscientização
- REQ 33/2026 e REQ 4/2026: requerimentos de audiências públicas sobre o tema
- PDL 404/2026: susta a eficácia da Portaria MEC nº 421, de 15/05/2026, que trata da Política Nacional de Educação Especial Inclusiva. Esta é a única proposta desta lista que trata de uma norma do Executivo. O texto cita AH/SD apenas de forma indireta, pela política de educação inclusiva.

Links oficiais de cada item estão em `dados/proposicoes.json` e `dados/materias.json`.

Nenhuma dessas proposições menciona a Mensa. A busca por "Mensa" nas bases da Câmara e do Senado não trouxe nada além do que já aparece pelos outros termos.

## 4. Redes sociais e opinião pública

### YouTube
- 363 vídeos sobre o tema, após remover ruído. 127 têm "Mensa" no título.
- O ruído mais comum: "Mensa Otabil" (um pastor estrangeiro), "Vic Mensa" (rapper) e provas de QI da Mensa de outros países. Todos foram excluídos.
- Os vídeos com mais visualizações sobre a Mensa são de provas de QI em inglês e de testes da Mensa da Noruega e da Suécia, não brasileiros.
- Nenhum vídeo com termo de elitismo entre os vídeos do tema.

### Comentários: não consegui medir a opinião pública
O YouTube bloqueou a coleta de comentários a partir do servidor. Ele pede verificação "não sou robô" para cada vídeo. Sem os comentários, o elitismo percebido pelo público não pode ser medido com os dados desta rodada. As manchetes e os títulos dizem o que a imprensa e os canais publicam, não o que o público pensa.

Para medir isso, a saída é a YouTube Data API v3, que é gratuita, mas exige uma chave criada na sua conta do Google Cloud. Com ela, dá para baixar comentários de forma legítima e anonimizada.

### Reddit
Só 6 posts entraram, porque o RSS público retorna poucos resultados. Não há dado suficiente para conclusão.

## 5. Influenciadores no tema (Brasil)

Ranking pelo número de vídeos que aparecem nas buscas do YouTube sobre o tema. Não é ranking de audiência. Os números de visualização são dos vídeos encontrados, não do canal inteiro.

| Canal | Vídeos encontrados | Visualizações dos vídeos encontrados | Assunto principal (pelo nome do canal) |
|---|---|---|---|
| Mensa Brasil | 11 | 18.192 | Canal da sociedade Mensa (confirmar se é o oficial) |
| Dra. Olzeni Ribeiro | 9 | 31.984 | Psicologia (pelo nome do canal) |
| Jean Alessandro | 6 | 381.227 | Não classificado |
| Mais Que Autismo | 5 | 128.904 | Autismo |
| INODAP (Instituto para Otimização da Aprendizagem) | 5 | 39.312 | Aprendizagem |
| Lygia Pereira - Psicologia e Autismo Feminino | 4 | 58.891 | Psicologia e autismo |
| UniqueBrain | 3 | 198.778 | Não classificado |
| Sem Groselha Podcast | 3 | 189.296 | Podcast, não classificado |
| Dra. Paula Lemes - Cognitiva | 3 | 33.067 | Psicologia (pelo nome do canal) |
| Psicorporificar (Daphne Queiroz) | 3 | 20.170 | Psicologia (pelo nome do canal) |
| Mayra Gaiato | 2 | 290.204 | Desenvolvimento infantil e autismo |
| Carol Capel | 2 | 818.383 | Não classificado |
| Cauê Santos | 2 | 127.165 | Não classificado |
| Prof. Rafael Chanin | 2 | 35.101 | Não classificado (nome sugere educação) |
| Irmãos Dias Podcast | 2 | 212.906 | Podcast, não classificado |

Os nomes foram tirados do nome do canal, sem checagem de identidade. A coluna de assunto é uma classificação preliminar, feita só pelo nome do canal. Os canais marcados como "não classificado" precisam de revisão manual antes de qualquer conclusão sobre eles. A lista completa, com links, está em `dados/youtube_canais.csv`.

Padrão que aparece nos dados: a maior parte das vozes sobre altas habilidades no YouTube são de psicólogas, psicólogos e canais sobre autismo. A Mensa aparece principalmente pelo canal oficial e por vídeos estrangeiros.

Instagram, TikTok e X não entraram. Ficaram fora por decisão sua (fase de redes sociais "vemos depois") e porque nenhum tem coleta gratuita e estável a partir de servidor.

## 6. Anonimização

- Cada comentarista é identificado por um hash SHA-256 de 16 caracteres, com um sal aleatório guardado só no servidor.
- O dicionário hash → nome está em `restrito/dicionario_hash_nome.json` e deve ser tratado como dado pessoal.
- Nesta rodada, só 6 autores do Reddit entraram no dicionário, porque não houve comentários coletados.
- O sal não foi copiado para o Drive. Sem ele, o hash não pode ser recalculado a partir de um nome.
- Os nomes de influenciadores que aparecem no relatório são de canais públicos e não foram anonimizados.

## 7. Limitações desta rodada

1. Google Notícias traz só título e veículo. Não é possível ler o texto da matéria para medir o tom.
2. Sem comentários do YouTube, o elitismo percebido pelo público não foi medido.
3. Sem data de publicação dos vídeos do YouTube (a busca não traz a data), não há série temporal de vídeos.
4. Reddit retornou só 6 posts.
5. A série por ano mistura cobertura com crescimento da indexação.
6. Os números de visualização são de vídeos encontrados, não de canais.

## 8. Próximos passos sugeridos

1. Criar a chave da YouTube Data API (gratuita) para baixar comentários. Preciso que você crie e me passe a chave, que fica só no servidor.
2. Ler o texto das matérias mais relevantes (cerca de 200 links) para medir o tom em relação à Mensa.
3. Fase de redes sociais, quando você quiser, com as decisões de custo que ficaram para depois.

## Arquivos

- `dados/noticias_unicas_tema.csv`: 1.196 manchetes com data, veículo e link
- `dados/tema_todas_fontes.csv`: todas as fontes do tema em uma tabela
- `dados/youtube_canais.csv`: canais e vídeos encontrados
- `dados/proposicoes.json` e `dados/materias.json`: projetos de lei da Câmara e do Senado
- `dados/resultado_final.txt`: saída das consultas usadas neste relatório
- `restrito/dicionario_hash_nome.json`: dicionário de pseudônimos (acesso restrito)
