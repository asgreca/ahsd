#!/bin/bash
# Pipeline completo de coleta e análise do Instagram para Mensa / AH/SD
# Execução no Mac mini via Safari logado e Whisper local.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || exit 1

echo "=============================================="
echo "1. Descoberta de tags, buscas e perfis"
echo "=============================================="
python3 descobrir.py

echo "=============================================="
echo "2. Visita e categorização de perfis (médicos, psicólogos, etc.)"
echo "=============================================="
python3 perfis.py

echo "=============================================="
echo "3. Coleta de postagens, curtidas e comentários"
echo "=============================================="
python3 coletar_posts.py

echo "=============================================="
echo "4. Transcrição de áudio/vídeo via Whisper"
echo "=============================================="
python3 transcrever.py

echo "=============================================="
echo "5. Consolidação e geração do relatório"
echo "=============================================="
python3 analise_instagram.py

echo "Pipeline concluído com sucesso!"
