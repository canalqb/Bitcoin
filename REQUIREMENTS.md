# Bitcoin - Requisitos

O projeto inteiro (motor de busca, snapshot e testes) usa **apenas a
biblioteca padrao do Python** - sem dependencias externas, sem framework,
sem compilacao. Isso reduz ataque de cadeia de suprimentos, espaco em
disco, consumo de RAM e o tempo de instalacao a zero.

## Python

| Item              | Valor                                   |
| ----------------- | --------------------------------------- |
| Versao minima     | 3.8 (usa `pow(a, -1, m)` / f-strings)   |
| Versao recomendada| 3.11+ (validado em 3.11.15)             |
| Gerenciador       | `pip` (sem dependencias para instalar)  |
| Runtime           | CPython 3.x (Windows/Linux/macOS)       |

## Modulos da stdlib utilizados

| Modulo            | Uso                                          |
| ----------------- | -------------------------------------------- |
| `hashlib`         | SHA-256 e RIPEMD-160 (enderecos, checksum)   |
| `secrets`         | CSPRNG do SO para geracao de chaves          |
| `sqlite3`         | banco local do snapshot                      |
| `urllib`          | consulta a API blockstream.info              |
| `json`            | arquivo de dados / resume                    |
| `argparse`        | interface de linha de comando                |
| `multiprocessing` | busca multi-processo opcional                |
| `os` / `time`     | I/O e progresso                              |

## Ferramentas de desenvolvimento

| Ferramenta        | Uso                           | Versao testada |
| ----------------- | ----------------------------- | -------------- |
| `python`          | execucao/CLI                  | 3.11.15        |
| `git`             | versionamento                 | 2.54.0         |
| `gh` (opcional)   | integracao GitHub             | 2.95.0         |

## Binarios originais (mantidos como referencia)

Os arquivos `.exe` originais (`Puzzle_Random_Search/`,
`endomorph_puzzle/`, `Snapshot/`) sao executaveis para **Windows x64**
(PE32+) e **Linux/Ubuntu**. Foram distribuidos sem codigo-fonte no
repositorio; a linguagem/versao exata de compilacao e `NAO VALIDADO`
(sem acesso ao codigo-fonte). Esta nova versao Python os substitui com
codigo aberto.

## Sistema operacional / arquitetura

- Suportado: Windows 10/11 x64, Linux x64, macOS x64/ARM
- Requisito: Python 3.8+ instalado
- A busca endomorph e puramente CPU (1 core por default, `--workers N`
  para escalar sob demanda)

## Compliance de seguranca

Nenhuma credencial, token ou chave privada e necessaria para executar
qualquer ferramenta deste projeto. Conexoes de rede (snapshot) usam
HTTPS contra a API publica blockstream.info. Consulte `SECURITY.md`
para a politica completa.
