#!/usr/bin/env python3
"""snapshot_btc - consulta saldos de enderecos Bitcoin via API publica.

Uso:
    python tools/snapshot_btc.py --address 13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so
    python tools/snapshot_btc.py --from-puzzles 66 67 68
    python tools/snapshot_btc.py --all-puzzles
    python tools/snapshot_btc.py --from-file lista.txt
    python tools/snapshot_btc.py --all-puzzles --refresh --export dados.tsv
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import puzzle_data, snapshot  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    addr_src = p.add_mutually_exclusive_group()
    addr_src.add_argument("--address", action="append", metavar="END",
                          help="endereco para consultar (repetivel)")
    addr_src.add_argument("--from-puzzles", type=int, nargs="+",
                          metavar="N", help="numeros dos puzzles")
    addr_src.add_argument("--all-puzzles", action="store_true",
                          help="todos os 160 puzzles")
    addr_src.add_argument("--from-file", metavar="ARQUIVO",
                          help="arquivo texto com um endereco por linha")

    p.add_argument("--refresh", action="store_true",
                   help="forca reconsulta (ignora cache)")
    p.add_argument("--export-tsv", metavar="ARQUIVO",
                   help="salva resultado como TSV")
    p.add_argument("--rate-limit", type=float, default=1.0,
                   help="segundos entre requisicoes (default: 1.0)")
    p.add_argument("--db", default=os.path.join("data", "relatorio_btc.db"),
                   help="caminho do SQLite (default: %(default)s)")
    p.add_argument("--quiet", action="store_true",
                   help="menos saida no terminal")
    args = p.parse_args(argv)

    # coleta enderecos
    addresses = []
    label = ""
    if args.address:
        addresses = list(args.address)
        label = f"{len(addresses)} endereco(s) especifico(s)"
    elif args.from_puzzles:
        for n in args.from_puzzles:
            if not 1 <= n <= puzzle_data.MAX_PUZZLE:
                sys.exit(f"puzzle {n} invalido")
            addresses.append(puzzle_data.puzzle_address(n))
        label = f"puzzle(s) {', '.join(map(str, args.from_puzzles))}"
    elif args.all_puzzles:
        for n in range(1, puzzle_data.MAX_PUZZLE + 1):
            addresses.append(puzzle_data.puzzle_address(n))
        label = "todos os 160 puzzles"
    elif args.from_file:
        path = args.from_file
        if not os.path.exists(path):
            sys.exit(f"arquivo nao encontrado: {path}")
        with open(path, encoding="utf-8") as fh:
            addresses = [line.strip() for line in fh if line.strip()]
        label = f"{len(addresses)} endereco(s) de {path}"
    else:
        sys.exit("informe --address, --from-puzzles, --all-puzzles ou --from-file")

    if not addresses:
        sys.exit("nenhum endereco para consultar")

    # snapshot
    print(f"[info] {label}")
    print(f"[info] banco: {args.db}")
    started = time.time()
    results = snapshot.snapshot_addresses(
        addresses=addresses,
        db_path=args.db,
        rate_limit=args.rate_limit,
        refresh=args.refresh,
        quiet=args.quiet,
    )
    elapsed = time.time() - started

    # sumario
    total_btc = sum(r["balance"] for r in results) / 1e8
    cached = sum(1 for r in results if r.get("cached"))
    print(f"\n--- resumo ---")
    print(f"consultados: {len(results)} ({cached} em cache)")
    print(f"saldo total: {total_btc:.8f} BTC")
    print(f"tempo: {elapsed:.1f}s")

    # top 10
    results_sorted = sorted(results, key=lambda r: -r["balance"])
    print(f"\n--- top 10 saldos ---")
    for r in results_sorted[:10]:
        if r["balance"] > 0:
            print(f"  {r['address']}\t{r['balance'] / 1e8:.8f} BTC")

    if args.export_tsv:
        path = snapshot.export_tsv(results, args.export_tsv)
        print(f"[info] exportado: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())