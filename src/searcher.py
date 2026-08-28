"""searcher - motor de busca de chaves privadas (stdlib apenas).

Modos de busca:

  sequential  - percorre k de `start` ate `end` em ordem (deterministico,
                resumivel pelo ultimo k testado). Ideal para intervalos
                pequenos ja resolvidos (ex.: puzzles 1..50).

  random      - sorteia k com `secrets.randbelow` (CSPRNG do SO, nao MAC
                address, nao semente previsivel). Sem repeticao de trabalho
                entre maquinas; cobertura uniforme do intervalo.

  endomorph   - como random, mas usa o endomorfismo GLV da secp256k1:
                uma unica multiplicacao escalar gera 3 chaves relacionadas
                (k, LAMBDA*k, LAMBDA^2*k). Custo de 1 mult + 2/3 de custo
                de endereco = ate 3x mais chaves testadas por operacao.

O motor compara por HASH160 pre-computado dos alvos (sem gastar base58
por candidato) e so calcula endereco/WIF completo quando encontra.

Progresso: salvamento periodico em JSON (escrita atomica via temp+rename)
e interrupcao segura com Ctrl+C. Multi-processo opcional via --workers
(apenas modos random/endomorph), com default de 1 processo para minimizar
consumo de CPU/RAM.
"""

import json
import os
import secrets
import signal
import sys
import time

from src import btcaddr, secp256k1

# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------

def hash160_targets(addresses):
    """Converte lista de enderecos P2PKH em set de hash160 (comparacao O(1))."""
    targets = set()
    for addr in addresses:
        raw = btcaddr.b58check_decode(addr)
        if raw is None or raw[:1] != b"\x00" or len(raw) != 21:
            raise ValueError(f"endereco P2PKH invalido: {addr}")
        targets.add(raw[1:])
    return targets


def candidates_for(k, mode):
    """Gera os pares (escalar, hash160) para uma chave k conforme o modo."""
    if mode == "endomorph":
        q = secp256k1.mul(k)
        out = []
        for scalar, pt in zip(
            (k, (k * secp256k1.LAMBDA) % secp256k1.N,
             (k * secp256k1.LAMBDA2) % secp256k1.N),
            secp256k1.endomorphism(q),
        ):
            x, y = pt
            pk = (b"\x02" if (y & 1) == 0 else b"\x03") + x.to_bytes(32, "big")
            out.append((scalar, btcaddr.hash160(pk)))
        return out
    # random / sequential: 1 candidato por multiplicacao
    x, y = secp256k1.mul(k)
    pk = (b"\x02" if (y & 1) == 0 else b"\x03") + x.to_bytes(32, "big")
    return [(k, btcaddr.hash160(pk))]


def _atomic_write(path, data):
    """Escrita atomica (temp + rename) - evita arquivo de resume corrompido."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Busca em processo unico
# ---------------------------------------------------------------------------

class SearchConfig:
    def __init__(self, mode, start, end, targets, limit=None,
                 resume_path=None, quiet=False, interval=2.0):
        self.mode = mode
        self.start = start
        self.end = end
        self.targets = hash160_targets(targets)   # set de hash160
        self.target_addresses = list(targets)      # para exibicao
        self.limit = limit
        self.resume_path = resume_path
        self.quiet = quiet
        self.interval = interval


def _load_resume(path, start, end):
    """Carrega arquivo de resume; valida parametros para nao retomar errado."""
    if not path or not os.path.exists(path):
        return None, 0
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None, 0
    if (data.get("start") != start or data.get("end") != end):
        return data, 0
    return data, data.get("attempts", 0)


def _display(keys, rate, elapsed, found=False, found_addr=""):
    line = (f"[{time.strftime('%H:%M:%S')}] chaves={keys:,} "
            f"velocidade={rate:,.1f}/s tempo={int(elapsed) // 60}m{int(elapsed) % 60:02d}s")
    if found:
        line += f" ENCONTRADA -> {found_addr}"
    sys.stderr.write("\r" + line + " " * 20)
    sys.stderr.flush()


def run_search(cfg):
    """Executa a busca em processo unico. Retorna dict de resultado.

    O sinal Ctrl+C e tratado: salva o resume e encerra de forma limpa.
    """
    if cfg.mode not in ("random", "sequential", "endomorph"):
        raise ValueError(f"modo invalido: {cfg.mode}")

    span = cfg.end - cfg.start + 1
    resume_data, attempts_offset = _load_resume(cfg.resume_path, cfg.start, cfg.end)
    keys = attempts_offset
    last_save = time.time()

    stop = {"flag": False}
    state = {"last_k": None}

    def _handler(signum, frame):  # noqa: ARG001
        stop["flag"] = True
        sys.stderr.write("\n[ctrl+c] finalizando...\n")

    old_handler = signal.signal(signal.SIGINT, _handler)

    started = time.time()
    last_display = 0.0
    result = {"found": None, "keys_tried": 0, "elapsed": 0.0, "interrupted": False}

    def _save(last_k=None):
        if not cfg.resume_path:
            return
        data = {"mode": cfg.mode, "start": cfg.start, "end": cfg.end,
                "attempts": keys, "updated_at": time.time()}
        if cfg.mode == "sequential" and last_k is not None:
            data["last_k"] = last_k
        _atomic_write(cfg.resume_path, data)

    try:
        iterator = iter(())
        if cfg.mode == "sequential":
            # determinismo: resume pelo ultimo k
            k = cfg.start
            if resume_data and isinstance(resume_data.get("last_k"), int):
                k = max(cfg.start, resume_data["last_k"] + 1)
            keys = k - cfg.start
            state["last_k"] = k

            def gen():
                nonlocal k
                while k <= cfg.end and not stop["flag"]:
                    yield k
                    k += 1
            iterator = gen()
        else:  # random / endomorph
            if cfg.limit is not None:
                keys = 0

            def gen():
                # em random o resume e apenas informativo (contador)
                total = cfg.limit if cfg.limit is not None else None
                n = 0
                while not stop["flag"]:
                    if total is not None and n >= total:
                        break
                    yield secrets.randbelow(span) + cfg.start
                    n += 1
            iterator = gen()

        for k in iterator:
            state["last_k"] = k
            for scalar, h in candidates_for(k, cfg.mode):
                keys += 1
                if h in cfg.targets:
                    addr = btcaddr.address_from_privkey(scalar)
                    result["found"] = {"key": scalar, "address": addr,
                                       "mode": cfg.mode}
                    if not cfg.quiet:
                        _display(keys, keys / max(time.time() - started, 1e-9),
                                 time.time() - started, found=True, found_addr=addr)
                    break
            if result["found"]:
                break
            if cfg.limit is not None and keys >= cfg.limit:
                break

            now = time.time()
            if not cfg.quiet and now - last_display >= cfg.interval:
                _display(keys, keys / max(now - started, 1e-9), now - started)
                last_display = now
            if cfg.resume_path and now - last_save >= 10:
                _save(state["last_k"])
                last_save = now
    finally:
        _save(state["last_k"])
        signal.signal(signal.SIGINT, old_handler)

    result["keys_tried"] = keys
    result["elapsed"] = time.time() - started
    result["interrupted"] = stop["flag"]
    if not cfg.quiet:
        sys.stderr.write("\n")
    return result


# ---------------------------------------------------------------------------
# Busca multi-processo (opcional - apenas random/endomorph)
# ---------------------------------------------------------------------------

_worker_mode = None
_worker_start = 0
_worker_end = 0
_worker_targets = frozenset()


def _init_worker(mode, start, end, targets_tuple):
    global _worker_mode, _worker_start, _worker_end, _worker_targets
    _worker_mode = mode
    _worker_start = start
    _worker_end = end
    _worker_targets = frozenset(targets_tuple)


def _worker_try(_):
    """Processa uma chave sorteada; retorna (scalar, endereco) ou None."""
    span = _worker_end - _worker_start + 1
    k = secrets.randbelow(span) + _worker_start
    for scalar, h in candidates_for(k, _worker_mode):
        if h in _worker_targets:
            return (scalar, btcaddr.address_from_privkey(scalar))
    return None


def run_search_workers(cfg, workers):
    """Busca random/endomorph com N processos. Progresso sem lock por
    resultado (cada resultado == 1 multiplicacao concluida)."""
    import itertools
    import multiprocessing

    if cfg.mode not in ("random", "endomorph"):
        raise ValueError("workers so suporta modos random/endomorph")
    if workers < 1:
        workers = 1

    started = time.time()
    result = {"found": None, "keys_tried": 0, "elapsed": 0.0, "interrupted": False}
    keys = 0
    stop = {"flag": False}

    def _handler(signum, frame):  # noqa: ARG001
        stop["flag"] = True

    old_handler = signal.signal(signal.SIGINT, _handler)

    pool = multiprocessing.Pool(
        processes=workers,
        initializer=_init_worker,
        initargs=(cfg.mode, cfg.start, cfg.end, tuple(cfg.targets)),
    )
    last_display = 0.0
    total = cfg.limit if cfg.limit is not None else None
    try:
        try:
            it = pool.imap_unordered(_worker_try, itertools.count(), chunksize=1)
            for _ in range(total) if total is not None else ():
                pass  # placeholder; loop real abaixo
            # iteracao lazily interrompida por found/stop/limit
            for res in it:
                if stop["flag"]:
                    pool.terminate()
                    break
                keys += 1
                if total is not None and keys >= total:
                    pool.terminate()
                    break
                if res is not None:
                    scalar, addr = res
                    result["found"] = {"key": scalar, "address": addr,
                                       "mode": cfg.mode}
                    if not cfg.quiet:
                        _display(keys, keys / max(time.time() - started, 1e-9),
                                 time.time() - started, found=True, found_addr=addr)
                    pool.terminate()
                    break
                now = time.time()
                if not cfg.quiet and now - last_display >= cfg.interval:
                    _display(keys, keys / max(now - started, 1e-9), now - started)
                    last_display = now
        except KeyboardInterrupt:
            pool.terminate()
    finally:
        pool.close()
        pool.join()
        signal.signal(signal.SIGINT, old_handler)

    result["keys_tried"] = keys
    result["elapsed"] = time.time() - started
    result["interrupted"] = stop["flag"]
    if not cfg.quiet:
        sys.stderr.write("\n")
    return result
