# Voiceover Generator Engine

Motor de automação em Python criado para preparar locuções e organizar áudio em festivais de dança.

Este repositório funciona como um estudo de caso público. Planilhas, músicas, áudios, nomes de participantes e regras específicas de eventos permanecem fora do GitHub para proteger dados operacionais e conteúdo de terceiros.

Além do estudo de caso, o repositório inclui uma **implementação de referência executável e sanitizada** do núcleo de validação e geração de manifestos. Ela usa somente dados fictícios e a biblioteca padrão do Python. O motor de produção e seus adaptadores de Excel, PDF, TTS e áudio continuam privados.

## Problema resolvido

Preparar centenas de entradas de um festival manualmente exige copiar dados, conferir numeração, tratar pronúncias, gerar locuções, baixar músicas, criar pastas e validar cada saída. O motor transforma esse trabalho em um pipeline reproduzível e auditável.

## Fluxo

```text
Excel/PDF do evento
        ↓
Extração e normalização dos registros
        ↓
Validação de números, duplicidades e campos
        ↓
Detecção de idioma e regras de pronúncia
        ↓
Geração assíncrona das locuções PT/EN
        ↓
Organização de músicas e áudios por sessão
        ↓
Manifesto JSON + relatório HTML + logs
```

## Capacidades

- leitura de planilhas Excel e documentos PDF;
- identificação de sessão, ordem, coreografia, grupo e participantes;
- TTS multilíngue com troca de voz por trecho;
- memória de termos em inglês e substituições fonéticas;
- controle de velocidade, pitch, volume, pausas e emoção;
- geração assíncrona com tentativas automáticas em caso de falha;
- combinação de segmentos e criação de locuções completas;
- auditoria de arquivos, duração, hash e estado do processamento;
- geração de relatórios HTML, manifestos JSON e logs detalhados.

## Stack

- Python
- `asyncio` e `aiohttp`
- `edge-tts`
- `openpyxl`
- `pydub` / FFmpeg
- Tkinter no aplicativo original

## Executar a implementação pública

Requer Python 3.10 ou superior.

```bash
python -m pip install -e .
voiceover-manifest examples/program.json --output manifest.json
python -m unittest discover -s tests -v
```

O comando valida a programação antes de gerar um manifesto JSON estável. Cada item contém sessão, ordem, idioma, voz, texto, caminho de saída e hash SHA-256 para auditoria.

```json
{
  "id": "afternoon-showcase-001",
  "language": "pt-BR",
  "voice": "pt-BR-FranciscaNeural",
  "status": "pending"
}
```

### Estrutura pública

```text
src/voiceover_engine/
├── domain.py       # objetos de domínio e normalização
├── pipeline.py     # validação e geração do manifesto
└── cli.py          # interface de linha de comando
tests/              # testes de duplicidade, ordem e persistência
examples/           # dados completamente fictícios
```

## Escala observada

O ambiente local de produção contém mais de **2.000 ativos de áudio**, diferentes perfis de festivais e um motor principal com **5.797 linhas de Python**.

As auditorias operacionais registram execuções de escala: **334 apresentações ativas** no Calixta 2026, **326** no FAC16, **292** no Ballace Kids e **194 músicas e locuções validadas** no ODNEM26. Esses números são referências do ambiente privado; os dados de participantes, planilhas, músicas e áudios continuam fora deste repositório.

## Decisões de engenharia

- regras de cada evento ficam separadas do núcleo reutilizável;
- a geração é auditável antes e depois do processamento;
- falhas não são silenciosas: aparecem em relatórios e logs;
- dados pessoais e mídias dos festivais não são publicados;
- a automação permite correções pontuais sem refazer todo o evento.

## Projeto relacionado

[Multilingual TTS Studio](https://github.com/marxb50/Multilingual-TTS-Studio) documenta a camada web local criada sobre este motor.

Desenvolvido por [Marx Bruno](https://github.com/marxb50).
