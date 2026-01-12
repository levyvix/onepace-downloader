# One Pace Downloader

Sistema automatizado para download de episódios e legendas do One Pace com correspondência inteligente.

## 🎯 O que faz?

1. Baixa episódios do nyaa.si via torrent
2. Baixa legendas do Google Drive
3. Renomeia automaticamente as legendas para corresponder aos nomes dos vídeos
4. Verifica se tudo foi correspondido corretamente

Quando os nomes dos arquivos correspondem, players de vídeo carregam as legendas automaticamente!

## ⚡ Início Rápido - Pipeline com Um Comando

**Forma mais fácil:** Execute todo o workflow com um único comando!

```bash
uv run onepace_pipeline.py "<URL_NYAA>" "<URL_GDRIVE>" "<NOME_PASTA>"
```

### Exemplos

```bash
# Com prefixo "arc" (usado exatamente como fornecido)
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Sem prefixo "arc" (adiciona "arc-" automaticamente)
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+skypiea" \
  "https://drive.google.com/drive/folders/1ABC..." \
  "skypiea"
# Cria: arc-skypiea/
```

### O que você precisa fornecer

1. **URL do Nyaa.si** - Resultados de busca ou página de torrent único
2. **URL do Google Drive** - Link da pasta de legendas
3. **Nome da pasta** - Nome exato da pasta que você quer usar (ex: "arc15-jaya", "skypiea", "water7")
   - Se o nome começa com "arc", usa exatamente como fornecido
   - Caso contrário, adiciona prefixo "arc-" automaticamente (ex: "jaya" → "arc-jaya")

### 📥 Onde encontrar os links?

Acesse [One Pace PT-BR](https://onepaceptbr.github.io/) para encontrar:
- Links de torrent (nyaa.si) para cada arco
- Links do Google Drive com as legendas em português
- Informações sobre quais arcos estão disponíveis

### O que faz automaticamente

1. ✓ Inicia o download de todos os episódios do nyaa.si
2. ✓ Baixa todas as legendas do Google Drive
3. ✓ Aguarda a conclusão dos downloads dos episódios (monitora progresso do transmission)
4. ✓ Corresponde legendas aos nomes dos arquivos de vídeo
5. ✓ Verifica se tudo foi correspondido corretamente

### Recursos

- **Idempotente** - Seguro executar novamente após falhas, pula etapas concluídas
- **Downloads paralelos** - Baixa episódios e legendas ao mesmo tempo (economiza tempo!)
- **Detecção inteligente** - Aguarda até que os tamanhos dos arquivos estejam estáveis
- **Funciona com seeding** - Não espera o transmission-cli sair
- **Progresso em tempo real** - Mostra o progresso de cada etapa
- **Ctrl+C durante a espera** - Pula a espera e continua manualmente depois

## 📋 Pré-requisitos

```bash
# Arch Linux
sudo pacman -S transmission-cli python uv

# Debian/Ubuntu
sudo apt install transmission-cli python3
pip install uv

# macOS
brew install transmission-cli uv
```

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/levyvix/onepace-downloader.git
cd onepace-downloader
```

Não precisa instalar dependências Python! O `uv` gerencia tudo automaticamente.

## 🎬 Exemplo Completo: Baixar Arco Jaya

```bash
cd onepace-downloader

# Um único comando - workflow completo
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"
```

**Saída:**
```
======================================================================
STEP 1: Downloading episodes from nyaa.si
✓ Created: arc15-jaya/
✓ Starting downloads...

STEP 2: Downloading subtitles from Google Drive
✓ Downloaded 25 subtitle files

======================================================================
⏳ Waiting for episode downloads to complete...
======================================================================
Monitoring file sizes until stable...
(Press Ctrl+C to skip waiting and continue anyway)

⏳ Downloading: 25 file(s) found, sizes still changing...
⏳ Files stable (1/3)... 25 file(s) downloaded
⏳ Files stable (2/3)... 25 file(s) downloaded
⏳ Files stable (3/3)... 25 file(s) downloaded
✓ All downloads complete! Found 25 episode(s)

STEP 3: Matching subtitles to video filenames
✓ Matched and renamed 25 subtitle files

STEP 4: Verifying all videos have matching subtitles
Result: 25/25 videos have matching subtitles
======================================================================
✓ PIPELINE COMPLETED SUCCESSFULLY!
🎉 Ready to watch! Your video player will automatically load the subtitles.
```

## 🔧 Workflow Manual (4 Etapas)

Se preferir executar cada etapa manualmente:

```bash
# Etapa 1: Baixar episódios
uv run magnet_downloader.py "<URL_NYAA>" "<NOME_PASTA>"

# Etapa 2: Baixar legendas (enquanto os vídeos baixam)
uv run download_subtitles.py "<URL_GDRIVE>" "<NOME_PASTA>"

# Etapa 3: Corresponder legendas aos vídeos
uv run match_onepace_subtitles.py "<NOME_PASTA>" "<NOME_PASTA>"

# Etapa 4: Verificar se tudo correspondeu
uv run verify_subtitles.py "<NOME_PASTA>"
```

## 🔄 Executar Novamente Após Falhas

O pipeline é **idempotente** - seguro executar várias vezes!

```bash
# Primeira execução - falha durante etapa 2
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ✓ Episódios baixando
# STEP 2: ✗ Erro de rede!

# Segunda execução - retoma de onde parou
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ⏭️ Pulando - 25 arquivos .mkv já existem
# STEP 2: ✓ Baixa legendas com sucesso
# STEP 3: ✓ Corresponde legendas
# STEP 4: ✓ Verifica
```

## 🗂️ Estrutura de Pastas

**Antes:**
```
arc15-jaya/
├── [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
├── [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
├── Jaya 01.ass
└── Jaya 02.ass
```

**Depois (correspondido):**
```
arc15-jaya/
├── [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
├── [One Pace][218-220] Jaya 01 [1080p][HASH].ass  ← Correspondido!
├── [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
└── [One Pace][221-224] Jaya 02 [1080p][HASH].ass  ← Correspondido!
```

## 🛠️ Scripts Disponíveis

### `onepace_pipeline.py` ⭐ (main.py)
Pipeline completo - executa todas as 4 etapas automaticamente.

### `magnet_downloader.py`
Extrai links magnet do nyaa.si e baixa via transmission-cli.

### `download_subtitles.py`
Baixa arquivos de legendas de uma pasta do Google Drive.

### `match_onepace_subtitles.py`
Renomeia legendas para corresponder exatamente aos nomes dos vídeos.

### `verify_subtitles.py`
Verifica se cada arquivo de vídeo tem uma legenda correspondente.

## ❓ Troubleshooting

### Quer pular a espera pelos downloads?
- **Durante a espera:** Pressione `Ctrl+C` para pular e continuar depois
- **Correspondência manual depois:** Execute `uv run match_onepace_subtitles.py "<pasta>" "<pasta>"` após os downloads terminarem

### Pipeline diz "files stable" mas downloads ainda ativos?
- **Isso é normal!** O pipeline detecta quando os downloads estão **completos** (tamanhos estáveis)
- transmission-cli continua em background para **seeding** - isso é esperado
- Você pode parar o seeding depois: `killall transmission-cli`

### Downloads não estão iniciando?
- **Verifique:** `ps aux | grep transmission-cli` para ver downloads ativos
- **Verifique arquivos:** `ls -lh <pasta>/` para ver o que foi baixado
- **Correção:** Certifique-se que transmission-cli está instalado

### Nenhum arquivo de legenda baixado?
- **Verifique:** Link do Google Drive está acessível no navegador
- **Correção:** Verifique se a pasta está compartilhada "Qualquer pessoa com o link"

## 📄 Licença

MIT

## 🙏 Créditos

- [One Pace](https://onepace.net/) - Projeto de edição de One Piece
- [One Pace PT-BR](https://onepaceptbr.github.io/) - Fonte dos downloads e legendas em português
- Comunidade One Pace Brasil

## ⚠️ Aviso

Este projeto é apenas para uso educacional. Respeite os direitos autorais e use apenas com conteúdo que você tem permissão para baixar.
