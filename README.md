# 🚜 Sistema de Monitoramento de Rede - Operação Mina

Sistema web local desenvolvido em Python para monitoramento de ativos de rede (pings continuos e pontuais) em ambientes isolados (sem acesso à internet).

---

## 🚀 Funcionalidades Principais

* **📊 Monitoramento de Ativos:** Checagem contínua de status (Online/Offline) e latência dos IPs cadastrados.
* **🎯 Ping Pontual:** Testes individuais rápidos por IP ou nome do equipamento.
* **⚙️ Gestão de Equipamentos:** Cadastro manual ou importação massiva via arquivo Excel (`.xlsx`).
* **👥 Controle de Acesso (RBAC):**
  * **Admin:** Acesso total + gestão de usuários.
  * **Avançado:** Monitora, testa pings e cadastra/edita equipamentos.
  * **Leitura:** Apenas visualiza o monitoramento e executa pings pontuais.

---

## 📊 Padrão da Planilha para Importação (.xlsx)

Para realizar o cadastro massivo na aba **Cadastrar Equipamentos**, a planilha deve conter exatamente as seguintes colunas na primeira linha:

| Nome | IP | Setor | Tipo |
| :--- | :--- | :--- | :--- |
| Switch Principal | 192.168.1.1 | Subestação 01 | Switch |
| Câmera Britador | 192.168.1.50 | Britagem | Câmera |

---

## 📦 Como Baixar e Executar na Mina (Sem Instalação)

Não é necessário instalar Python, banco de dados ou qualquer dependência na máquina da mina.

1. Acesse a aba **Actions** neste repositório GitHub.
2. Clique no último *build* realizado com sucesso na lista.
3. Baixe o arquivo **`Sistema_Monitoramento_Mina.zip`** na seção *Artifacts*.
4. Extraia o conteúdo do `.zip` na máquina desejada.
5. Dê dois cliques no executável **`app.exe`**.
6. O sistema abrirá automaticamente no navegador da máquina local.

---

## 🔑 Acesso Inicial (Primeiro Login)

 Ao iniciar pela primeira vez, utilize o usuário administrador padrão:
* **Usuário:** `admin`
* **Senha:** `admin123`

> ⚠️ **Recomendação:** Crie novos usuários na aba *Gestão de Usuários* para a equipe da mina.
