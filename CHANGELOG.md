# Changelog

Todas as alteracoes relevantes deste repositorio.

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
