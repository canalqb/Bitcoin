# Changelog

Todas as alteracoes relevantes deste repositorio.

## [2.0.1] - revisao

### Corrigido (auditoria de codigo)
- **Bug (crash)**: `candidates_for()` com `k=0` ou multiplo de `N` gerava `ValueError: not enough values to unpack` ao descompactar o ponto no infinito (`pt = ()`). Agora retorna lista vazia (sem candidatos validos) e o modo `endomorph` ignora pontos no infinito com `continue`.
- **Bug (correcao de resume)**: `_load_resume()` retornava `(data, 0)` mesmo quando `start`/`end` divergiam do solicitado, permitindo que `last_k` de outro intervalo pulasse a busca. Agora retorna `(None, 0)` (resume descartado) quando os parametros divergem.
- **Bug (validacao de resume)**: resume de um modo (ex.: sequential) podia ser aplicado a outro modo (ex.: random). Adicionado parametro `mode` a `_load_resume()` para validar e descartar resume incompativel.
- **Validacao de entrada**: `puzzle_search.py` agora rejeita `--workers < 1`, `--workers > 1` combinado com `--mode sequential`, e `--limit < 1` (antes aceitava e falhava depois com erro obscuro ou loop).
- **Desempenho (I/O)**: `snapshot.py` fazia 1 `commit()` por endereco (160 commits para 160 enderecos). Agora commita em lote a cada 10 inserts, com `commit()` final garantido no `finally`.

### Verificado
- Selftest: **17/17 PASS** apos as correcoes.

## [2.0.0] - 2025-08-28

### Analisado
- Repositorio original contendo apenas binarios Windows (`Puzzle_Random_Search`, `endomorph_puzzle`, `Snapshot`) e readmes; sem codigo-fonte.

### Adicionado
- `src/` - biblioteca Python pura (stdlib):
  - `secp256k1.py` - aritmetica de curva eliptica com endomorfismo GLV (beta/lambda), coordenadas Jacobianas.
  - `btcaddr.py` - Base58/Base58Check, Bech32 (BIP-173), P2PKH/P2WPKH, WIF.
  - `puzzle_data.py` - dados publicos dos 160 puzzles (intervalos + enderecos).
  - `searcher.py` - motor de busca em 3 modos (sequential/random/endomorph), resume atomico, `--workers`.
  - `snapshot.py` - snapshot de saldos via API publica (SQLite/TSV).
- `tools/`:
  - `puzzle_search.py` - CLI principal de busca.
  - `selftest.py` - 17 verificacoes de correcao (vetores reais + algebra).
  - `seed_puzzles.py` - gerador de `data/puzzles.json`.
  - `snapshot_btc.py` - CLI de snapshot de saldos.
- `data/puzzles.json` - 160 puzzles com intervalos/enderecos oficiais.
- Documentacao: `README.md`, `ANALYSIS.md`, `SECURITY.md`, `REQUIREMENTS.md`, `TUTORIAL.md`, `CHANGELOG.md`.
- `docs/` - post HTML + metadados (JSON) do projeto.
- `.gitignore`, `LICENSE` (MIT), `requirements.txt` (stdlib - sem dependencias).

### Corrigido
- **Bug real**: `hash160_targets()` usava `b58decode` (25 bytes) em vez de `b58check_decode` (21 bytes) - enderecos alvo eram rejeitados. Corrigido e coberto por teste.
- **Seguranca (HIGH)**: semente derivada do endereco MAC substituida por CSPRNG (`secrets`).
- **Seguranca (HIGH)**: dependencia de PostgreSQL remoto removida - dados locais.
- **Seguranca (CRITICAL)**: token de GitHub exposto em URL remota de clone - URL sanitizada apos push; recomendada rotacao.
- **Estilo**: caminhos com espacos referenciados corretamente.
- **Desempenho (HIGH)**: loop placeholder `for _ in range(total): pass` removido em `run_search_workers` - desperdicava CPU e travaria com `--limit` muito grande.
- **Correcao**: `--benchmark` agora desabilita resume - antes usava/sobrescrevia `data/resume.json` de buscas reais.
- **Consistencia**: `--limit` e velocidade em modo `endomorph` agora contam candidatos (enderecos testados) de forma identica em single-process e workers - antes o workers contava chaves (1x) e o single contava candidatos (3x).

### Melhorado (desempenho / consumo)
- Comparacao de alvo por hash160 pre-computado (evita Base58 por chave).
- Coordenadas Jacobianas (1 inversao por multiplicacao, sem inversao no laco).
- Multi-processo opcional com default de 1 processo.
- Escrita atomica de resume (tmp + rename).
- Zero dependencias externas.

## [1.0.0] - (binarios originais, mantidos)
- Versao distribuida pelo autor (@CanalQb) como executaveis Windows/Linux.
- Preservada intacta nas pastas `Puzzle_Random_Search/`, `endomorph_puzzle/`, `Snapshot/`.
