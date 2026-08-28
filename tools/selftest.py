#!/usr/bin/env python3
"""selftest - verificacao de correcao da implementacao.

Valida, sem tocar a rede:
  1. codificacao Base58/Base58Check (roundtrip + checksum);
  2. derivacao de endereco P2PKH comprimido contra vetores reais
     (chaves conhecidas dos puzzles 1..19 x tabela publica de enderecos);
  3. endereco P2WPKH (bech32) contra vetor conhecido;
  4. WIF (roundtrip + prefixo/versao);
  5. propriedades do endomorfismo GLV (beta, lambda) da secp256k1;
  6. integracao: busca sequential + endomorph encontra chaves reais
     dos puzzles 1 e 8 em intervalos pequenos;
  7. data/puzzles.json valido e consistente.

Nenhuma chave real e gerada/utilizada alem dos vetores publicos do
desafio (puzzles ja resolvidos). Saida: 0 = sucesso.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import btcaddr, puzzle_data, secp256k1, searcher  # noqa: E402

# chaves privadas publicas dos puzzles 1..19 (bitcointalk thread 1306983)
SOLVED_KEYS = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
    9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5216, 14: 10544,
    15: 26867, 16: 51510, 17: 95823, 18: 198669, 19: 357535,
}

# vetor bech32 conhecido (BIP-173): chave publica de testes
BECH32_PUBKEY = bytes.fromhex(
    "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798"
)
BECH32_EXPECTED = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"

FAILED = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))
    if not cond:
        FAILED.append(name)
    return cond


def main():
    print("== 1. Base58/Base58Check ==")
    addr = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"
    raw = btcaddr.b58check_decode(addr)
    check("decode puzzle66", raw is not None and raw[:1] == b"\x00" and len(raw) == 21)
    check("roundtrip b58", btcaddr.b58check_encode(raw) == addr)
    check("checksum invalido", btcaddr.b58check_decode(addr[:-1] + ("1" if addr[-1] != "1" else "2")) is None)

    print("== 2. Enderecos P2PKH (vetores reais 1..19) ==")
    ok = True
    for n, key in SOLVED_KEYS.items():
        got = btcaddr.address_from_privkey(key)
        want = puzzle_data.puzzle_address(n)
        if got != want:
            ok = False
            print(f"    mismatch p{n}: got={got} want={want}")
    check("19 vetores reais", ok)

    print("== 3. P2WPKH bech32 ==")
    check("vetor bech32",
          btcaddr.pubkey_to_p2wpkh(BECH32_PUBKEY) == BECH32_EXPECTED,
          f"got={btcaddr.pubkey_to_p2wpkh(BECH32_PUBKEY)}")

    print("== 4. WIF ==")
    wif = btcaddr.wif_from_privkey(3)
    dec = btcaddr.b58check_decode(wif)
    check("WIF roundtrip",
          dec is not None and dec == b"\x80" + (3).to_bytes(32, "big") + b"\x01")
    check("WIF prefixo K", wif.startswith("K"))

    print("== 5. Endomorfismo GLV ==")
    check("beta^3 == 1 (mod p)",
          (secp256k1.BETA2 * secp256k1.BETA) % secp256k1.P == 1)
    check("lambda^3 == 1 (mod n)",
          (secp256k1.LAMBDA2 * secp256k1.LAMBDA) % secp256k1.N == 1)
    g = secp256k1.G
    q1 = secp256k1.mul(secp256k1.LAMBDA)
    check("mul(lambda) == phi(G)",
          q1 == ((secp256k1.BETA * g[0]) % secp256k1.P, g[1]))
    q2 = secp256k1.mul(secp256k1.LAMBDA2)
    check("mul(lambda^2) == phi^2(G)",
          q2 == ((secp256k1.BETA2 * g[0]) % secp256k1.P, g[1]))
    e = secp256k1.endomorphism(secp256k1.mul(5))
    check("endomorphism 3 pontos distintos", len(set(e)) == 3)
    check("endomorphism pontos na curva", all(secp256k1.is_on_curve(pt) for pt in e))

    print("== 6. Integracao (busca real em intervalos pequenos) ==")
    # puzzle 1: intervalo [1,1], chave 1
    r1 = searcher.run_search(searcher.SearchConfig(
        mode="sequential", start=1, end=1,
        targets=[puzzle_data.puzzle_address(1)], quiet=True, resume_path=None))
    check("sequential acha puzzle 1",
          r1["found"] and r1["found"]["key"] == 1,
          f"got={r1['found']}")
    # puzzle 8: intervalo [128,255], chave 224
    r8 = searcher.run_search(searcher.SearchConfig(
        mode="sequential", start=128, end=255,
        targets=[puzzle_data.puzzle_address(8)], quiet=True, resume_path=None))
    check("sequential acha puzzle 8",
          r8["found"] and r8["found"]["key"] == 224,
          f"got={r8['found']}")
    # endomorph: range [1,1] deve achar a chave 1 via candidato k=1
    r1e = searcher.run_search(searcher.SearchConfig(
        mode="endomorph", start=1, end=1,
        targets=[puzzle_data.puzzle_address(1)], quiet=True, resume_path=None))
    check("endomorph acha puzzle 1", r1e["found"] and r1e["found"]["key"] == 1,
          f"got={r1e['found']}")

    print("== 7. data/puzzles.json ==")
    path = os.path.join("data", "puzzles.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        check("json valido (160 puzzles)", len(doc.get("puzzles", [])) == 160)
        p8 = next((x for x in doc["puzzles"] if x["id"] == 8), None)
        check("intervalo p8 no json",
              p8 and int(p8["start"], 0) == 128 and int(p8["end"], 0) == 255)
    else:
        print("  [SKIP] data/puzzles.json ausente (rode tools/seed_puzzles.py)")

    print()
    if FAILED:
        print(f"FALHOU: {len(FAILED)} teste(s): {FAILED}")
        return 1
    print("TODOS OS TESTES PASSARAM")
    return 0


if __name__ == "__main__":
    sys.exit(main())
