# One Pace Downloader

Pipeline automatizado para baixar episódios e legendas do One Pace. Baixe, organize e assista com uma experiência interativa no terminal.

## Início Rápido — Experiência Interativa ⭐

A forma mais fácil e recomendada:

```bash
uv run browse.py
```

Isso abre um menu interativo onde você:
1. Seleciona a saga (East Blue, Alabasta, etc)
2. Seleciona o arco desejado
3. Vê confirmação dos links
4. O pipeline executa automaticamente

O script scrapo automaticamente https://onepaceptbr.github.io/, oferece seleção com fzf e gerencia todo o download—episódios, legendas, organização e verificação.

### Alternativa: Linha de Comando (Manual)

Se preferir especificar as URLs diretamente:

```bash
uv run main.py "<URL_NYAA>" "<URL_GDRIVE>" "<NOME_PASTA>"
```

**Exemplo:**
```bash
uv run main.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"
```

## Recursos

- **Pipeline em um comando** - Baixa episódios, legendas e organiza automaticamente
- **Downloads paralelos** - Episódios e legendas baixam simultaneamente
- **Espera inteligente** - Detecta quando os downloads terminaram monitorando tamanho de arquivos
- **Auto-organização** - Move vídeos de subpastas para a pasta principal
- **Idempotente** - Seguro executar novamente após falhas—pula etapas concluídas
- **Progresso em tempo real** - Mostra o que está acontecendo em cada etapa
- **Nomes flexíveis** - Funciona com ou sem prefixo "arc-" no nome da pasta
- **Funciona com seeding** - Não aguarda transmission sair completamente
- **Ctrl+C amigável** - Pule a espera e continue manualmente depois
- **Emparelhamento de legendas** - Renomeia legendas para corresponder aos vídeos automaticamente

## Como Funciona

1. **Extrai magnets** dos resultados de busca do nyaa.si
2. **Inicia downloads** usando transmission-cli para os episódios
3. **Baixa legendas** do Google Drive em paralelo
4. **Monitora conclusão** observando estabilização de tamanhos de arquivo
5. **Organiza estrutura** - move vídeos de subpastas se necessário
6. **Emparelha legendas** - renomeia legendas para corresponder aos nomes dos vídeos
7. **Mostra resumo** - exibe total de episódios e legendas baixadas

## Pré-requisitos

Dependências do sistema obrigatórias:

| Ferramenta | Necessário para | Instalação |
|-----------|-----------------|-----------|
| **transmission-cli** | Downloads de episódios | Abaixo ↓ |
| **fzf** | Menu interativo (browse.py) | Abaixo ↓ |
| **uv** | Gerenciar scripts Python | Abaixo ↓ |

### Instalar Dependências

**Arch Linux:**
```bash
sudo pacman -S transmission-cli fzf uv
```

**Debian/Ubuntu:**
```bash
sudo apt install transmission-cli fzf python3
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS:**
```bash
brew install transmission-cli fzf uv
```

**Nota:** Para usar apenas `main.py` (entrada manual de URLs), `fzf` é opcional. Para a experiência interativa com `browse.py`, todas as ferramentas acima são necessárias.

## Instalação

```bash
git clone https://github.com/levyvix/onepace-downloader.git
cd onepace-downloader
```

Sem dependências Python para instalar—`uv` gerencia tudo automaticamente.

## Estrutura de Pastas

Após baixar um arco:
```
arc15-jaya/
├── [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
├── [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
├── subtitles/
│   ├── Jaya 01.ass
│   └── Jaya 02.ass
```

## Scripts Disponíveis

### `browse.py` — Menu Interativo (Recomendado) ⭐

A experiência recomendada. Scrapo https://onepaceptbr.github.io/ e oferece seleção interativa no terminal usando fzf.

```bash
uv run browse.py
```

**Como funciona:**
1. Scrapo automaticamente a página de downloads
2. Menu para selecionar a saga (East Blue, Alabasta, etc.)
3. Menu para selecionar o arco (Arco 8, 9, 10, etc.)
4. Gera nome da pasta automaticamente
5. Mostra confirmação dos links encontrados
6. Executa o pipeline completo (downloads + legendas + organização)

**Indicadores de disponibilidade:**
- `[nyaa+gdrive]` — Episódios + legendas disponíveis
- `[apenas nyaa]` — Apenas episódios disponíveis
- `[apenas gdrive]` — Apenas legendas disponíveis

### `main.py` - Pipeline Completo (Manual)

Executa todo o workflow em um comando. Baixa episódios, legendas, organiza e mostra resumo.

**Nota importante:** Este script NÃO faz emparelhamento de legendas automaticamente. Use-o para baixar, depois rode o `match_onepace_subtitles.py`.

```bash
uv run main.py "<URL_NYAA>" "<URL_GDRIVE>" "<NOME_PASTA>"
```

### `magnet_downloader.py` - Baixar Apenas Episódios

Extrai links magnet dos resultados de busca do nyaa.si e inicia downloads via transmission-cli.

```bash
uv run magnet_downloader.py "<URL_NYAA>" "<NOME_PASTA>"
```

### `download_subtitles.py` - Baixar Apenas Legendas

Baixa arquivos de legendas de uma pasta do Google Drive.

```bash
uv run download_subtitles.py "<URL_GDRIVE>" "<NOME_PASTA>"
```

### `match_onepace_subtitles.py` - Emparelhar Legendas com Vídeos ⭐

Renomeia automaticamente arquivos de legenda para corresponder aos nomes dos vídeos, baseado no número do episódio.

```bash
uv run match_onepace_subtitles.py "<DIR_VÍDEOS>" "<DIR_LEGENDAS>"
```

**Exemplo:**
```bash
uv run match_onepace_subtitles.py \
  "arc15-jaya" \
  "arc15-jaya/subtitles"
```

**O que faz:**
1. Encontra todos os arquivos .mkv na pasta de vídeos
2. Encontra todos os arquivos .ass na pasta de legendas
3. Extrai número do episódio de ambos
4. Renomeia legendas para corresponder aos vídeos (ex: "Jaya 01.ass" → "[One Pace][218-220] Jaya 01 [1080p][HASH].ass")

### `verify_subtitles.py` - Verificar Emparelhamento

Verifica se todos os vídeos têm legendas correspondentes.

```bash
uv run verify_subtitles.py "<NOME_PASTA>"
```

**Exemplo:**
```bash
uv run verify_subtitles.py "arc15-jaya"
```

Saída:
```
✓ [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
  → [One Pace][218-220] Jaya 01 [1080p][HASH].ass

✗ [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
  → MISSING: [One Pace][221-224] Jaya 02 [1080p][HASH].ass

Result: 1/2 videos have matching subtitles
```

## Fluxo Completo: Passo a Passo

### Opção 1: Menu Interativo (Recomendado) ⭐

```bash
# Tudo automaticamente: selecione saga → arco → execute
uv run browse.py
```

O `browse.py` cuida de tudo: download de episódios, legendas, organização e emparelhamento automático.

### Opção 2: Pipeline Manual

Se preferir especificar as URLs:

```bash
# Baixa tudo automaticamente
uv run main.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Depois emparelha as legendas
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya/subtitles"

# Opcional: Verifica se tudo está correto
uv run verify_subtitles.py "arc15-jaya"
```

### Opção 3: Controle Total (Passo a Passo)

```bash
# Passo 1: Baixa episódios (inicia transmission)
uv run magnet_downloader.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "arc15-jaya"

# Passo 2: Baixa legendas em paralelo
uv run download_subtitles.py \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Aguarde downloads terminarem (verifique com ls -lh arc15-jaya/)

# Passo 3: Emparelha legendas
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya/subtitles"

# Passo 4: Verifica resultado
uv run verify_subtitles.py "arc15-jaya"
```

## Recuperação Após Falhas

O pipeline é **idempotente**—seguro executar várias vezes:

```bash
# Primeira execução falha no meio
uv run main.py "<URL1>" "<URL2>" "arc15-jaya"

# Segunda execução retoma de onde parou
# Pula etapas concluídas automaticamente
uv run main.py "<URL1>" "<URL2>" "arc15-jaya"

# Emparelhamento pode ser executado novamente sem problemas
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya/subtitles"
```

## Solução de Problemas

### Vídeos em subpastas?

O pipeline detecta e move automaticamente. Procure por:
```
📁 Found X video(s) in subfolder: folder_name
```

Correção manual se necessário:
```bash
mv "subpasta"/*.mkv . && rmdir "subpasta"
```

### Quer pular a espera pelos downloads?

Pressione `Ctrl+C` durante a espera e execute o pipeline novamente depois—pula etapas concluídas.

### Arquivo diz "stable" mas transmission ainda ativo?

Normal! O pipeline detecta quando downloads estão **completos** (tamanhos estáveis). transmission continua rodando para **seeding**, que é esperado. Pare com:

```bash
killall transmission-cli
```

### Nenhum download iniciou?

Verifique downloads ativos:
```bash
ps aux | grep transmission-cli
ls -lh arc15-jaya/
```

Certifique-se que transmission-cli está instalado.

### Nenhuma legenda baixada?

O link do Google Drive deve estar acessível publicamente ("Qualquer pessoa com o link"). Verifique se abre no navegador.

### Emparelhamento não encontrou legendas?

As legendas devem estar em um diretório separado. Verifique:

```bash
# Verifique se as legendas estão lá
ls -la arc15-jaya/subtitles/

# O arquivo de legenda deve ter o número do episódio
# Exemplos: "Jaya 01.ass", "01.ass", "Episode 1.ass"
```

Se as legendas estão em um local diferente, especifique o caminho correto:
```bash
uv run match_onepace_subtitles.py "arc15-jaya" "caminho/para/legendas"
```

### Legendas não aparecem no mpv?

Se as legendas estão nomeadas corretamente mas mpv não as carrega:

1. Pressione `j` no mpv para alternar entre faixas de legenda
2. Ou adicione isso a `~/.config/mpv/mpv.conf`:
   ```
   sub-auto=fuzzy
   ```

Se o emparelhamento funcionou corretamente, as legendas devem carregar automaticamente.

### Verifique o emparelhamento antes de assistir

Sempre rode antes de assistir:
```bash
uv run verify_subtitles.py "arc15-jaya"
```

Saída esperada:
```
✓ video1.mkv
  → video1.ass
✓ video2.mkv
  → video2.ass

Result: 25/25 videos have matching subtitles
✓ All videos have matching subtitle files!
```

## Estrutura de Pasta Recomendada

Para manter tudo organizado:

```
~
├── Videos/onepace/
│   ├── arc15-jaya/
│   │   ├── [One Pace][218-220] Jaya 01.mkv
│   │   ├── [One Pace][218-220] Jaya 01.ass
│   │   ├── [One Pace][221-224] Jaya 02.mkv
│   │   ├── [One Pace][221-224] Jaya 02.ass
│   │   └── subtitles/  (pasta original do download)
│   │
│   ├── arc14-skypiea/
│   └── arc13-jaya/
```

## Exemplo Completo: Experiência Recomendada

```bash
cd ~/Videos/onepace

# 1. Menu interativo: seleciona saga → arco → executa pipeline
uv run browse.py

# 2. Verificar resultado (opcional)
uv run verify_subtitles.py "arc15-jaya"

# 3. Assistir!
mpv arc15-jaya/
```

### Se precisar executar manualmente:

```bash
cd ~/Videos/onepace

# 1. Download automático (episódios + legendas)
uv run main.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1abcdef..." \
  "arc15-jaya"

# 2. Emparelhar legendas
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya/subtitles"

# 3. Verificar resultado
uv run verify_subtitles.py "arc15-jaya"

# 4. Assistir!
mpv arc15-jaya/
```

## Licença

MIT

## Créditos

- [One Pace](https://onepace.net/) - Projeto de edição de One Piece
- [One Pace PT-BR](https://onepaceptbr.github.io/) - Fonte dos downloads e legendas em português
- Comunidade One Pace Brasil

## Aviso

Este projeto é apenas para uso educacional. Respeite os direitos autorais e use apenas com conteúdo que você tem permissão para baixar.
