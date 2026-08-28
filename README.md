# Bitcoin - Ferramentas de Pesquisa e Analise

Colecao de ferramentas para o "Bitcoin Puzzle Transaction" e analise
da blockchain Bitcoin, desenvolvidas por [@CanalQb](https://www.youtube.com/@canalqb).

**Versao 2.0** - reimplementacao em Python puro (stdlib, sem dependencias)
com correcoes de seguranca, melhorias de desempenho e novos recursos.

## Ferramentas

| Ferramenta | Descricao |
| ---------- | --------- |
| `python tools/puzzle_search.py` | Busca de chaves privadas em 3 modos (sequential, random, endomorph 3x) |
| `python tools/snapshot_btc.py` | Consulta de saldos via API publica (SQLite + TSV) |
| `python tools/selftest.py` | Verificacao de correcao (17 testes, vetores reais) |
| `python tools/seed_puzzles.py` | Geracao dos dados dos 160 puzzles |

## Modos de busca

- **Sequential** - percorre o intervalo em ordem, resumivel.
- **Random** - sorteio com CSPRNG do SO (`secrets`).
- **Endomorph** - aceleracao 3x via endomorfismo GLV da secp256k1.

## Requisitos

- **Python 3.8+** (stdlib cobre tudo - zero dependencias externas)
- Windows, Linux ou macOS; CPU apenas (1 core default, `--workers N` opcional)

## Instalacao

```bash
git clone https://github.com/canalqb/Bitcoin.git
cd Bitcoin
python tools/seed_puzzles.py   # gerar data/puzzles.json
python tools/selftest.py       # verificar implementacao (opcional)
```

## Uso rapido

```bash
# Verificar puzzles resolvidos (demo)
python tools/puzzle_search.py --puzzle 8 --mode sequential

# Buscar com endomorfismo (3x)
python tools/puzzle_search.py --puzzle 66 --limit 100000

# Benchmark de velocidade
python tools/puzzle_search.py --benchmark --limit 10000

# Snapshot de saldos de todos os puzzles
python tools/snapshot_btc.py --all-puzzles
```

Veja `TUTORIAL.md` para guia completo.

## Seguranca

- Geracao de chaves por `secrets.randbelow` (CSPRNG, nao MAC address).
- Dados locais (SQLite/JSON) - sem PostgreSQL remoto.
- Conexoes HTTPS contra API publica.
- Veja `SECURITY.md` para politica completa.

## Estrutura

```
Bitcoin/
├── src/            # biblioteca Python (stdlib)
├── tools/          # CLIs
├── data/           # dados gerados (puzzles, resume, found)
├── docs/           # post HTML + metadados
├── *.md            # documentacao
├── .gitignore
├── CHANGELOG.md
├── LICENSE
└── (pastas originais: Puzzle_Random_Search, endomorph_puzzle, Snapshot)
```

## Licenca

MIT - veja `LICENSE`.

## Autor

[@CanalQb](https://www.youtube.com/@canalqb) - Pesquisador independente.