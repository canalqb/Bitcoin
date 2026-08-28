#!/usr/bin/env python3
"""puzzle_search - busca de chaves privadas dos puzzles Bitcoin.

Uso:
    python tools/puzzle_search.py --puzzle 8
    python tools/puzzle_search.py --puzzle 8 --mode endomorph
    python tools/puzzle_search.py --puzzle 66 --limit 100000
    python tools/puzzle_search.py --start 1 --end 0xff --target 1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK
    python tools/puzzle_search.py --puzzle 8 --mode sequential --workers 1

Fins exclusivamente educacionais/pesquisa. So busque chaves de enderecos
que voce tem direito de investigar (puzzles publicos, testes proprios).
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import btcaddr, puzzle_data, searcher  # noqa: E402

DEFAULT_RESUME = os.path.join("data", "resume.json")
DEFAULT_FOUND_DIR = os.path.join("data", "found")


def parse_hex_or_int(value):
    return int(value, 0)


def build_parser():
    p = argparse.ArgumentParser(
        prog="puzzle_search",
        description="Busca de chaves privadas dos puzzles Bitcoin (educacional).",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument("--puzzle", type=int, metavar="N",
                   help="puzzle 1..160 (usa intervalo e endereco oficiais)")
    g.add_argument("--start", type=parse_hex_or_int, metavar="VALOR",
                   help="inicio do intervalo (hex 0x.. ou decimal)")
    p.add_argument("--end", type=parse_hex_or_int, metavar="VALOR",
                   help="fim do intervalo (inclusive)")
    p.add_argument("--target", action="append", metavar="ENDERECO",
                   help="endereco(s) alvo P2PKH (repetivel)")
    p.add_argument("--mode", choices=["random", "sequential", "endomorph"],
                   default="endomorph",
                   help="modo de busca (default: endomorph - aceleracao 3x)")
    p.add_argument("--limit", type=int, metavar="N",
                   help="limita o numero de chaves testadas (demo/benchmark)")
    p.add_argument("--workers", type=int, default=1, metavar="N",
                   help="processos (so random/endomorph; default 1 = menor consumo)")
    p.add_argument("--resume", metavar="ARQUIVO", default=DEFAULT_RESUME,
                   help="arquivo de resume JSON (default: %(default)s)")
    p.add_argument("--no-resume", action="store_true",
                   help="nao salvar/ler arquivo de resume")
    p.add_argument("--quiet", action="store_true", help="menos saida no terminal")
    p.add_argument("--benchmark", action="store_true",
                   help="mede velocidade (--limit obrigatorio) sem alvo")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.puzzle is not None:
        if not 1 <= args.puzzle <= puzzle_data.MAX_PUZZLE:
            sys.exit(f"erro: puzzle deve estar entre 1 e {puzzle_data.MAX_PUZZLE}")
        start, end = puzzle_data.puzzle_range(args.puzzle)
        targets = [puzzle_data.puzzle_address(args.puzzle)]
        label = f"puzzle {args.puzzle}"
    elif args.start is not None:
        if args.end is None or args.target is None:
            sys.exit("erro: --start exige --end e --target")
        start, end = args.start, args.end
        targets = args.target
        label = f"intervalo {hex(start)}..{hex(end)}"
    else:
        if not args.benchmark:
            sys.exit("erro: informe --puzzle N ou --start/--end/--target "
                     "(ou --benchmark)")
        start, end = 1, (1 << 64) - 1
        targets = []
        label = "benchmark"

    if start > end:
        sys.exit(f"erro: start ({hex(start)}) maior que end ({hex(end)})")

    resume_path = None if args.no_resume else args.resume

    if args.benchmark:
        if args.limit is None:
            sys.exit("erro: --benchmark exige --limit N")
        targets = []
        start, end = 1, 1 << 64  # intervalo amplo, sem chance de colisao

    print(f"[info] alvo: {label}")
    print(f"[info] intervalo: {hex(start)}..{hex(end)} "
          f"({end - start + 1:,} chaves)")
    print(f"[info] modo: {args.mode}"
          f"{f' | workers={args.workers}' if args.workers > 1 else ''}")
    if not args.benchmark:
        print(f"[info] endereco alvo: {targets[0]}")

    cfg = searcher.SearchConfig(
        mode=args.mode,
        start=start,
        end=end,
        targets=targets,
        limit=args.limit,
        resume_path=resume_path,
        quiet=args.quiet,
    )

    started = time.time()
    if args.workers > 1:
        result = searcher.run_search_workers(cfg, args.workers)
    else:
        result = searcher.run_search(cfg)
    elapsed = result["elapsed"]

    if result["found"]:
        f = result["found"]
        key = f["key"]
        wif = btcaddr.wif_from_privkey(key)
        print("\n=== CHAVE ENCONTRADA ===")
        print(f"chave (hex) : {hex(key)}")
        print(f"chave (dec) : {key}")
        print(f"endereco    : {f['address']}")
        print(f"WIF         : {wif}")
        if not args.no_resume and resume_path and os.path.exists(resume_path):
            try:
                os.remove(resume_path)
            except OSError:
                pass
        if not args.benchmark:
            found_dir = DEFAULT_FOUND_DIR
            os.makedirs(found_dir, exist_ok=True)
            payload = {
                "encontrado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
                "puzzle": args.puzzle,
                "chave_hex": hex(key),
                "chave_dec": str(key),
                "wif": wif,
                "endereco": f["address"],
                "modo": f["mode"],
            }
            path = os.path.join(
                found_dir,
                f"puzzle_{args.puzzle or 'custom'}_{time.strftime('%Y%m%d_%H%M%S')}.json",
            )
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            print(f"[info] resultado salvo em: {path}")
    else:
        print("\n=== FIM (nao encontrado) ===")
        print(f"chaves testadas: {result['keys_tried']:,}")
        print(f"velocidade     : {result['keys_tried'] / max(elapsed, 1e-9):,.1f} chaves/s")
        print(f"tempo          : {elapsed:.1f}s")
        if result["interrupted"]:
            print("[info] interrompido pelo usuario; resume salvo.")

    if args.benchmark:
        print(f"\n[benchmark] {result['keys_tried']:,} chaves em {elapsed:.1f}s "
              f"-> {result['keys_tried'] / max(elapsed, 1e-9):,.1f} chaves/s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
