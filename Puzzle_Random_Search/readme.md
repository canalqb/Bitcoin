---

# 🔐 Bitcoin Private Key Finder

Este é um **programa autônomo** que realiza uma busca pseudoaleatória por chaves privadas de Bitcoin, baseando-se em intervalos definidos e tentando encontrar correspondência com endereços previamente configurados.

> ⚠️ **Aviso:** Este projeto é apenas para fins **educacionais** e de **pesquisa**. Não incentive ou realize atividades que violem termos de uso, leis locais ou internacionais.

---

# Para programadores use `Puzzle_Procurar_RANDOM.exe ID` exemplo, quero procurar diretamente o puzzle 69 então `Puzzle_Procurar_RANDOM.exe 69`

---

## 🚀 O que o programa faz?

- Conecta-se a um banco de dados com:
  - Intervalos de chaves privadas em formato hexadecimal
  - Endereços de Bitcoin alvo
  - Registros de chaves encontradas (se houver)

- Permite selecionar um intervalo com base no **ID**.

- Utiliza o **endereço MAC da sua máquina** como semente (SEED) para garantir que a geração de chaves seja **única por dispositivo**.

- Realiza uma busca pseudoaleatória dentro do intervalo, gerando e testando chaves.

- Se encontrar a chave privada correspondente ao endereço:
  - Mostra a chave no formato hexadecimal
  - Gera a chave no formato WIF
  - Salva o resultado no banco de dados
  - Exibe progresso detalhado com barra visual

- Salva o progresso automaticamente em um arquivo local `.json` para continuar de onde parou.

---

## 🖥️ Como usar

1. **Execute o programa**:

   - Basta abrir o programa diretamente (duplo clique ou via terminal).
   - Um menu será exibido com a lista de IDs disponíveis para escolher.

2. **Ou inicie direto com um ID específico** (via terminal):

   ```bash
   programa.exe 3
   ```

---

## ✨ Funcionalidades

- 🔐 Geração de chaves baseada no endereço MAC
- 💾 Salvamento automático de progresso
- 📊 Exibição de progresso com porcentagem e barra visual
- 🔍 Verificação contínua até encontrar o endereço alvo
- ✅ Atualização automática no banco de dados ao encontrar a chave
- 🛑 Suporte a interrupção segura (Ctrl+C)

---

## 📌 Dicas

- O intervalo de busca é definido no banco de dados. Quanto menor o intervalo, maiores as chances de sucesso em menos tempo.
- Cada execução é única para seu dispositivo, já que o MAC address influencia diretamente na geração das chaves.

---

## 🤝 Agradecimento

Se este programa te ajudar de alguma forma, considere apoiar:

- 📺 YouTube: [youtube.com/@canalqb](https://youtube.com/@canalqb)  
- 💸 Pix: `qrodrigob@gmail.com`

---
