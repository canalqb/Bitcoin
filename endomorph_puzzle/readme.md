# CanalQb - Pesquisa baseada em Endomorfismo - Lambda

## Descrição

O btc_privatekey_endomorph_search **CanalQb** é uma ferramenta de pesquisa baseada em **endomorfismos** aplicada à manipulação de **chaves privadas** no contexto de criptomoeda. Ele permite realizar transformações rápidas e anônimas de chaves privadas dentro de um mesmo espaço numérico, otimizando tanto a geração quanto a pesquisa de chaves, sem comprometer sua estrutura original.

A aplicação utiliza uma combinação de cálculos matemáticos, chamadas a um banco de dados e a aplicação de funções rápidas para encontrar a chave privada correspondente a um endereço-alvo. Ele pode ser configurado para buscar chaves privadas em intervalos definidos por um banco de dados remoto.

## Funcionalidades

- **Conexão com Banco de Dados**: O btc_privatekey_endomorph_search conecta-se a um banco de dados PostgreSQL para consultar um conjunto de dados de chaves privadas.
- **Processamento de Endomorfismo**: Aplica transformações baseadas em endomorfismos para calcular possíveis chaves privadas correspondentes a um endereço-alvo.
- **Busca Rápida**: Realiza a busca de forma eficiente através de intervalos de valores (range) definidos no banco de dados.
- **Geração de Chave Privada e WIF**: Ao encontrar a chave privada correta, a ferramenta gera e exibe o formato WIF da chave.
- **Interatividade**: O btc_privatekey_endomorph_search permite ao usuário interagir com o sistema através de um menu simples para selecionar o intervalo de pesquisa.

## Como Usar

1. Clone este repositório:
   ```bash
   git clone https://github.com/canalqb/Bitcoin/endomorph_puzzle/canalqb.git
   cd canalqb
   ```  

2. O aplicativo irá apresentar um menu para você escolher o intervalo de pesquisa desejado.

6. A ferramenta irá realizar a busca e, se encontrar a chave privada correspondente ao endereço-alvo, exibirá o **WIF** da chave.

## Aviso de Segurança

Este btc_privatekey_endomorph_search lida com informações sensíveis (como chaves privadas). **Use com cuidado** e nunca execute em ambientes inseguros. Certifique-se de que você está operando dentro de uma rede segura e de que seus dados não serão comprometidos.

## Contribuição

Sinta-se à vontade para enviar pull requests ou abrir problemas caso encontre algo que precisa ser melhorado ou corrigido. Para contribuições, por favor, siga as boas práticas de desenvolvimento de código aberto e forneça descrições claras das mudanças que está propondo.

## Licença

Este projeto está licenciado sob a Licença MIT.

---

**CanalQb** - Pesquisa baseada em Endomorfismo - Lambda

Os puzzles 8 e 13 estão resolvidos, mas estão disponiveis para teste.

Aceitando doações em bc1qks4k7klzju6afzkyhnxtf84zctt5t9kl9vyl8e

Link para windows sem print de todas as frases: https://canalqb.blogspot.com/?c=puzzleendomorphw
Link para ubuntu sem print de todas as frases: https://canalqb.blogspot.com/?c=puzzleendomorphl
./btc_privatekey_endomorph_search_semprint
