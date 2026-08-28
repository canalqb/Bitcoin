"""snapshot - snapshot leve de saldos de enderecos em SQLite/TSV.

Diferente do SNAPSHOT_Bitcoin.exe original (que baixava o estado completo
da blockchain), esta versao consulta uma API publica e confiavel
(blockstream.info) com limite de requisicoes, armazenando em SQLite local.

Vantagens sobre a abordagem original:
  - sem baixar dezenas de GB da blockchain (menos disco/rede);
  - sem servidor PostgreSQL remoto (sem credenciais em arquivo);
  - retry com backoff e cache em SQLite (retoma de onde parou);
  - interrupcao segura (Ctrl+C) sem corromper o banco.
"""

import sqlite3
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://blockstream.info/api"
USER_AGENT = "canalqb-bitcoin-snapshot/2.0"


def _get_json(url, timeout=20, retries=3, backoff=2.0):
    """GET com User-Agent, timeout e retry com backoff exponencial."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                import json
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError,
                OSError, ValueError) as exc:
            if attempt >= retries:
                raise RuntimeError(f"falha ao consultar {url}: {exc}") from exc
            time.sleep(backoff * attempt)


def fetch_balance(address):
    """Saldo em satoshis via /api/address/{addr} (funded - spent)."""
    data = _get_json(f"{API_BASE}/address/{address}")
    cs = data.get("chain_stats", {})
    return int(cs.get("funded_txo_sum", 0)) - int(cs.get("spent_txo_sum", 0))


def _init_db(db_path):
    con = sqlite3.connect(db_path)
    con.execute(
        """CREATE TABLE IF NOT EXISTS balances (
               address   TEXT PRIMARY KEY,
               balance   INTEGER NOT NULL,
               checked_at TEXT NOT NULL
           )"""
    )
    con.commit()
    return con


def snapshot_addresses(addresses, db_path, rate_limit=1.0, refresh=False,
                       quiet=False):
    """Consulta saldos, grava em SQLite e retorna lista de dicts.

    rate_limit: segundos minimos entre requisicoes (respeito ao servico).
    refresh:    forca reconsulta mesmo com valor em cache.
    """
    con = _init_db(db_path)
    now_iso = time.strftime("%Y-%m-%d %H:%M:%S")
    results = []
    try:
        for i, addr in enumerate(addresses, 1):
            cached = None
            if not refresh:
                row = con.execute(
                    "SELECT balance FROM balances WHERE address=?",
                    (addr,),
                ).fetchone()
                if row:
                    cached = row[0]
            if cached is None:
                balance = fetch_balance(addr)
                con.execute(
                    "INSERT OR REPLACE INTO balances VALUES (?,?,?)",
                    (addr, balance, now_iso),
                )
                con.commit()
            else:
                balance = cached
            results.append({"address": addr, "balance": balance,
                            "cached": cached is not None})
            if not quiet:
                sys.stderr.write(
                    f"\r[{i}/{len(addresses)}] {addr} "
                    f"{'[cache]' if cached is not None else ''} "
                    f"{balance / 1e8:.8f} BTC"
                )
                sys.stderr.flush()
            if cached is None and i < len(addresses):
                time.sleep(rate_limit)
    except KeyboardInterrupt:
        if not quiet:
            sys.stderr.write("\n[ctrl+c] interrompido (dados ja salvos sao preservados)\n")
    finally:
        con.close()
        if not quiet:
            sys.stderr.write("\n")
    return results


def export_tsv(results, path):
    """Exporta resultados em TSV (endereco, saldo_satoshis, saldo_btc)."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("address\tbalance_satoshis\tbalance_btc\n")
        for r in results:
            fh.write(f"{r['address']}\t{r['balance']}\t{r['balance'] / 1e8:.8f}\n")
    return path
