# Bitcoin - Politica de Seguranca

## Modelo de ameaca

Este projeto trabalha com **criptografia de curva eliptica** e, em caso
de sucesso na busca, **chaves privadas reais**. A politica abaixo existe
para garantir que nenhuma chave, credencial ou dado sensivel vaze.

## O que este projeto NAO faz

- Nao envia chaves para a rede (nada e transmitido, tudo e local).
- Nao armazena chaves privadas em disco, exceto quando o usuario
  encontra uma chave de um puzzle publico e opta por salvar o resultado
  (arquivo em `data/found/`, ignorado pelo git).
- Nao se conecta a banco remoto (a versao original usava PostgreSQL
  remoto com credenciais - **removido**).

## Credenciais e secrets

- Nenhum token, senha, API key ou chave privada esta versionado.
- O arquivo `.env` e ignorado pelo git (`.gitignore`).
- Nenhuma credencial e exigida para rodar.

### Achado durante a auditoria (CORRIGIDO)

- **`CRITICAL - SECRET/CREDENTIAL EXPOSURE`**: o token do GitHub foi
  usado na URL de clone remoto e ficou gravado em `.git/config` do clone
  local. A URL remota foi sanitizada apos o push para nao reter o token.
  **Recomendacao: rotacionar o token exposto.**
- O token armazenado no `gh` CLI local estava **invalido/vencido**
  (`gh auth status` reportou falha) - `NAO VALIDADO` para reuso.

## Seguranca criptografica

- **Geracao de chaves**: usa `secrets.randbelow` (CSPRNG do sistema
  operacional). A versao original derivava a semente do **endereco MAC**
  da placa de rede - falha corrigida: o MAC e previsivel e publico, nao
  deve ser usado como fonte de entropia.
- **Implementacao de curva**: `secp256k1` em Python puro, validada por
  `tools/selftest.py` contra vetores reais (chaves publicas dos puzzles
  1..19, vetor BIP-173 bech32) e propriedades algebricas do endomorfismo
  GLV (`beta^3 == 1`, `lambda^3 == 1`, `phi(G) == lambda*G`).
- **Hash/encoding**: SHA-256, RIPEMD-160 e Base58Check validados por
  vetores conhecidos. Bech32 implementado conforme BIP-173 e testado
  contra o vetor oficial.

## Rede (apenas snapshot)

- O snapshot consulta a API publica `blockstream.info` por **HTTPS**
  (TLS), com `User-Agent` identificado, timeout e retry com backoff.
- Nenhum dado pessoal e enviado - apenas enderecos publicos.

## Responsabilidade

Este projeto tem finalidade **educacional e de pesquisa**. A busca so
deve ser executada sobre enderecos cuja investigacao o usuario tem
direito (puzzles publicos, testes proprios). Nao apoiamos uso contra
carteiras de terceiros.

## Reportar vulnerabilidades

Abra uma issue no repositorio com a descricao do problema. Nao inclua
chaves, tokens ou enderecos reais em reports publicos.
