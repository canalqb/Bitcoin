## 🧑‍💻 COMO USAR O APLICATIVO SNAPSHOT BTC

O aplicativo **SNAPSHOT BTC**, versão 1.0, permite que você baixe automaticamente os dados mais recentes da blockchain do Bitcoin (endereços e saldos), e os armazene em um banco de dados local para análise.

### 🔷 Para Usuários Windows (.exe)

#### ✅ Passo a passo:

1. **Dê dois cliques** no arquivo `SNAPSHOT_Bitcoin.exe`.
Também disponivel no link https://canalqb.blogspot.com/?c=snapshotbitcoinwindows
Como minha conta é gratuita no Github, pode ser que eu precise de espaço então vou manter pelo menos o Readme.md para as informações

3. O aplicativo será aberto em uma janela de terminal com o título:
   ```
   Sistema SNAPSHOT @CANALQB - V 1.0
   ```

4. Ele vai começar o processo:
   - Se já houver um arquivo de dados do dia atual, você poderá escolher se quer baixar de novo ou não.
   - Depois, ele faz a extração dos dados e a importação automática para o banco.

5. Ao final, você verá a mensagem indicando que o processo foi concluído com sucesso.

#### 📁 Arquivos gerados:
- `relatorio_btc.db` — banco de dados contendo os dados processados.
- Arquivos `.tsv` com os dados extraídos, caso deseje usar fora do banco.

---

### 🟢 Para Usuários Linux/Ubuntu (.bin)

Para usar no linux, o arquivo está com 39.7M, devido o tamanho resolvi deixar no TeraBox no link
https://canalqb.blogspot.com/?c=snapshotbitcoinpuzzle

#### ✅ Passo a passo:

1. Abra o terminal na pasta onde está o aplicativo.

2. Torne o arquivo executável (se ainda não estiver):
   ```bash
   chmod +x SNAPSHOT_Bitcoin.bin
   ```

3. Execute o aplicativo:
   ```bash
   ./SNAPSHOT_Bitcoin.bin
   ```

4. Assim como no Windows, o terminal exibirá o progresso das etapas: download, extração, e importação dos dados.

5. Ao final, os dados estarão armazenados localmente em um banco SQLite.

---

## 📊 O que fazer depois?

Você pode abrir o arquivo `relatorio_btc.db` com qualquer ferramenta que leia bancos SQLite, como:

- **DB Browser for SQLite** (interface gráfica)
- **Python**, para análises personalizadas
- Ferramentas de BI como Power BI (com conector SQLite)

---

## 🔄 Frequência de uso

Você pode rodar o aplicativo **diariamente ou sempre que quiser atualizar os dados**. Ele sempre vai buscar a versão mais atualizada do snapshot.

---

## 📦 Onde estão os dados?

Tudo é armazenado localmente, na mesma pasta do aplicativo:

- O banco de dados: `relatorio_btc.db`
- Os arquivos baixados e extraídos, com a data no nome

---

Pix: qrodrigob@gmail.com
