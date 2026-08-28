"""Bitcoin puzzle tooling - CanalQb.

Pacote com a reimplementação em Python puro (stdlib apenas) das
ferramentas de pesquisa do repositório Bitcoin.

Módulos:
    secp256k1  - aritmética da curva elíptica (com endomorfismo GLV)
    btcaddr    - geração de endereços P2PKH/P2WPKH e WIF
    puzzle_data- dados oficiais dos 160 puzzles Bitcoin
    searcher   - motor de busca (random, sequencial e endomorfismo)
    snapshot   - snapshot leve de saldos em SQLite/TSV
"""

__version__ = "2.0.0"
