# Bitcoin - Analise do Projeto

## 1. Inventario do repositorio original

Repositorio: `https://github.com/canalqb/Bitcoin`
Branch: `main` | Commit inicial (clone): `c5bd6a37c03117a4c5ee24c7a29ff3f6ce2d0d78`

| Caminho | Conteudo | Tipo |
| ------- | -------- | ---- |
| `README.md` | Descricao geral do canal @CanalQb | texto |
| `Puzzle_Random_Search/btc_privatekey_endomorph_search.exe` | busca pseudoaleatoria de chaves | binario Windows x64 (PE32+, ~15 MB) |
| `Puzzle_Random_Search/readme.md` | documentacao | texto |
| `endomorph_puzzle/btc_privatekey_endomorph_search.exe` | busca por endomorfismo | binario Windows x64 (PE32+, ~10 MB) |
| `endomorph_puzzle/Lambda e Endomorfismo` | explicacao textual dos conceitos | texto |
| `endomorph_puzzle/readme.md` | documentacao | texto |
| `Snapshot/SNAPSHOT_Bitcoin.exe` | download da blockchain + SQLite | binario Windows x64 (PE32+, ~7.6 MB) |
| `Snapshot/readme.md` | documentacao | texto |

**Nao ha codigo-fonte no repositorio** - apenas binarios compilados.
`NAO VALIDADO`: linguagem/versao exata dos binarios (indicios de
compilacao Go pelo tamanho/estrutura PE, sem confirmacao).

## 2. Problemas encontrados

| Severidade | Problema | Local | Solucao |
| ---------- | -------- | ----- | ------- |
| CRITICAL | Token do GitHub gravado na URL remota do clone (`.git/config`) | config local | URL sanitizada apos o push; recomendada rotacao do token |
| HIGH | Semente da busca derivada do **endereco MAC** (previsivel/publico) | `Puzzle_Random_Search` | Usar `secrets.randbelow` (CSPRNG do SO) |
| HIGH | Dependencia de **PostgreSQL remoto** para dados de busca (credenciais em jogo) | `endomorph_puzzle` | Dados locais (`data/puzzles.json`) + SQLite local |
| MEDIUM | Binarios sem fonte - impossivel auditar | repositorio | Reimplementacao aberta em Python |
| MEDIUM | Sem `.gitignore` - risco de commit de `.db`/`.env` | repositorio | `.gitignore` adicionado |
| MEDIUM | Nenhum teste automatizado | repositorio | `tools/selftest.py` (17 verificacoes) |
| LOW | Docs dos binarios sem versao/checksum | readmes | `REQUIREMENTS.md` + checksum documentado no CHANGELOG |

## 3. Bug real corrigido na implementacao

Durante o desenvolvimento do `src/searcher.py`, `hash160_targets()`
usava `b58decode` (que retorna 25 bytes, com checksum) em vez de
`b58check_decode` (21 bytes, payload) - qualquer endereco alvo era
rejeitado. Corrigido e coberto pelo selftest.

## 4. Melhorias de seguranca

1. **Entropia**: `secrets` (CSPRNG) no lugar de MAC address.
2. **Sem banco remoto**: nada de credenciais em arquivos.
3. **Validacao de entrada**: `argparse`, `int(value, 0)`, faixa 1..160,
   endereco validado por Base58Check antes da busca.
4. **Escrita atomica** de resume (`tmp` + `rename`) - evita arquivo
   corrompido em caso de Ctrl+C.
5. **Sem secrets no repo**: verificado por `.gitignore` e inspecao.
6. **Leitura de progresso via stderr**, stdout limpo para resultados.

## 5. Melhorias de desempenho / consumo de hardware

| Aspecto | Antes (binario) | Depois (Python) |
| ------- | --------------- | --------------- |
| Endomorfismo GLV | presente | mantido (3 chaves/multiplicacao) |
| Multi-processo | nao documentado | `--workers N` opcional, default 1 |
| Comparacao de alvo | via endereco | por **hash160 pre-computado** (evita Base58 por chave) |
| Aritmetica de curva | compilada | Jacobiano (1 inversao por multiplicacao, sem inv no laco) |
| Dependencias | - | **zero** (stdlib) |
| Snapshot | download da blockchain inteira | API publica + SQLite (sem GB de disco) |

`NAO MEDIDO`: comparacao CPU/RAM/tempo entre os binarios originais e a
versao Python - sem ambiente de referencia dos binarios.

## 6. Novos recursos adicionados

- **`tools/puzzle_search.py`** - busca em 3 modos: `sequential`
  (deterministico), `random` (CSPRNG) e `endomorph` (3x).
- **`tools/selftest.py`** - verificacao de correcao (17 testes).
- **`tools/seed_puzzles.py`** - gera `data/puzzles.json` (160 puzzles).
- **`tools/snapshot_btc.py`** - snapshot leve de saldos via
  blockstream.info com cache SQLite e exportacao TSV.
- **Resume automatico** (JSON atomico) com retomada segura.
- **`--benchmark`** para medir velocidade local sem rede.

## 7. Estrutura final

```
Bitcoin/
├── src/               # biblioteca Python (stdlib)
│   ├── secp256k1.py   # curva + endomorfismo GLV
│   ├── btcaddr.py     # enderecos P2PKH/P2WPKH, WIF, Base58/Bech32
│   ├── puzzle_data.py # dados dos 160 puzzles
│   ├── searcher.py    # motor de busca (3 modos + workers)
│   └── snapshot.py    # snapshot de saldos (SQLite/TSV)
├── tools/             # CLIs
│   ├── puzzle_search.py
│   ├── selftest.py
│   ├── seed_puzzles.py
│   └── snapshot_btc.py
├── data/              # dados gerados (ignorados: resume/found/*.db)
├── docs/              # post HTML + metadados
└── (pastas originais mantidas: Puzzle_Random_Search, endomorph_puzzle, Snapshot)
```

## 8. Analise dos subdiretorios (binarios originais)

Os tres executaveis nas pastas originais foram inspecionados tecnicamente
(analise estatica de cabecalho PE e strings - sem execucao, sem desmontagem
completa):

| Binario | SHA-256 | Observacoes |
| ------- | ------- | ----------- |
| `Puzzle_Random_Search/btc_privatekey_endomorph_search.exe` | `430fa02c...e017ee7` | PE32+ x86-64, 7 secoes, ~15.5 MB |
| `endomorph_puzzle/btc_privatekey_endomorph_search.exe` | `40300558...35719c` | PE32+ x86-64, 7 secoes, ~10.2 MB |
| `Snapshot/SNAPSHOT_Bitcoin.exe` | `4ba30365...fb1f1f1` | PE32+ x86-64, 7 secoes, ~7.6 MB |

Descobertas:

- **Linguagem: Swift** - marcadores `__swift_1`/`__swift_2` presentes nos
  tres binarios (runtime Swift embutido explica o tamanho dos arquivos).
- **Nome interno do projeto: "Mini"** - assembly name no manifest
  (`name="Mini" version="1.0.0.0"`).
- **PostgreSQL remoto confirmado** - strings `5432` (porta padrao do
  PostgreSQL) e `pg_` nos tres binarios. Confirma o uso de banco remoto
  (o readme de `endomorph_puzzle` cita PostgreSQL; `Snapshot` usava banco
  local SQLite `relatorio_btc.db`).
- **Recurso `.rsrc` gigante** (15.3 MB / 10.0 MB / 7.4 MB) - dados embutidos
  como recurso Windows (RCDATA), provavelmente tabelas de enderecos/intervalos.
  `.text` (codigo) e pequeno (~116 KB): a logica de negocio e simples, os
  dados e o runtime dominam o tamanho.
- **Nenhuma string de conexao em claro** (host, user, password, URLs):
  provavelmente ofuscadas/criptografadas no binario ou fornecidas em
  tempo de execucao. `NAO VALIDADO` - exigiria desmontagem/execucao
  controlada para confirmar.
- **Identificacao incompleta**: `NAO VALIDADO` - versao do compilador
  Swift e dependencias exatas (exigiria tooling especifico).

Implicacoes de seguranca para quem usa os binarios originais:

1. **PostgreSQL remoto** exige credenciais e rede para terceiros - a
   reimplementacao Python usa dados locais (`data/puzzles.json`) e nao
   depende de servidor externo.
2. **Binarios nao auditaveis** (sem fonte) - impossivel verificar o que
   e enviado pela rede. A versao Python e 100% auditavel (stdlib).
3. Os binarios e pastas originais foram **preservados intactos** neste
   repositorio, mas nao sao a implementacao de referencia.

