"""btcaddr - geracao de enderecos Bitcoin e chaves WIF (stdlib).

Funcoes:
    - pubkey_compressed(k)  : chave publica comprimida (33 bytes) a partir do escalar
    - pubkey_to_p2pkh(pk)   : endereco P2PKH (legado, puzzle)
    - pubkey_to_p2wpkh(pk)  : endereco P2WPKH (segwit, bech32)
    - wif_from_privkey(k)   : WIF comprimido a partir do escalar
    - address_from_privkey(k): endereco P2PKH direto
"""

import hashlib

# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

def sha256(data):
    return hashlib.sha256(data).digest()


def hash160(data):
    """RIPEMD160(SHA256(data)). Ambas disponiveis no OpenSSL do Python."""
    return hashlib.new("ripemd160", sha256(data)).digest()


# ---------------------------------------------------------------------------
# Base58 & Base58Check
# ---------------------------------------------------------------------------

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(raw):
    """Codifica bytes para Base58."""
    n = int.from_bytes(raw, "big")
    out = ""
    while n > 0:
        n, r = divmod(n, 58)
        out = B58[r] + out
    for b in raw:
        if b == 0:
            out = B58[0] + out
        else:
            break
    return out


def b58decode(text):
    """Decodifica Base58 pura para bytes; retorna None se invalido."""
    n = 0
    for ch in text:
        idx = B58.find(ch)
        if idx == -1:
            return None
        n = n * 58 + idx
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n > 0 else b""
    # preserva zeros a esquerda ('1' -> byte 0x00)
    pad = len(text) - len(text.lstrip(B58[0]))
    return b"\x00" * pad + raw


def b58check_decode(text):
    """Base58Check: valida checksum e retorna payload; None se invalido."""
    raw = b58decode(text)
    if raw is None or len(raw) < 5:
        return None
    payload, checksum = raw[:-4], raw[-4:]
    if sha256(sha256(payload))[:4] != checksum:
        return None
    return payload


def b58check_encode(payload):
    """Base58Check: payload + 4 bytes de checksum (SHA256^2)."""
    checksum = sha256(sha256(payload))[:4]
    return b58encode(payload + checksum)


# ---------------------------------------------------------------------------
# Bech32 (BIP-173) - compacto, sem dependencias
# ---------------------------------------------------------------------------

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32_GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]


def _bech32_polymod(values):
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i in range(5):
            if (b >> i) & 1:
                chk ^= BECH32_GEN[i]
    return chk


def _bech32_hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _bech32_checksum(hrp, data):
    values = _bech32_hrp_expand(hrp) + data + [0, 0, 0, 0, 0, 0]
    polymod = _bech32_polymod(values) ^ 1
    return [(polymod >> (5 * (5 - i))) & 31 for i in range(6)]


def _bech32_encode(hrp, data):
    combined = data + _bech32_checksum(hrp, data)
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in combined)


def _convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def encode_segwit_address(hrp, witver, witprog):
    """Codifica endereco segwit (BIP-173)."""
    if witver not in (0, 1):
        raise ValueError(f"witver {witver} nao suportado")
    if len(witprog) < 2 or len(witprog) > 40:
        raise ValueError(f"witprog tam {len(witprog)} invalido")
    data = _convertbits(witprog, 8, 5)
    return _bech32_encode(hrp, [witver] + data)


# ---------------------------------------------------------------------------
# Chave publica e enderecos
# ---------------------------------------------------------------------------

def pubkey_compressed(scalar):
    """Chave publica comprimida (33 bytes) a partir do escalar k.

    Retorna bytes: 0x02 + x se y for par, 0x03 + x se y for impar.
    """
    from src.secp256k1 import mul
    pt = mul(scalar)
    x, y = pt
    prefix = b"\x02" if (y & 1) == 0 else b"\x03"
    return prefix + x.to_bytes(32, "big")


def pubkey_to_p2pkh(pubkey_bytes):
    """Endereco P2PKH (legacy, 1...) - usado pelos puzzles."""
    return b58check_encode(b"\x00" + hash160(pubkey_bytes))


def pubkey_to_p2wpkh(pubkey_bytes):
    """Endereco P2WPKH (segwit, bc1...)."""
    return encode_segwit_address("bc", 0, hash160(pubkey_bytes))


def address_from_privkey(scalar):
    """Endereco P2PKH (legacy) a partir do escalar privado."""
    pk = pubkey_compressed(scalar)
    return pubkey_to_p2pkh(pk)


def wif_from_privkey(scalar):
    """WIF comprimido (prefixo K...) a partir do escalar."""
    payload = b"\x80" + scalar.to_bytes(32, "big") + b"\x01"
    return b58check_encode(payload)


def addresses_from_privkey(scalar):
    """Retorna dicionario com P2PKH, P2WPKH e WIF para o escalar."""
    pk = pubkey_compressed(scalar)
    return {
        "p2pkh": pubkey_to_p2pkh(pk),
        "p2wpkh": pubkey_to_p2wpkh(pk),
        "wif": wif_from_privkey(scalar),
    }