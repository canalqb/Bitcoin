# Tutorial - Ferramentas Bitcoin Puzzle @CanalQb

## O que e

Este projeto oferece ferramentas para pesquisar chaves privadas do
"Bitcoin Puzzle Transaction" (tx `08389f34...`) - um desafio
criptografico que bloqueou BTC em 160 enderecos com intervalos de chave
conhecidos. Tambem inclui um snapshot leve de saldos via API publica.

As ferramentas sao **100% Python**, sem dependencias externas, e
funcionam em Windows, Linux e macOS.

## Requisitos

- Python 3.8 ou superior (recomendado: 3.11+)
- Conexao com internet (apenas para o `snapshot_btc`)

## Instalacao

```bash
# Clone (se ainda nao fez)
git clone https://github.com/canalqb/Bitcoin.git
cd Bitcoin

# Nenhuma dependencia para instalar - a stdlib cobre tudo.
# Opcional: verificar se a implementacao esta correta
python tools/selftest.py
```

## Guia rapido

### 1. Verificar se a implementacao esta correta

```bash
python tools/selftest.py
```

Saida esperada:
```
[PASS] 19 vetores reais          # enderecos dos puzzles 1..19 batem
[PASS] vetor bech32               # BIP-173
[PASS] mul(lambda) == phi(G)      # endomorfismo GLV correto
[PASS] sequential acha puzzle 1   # busca funcional
TODOS OS TESTES PASSARAM
```

### 2. Encontrar uma chave de puzzle ja resolvido (demo)

```bash
# Puzzle 8: chave 224, intervalo [128, 255]
python tools/puzzle_search.py --puzzle 8 --mode sequential
```

Saida esperada:
```
=== CHAVE ENCONTRADA ===
chave (hex) : 0xe0
endereco    : 1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK
WIF         : KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU...
```

### 3. Buscar um puzzle nao resolvido (modo endomorph)

```bash
# Puzzle 66 (6.6 BTC, 66 bits - cerca de 2^65 chaves)
# ATENCAO: espaco enorme, modo demo com limite
python tools/puzzle_search.py --puzzle 66 --limit 100000
```

### 4. Modo benchmark (medir velocidade da sua maquina)

```bash
python tools/puzzle_search.py --benchmark --limit 10000
```

### 5. Snapshot de saldos (consultar saldos na blockchain)

```bash
# Todos os puzzles
python tools/snapshot_btc.py --all-puzzles

# Puzzles especificos
python tools/snapshot_btc.py --from-puzzles 66 67 68

# Endereco avulso
python tools/snapshot_btc.py --address 13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so

# Exportar como TSV
python tools/snapshot_btc.py --all-puzzles --export-tsv dados.tsv
```

## Explicacao dos modos de busca

### Sequential

Percorre o intervalo do inicio ao fim, em ordem. Deterministico e
resumivel (salva o ultimo k testado). Ideal para intervalos pequenos
(puzzles 1..50, ja resolvidos, para verificacao rapida).

### Random

Sorteia chaves com `secrets.randbelow()` - CSPRNG do sistema
operacional, sem semente previsivel. Cada execucao cobre o intervalo
de forma independente. Nao ha garantia de cobertura total.

### Endomorph

Como o random, mas o endomorfismo GLV da secp256k1 deriva **3 chaves
relacionadas** a partir de uma unica multiplicacao escalar. Efetivamente
3x mais chaves testadas por operacao, sem aumentar o consumo de CPU.

## Parametros do puzzle_search

```
--puzzle N         puzzle 1..160 (usa dados oficiais)
--start/--end      intervalo customizado
--target           endereco alvo (repetivel)
--mode             sequential | random | endomorph (default: endomorph)
--limit N          para de testar apos N chaves (demo/benchmark)
--workers N        processos paralelos (default: 1)
--resume ARQ       arquivo de progresso (default: data/resume.json)
--no-resume        nao salvar/ler progresso
--benchmark        mede velocidade sem alvo (exige --limit)
--quiet            menos saida no terminal
```

## Exemplos avancados

```bash
# Intervalo customizado com alvo manual
python tools/puzzle_search.py --start 0x80 --end 0xFF \
    --target 1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK --mode sequential

# Puzzle 8 com 4 processos (modo endomorph)
python tools/puzzle_search.py --puzzle 8 --mode endomorph --workers 4

# Snapshot com refresh forcado e exportacao
python tools/snapshot_btc.py --all-puzzles --refresh --export-tsv snapshot.tsv
```

## Erros comuns

### "endereco P2PKH invalido"
O endereco informado em `--target` nao e um P2PKH valido (checksum
incorreto, formato errado, ou nao comeca com "1"). Use
`python tools/selftest.py` para verificar se o Base58 esta funcionando.

### "puzzle deve estar entre 1 e 160"
O argumento `--puzzle` aceita apenas 1..160. Use `--start`/`--end`
`--target` para intervalos arbitrarios.

### Velocidade baixa
A implementacao e em Python puro - cada multiplicacao escalar custa
~1-3 ms (dependendo do hardware). Para acelerar: use `--workers N`
(quantos nucleos de CPU quiser dedicar) ou modo `endomorph` (3x
mais chaves por operacao).

### "Nao encontrado" em puzzle ja resolvido
O modo `random` nao garante cobertura. Use `--mode sequential` para
intervalos pequenos.

## Solucao de problemas

1. **Teste primeiro**: `python tools/selftest.py` - se falhar, algo
   esta errado na instalacao ou no codigo.
2. **Log no terminal**: ative `--quiet` para saida minima, ou omita
   para ver progresso.
3. **Interromper**: Ctrl+C salva o progresso e encerra de forma limpa.
4. **Retomar**: na proxima execucao com o mesmo `--resume`, o modo
   `sequential` retoma de onde parou.

## Como contribuir

1. Fork o repositorio.
2. Crie um branch: `git checkout -b minha-melhoria`.
3. Faca as alteracoes.
4. Execute `python tools/selftest.py` - todos os testes devem passar.
5. Commit e push.
6. Abra um Pull Request.

## Limites conhecidos

- A busca em Python puro e lenta comparada a implementacoes em C/Go
  (~1-3k chaves/s por core). Para puzzles de 66+ bits, a forca bruta
  nao e viavel em Python - este projeto e educacional/didatico.
- O snapshot consulta a API blockstream.info com rate limit de 1 req/s
  (configuravel). Enderecos com saldo zero sao registrados como 0.