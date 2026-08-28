#!/usr/bin/env python3
"""seed_puzzles - gera data/puzzles.json a partir dos dados oficiais.

Os dados sao publicos (Bitcoin Puzzle Transaction). Nenhum endereco aqui
e resultado de busca deste projeto.

Uso:
    python tools/seed_puzzles.py [--output data/puzzles.json]
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import puzzle_data  # noqa: E402

SOURCE_URL = "https://github.com/Daniel-Wu-1/bitcoin-puzzle-gpu"
REF_TX = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15"


def build_document():
    puzzles = []
    for n, start, end, addr in puzzle_data.all_puzzles():
        puzzles.append({
            "id": n,
            "start": hex(start),
            "end": hex(end),
            "bits": n,
            "size": end - start + 1,
            "address": addr,
        })
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "gerado_por": "tools/seed_puzzles.py",
        "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "versao": "1.0",
        "fonte_dados": SOURCE_URL,
        "referencia_tx": REF_TX,
        "nota": "Dados publicos do desafio Bitcoin Puzzle. "
                "Intervalo do puzzle n = [2^(n-1), 2^n - 1].",
        "puzzles": puzzles,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Gera data/puzzles.json")
    p.add_argument("--output", default=os.path.join("data", "puzzles.json"))
    args = p.parse_args(argv)

    doc = build_document()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # valida o proprio JSON gerado
    with open(args.output, encoding="utf-8") as fh:
        json.load(fh)
    print(f"[ok] {args.output} gerado com {len(doc['puzzles'])} puzzles "
          f"({os.path.getsize(args.output):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
