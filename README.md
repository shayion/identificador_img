# identificador_img - API de Análise de Imagem com Google Cloud Vision

Este projeto é uma API RESTful desenvolvida com FastAPI que permite o upload e a análise de imagens utilizando a API Google Cloud Vision. Ele inclui um sistema de autenticação de usuários e persiste os dados das imagens e suas labels em um banco de dados SQLite.

## Funcionalidades

* **Autenticação de Usuários:** Registro, Login, Logout e Refresh de tokens JWT.
* **Análise de Imagem:** Upload de imagens e detecção de labels (rótulos) usando o Google Cloud Vision.
* **Persistência de Dados:** Armazenamento de informações de usuários, imagens e labels detectadas em um banco de dados SQLite (`database.db`).
* **Armazenamento de Imagens:** As imagens uploaded são salvas localmente na pasta `uploads/`.

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:

* **Python 3.9+** (Recomendado Python 3.12)
* **Git**

## Configuração do Ambiente

Siga os passos abaixo para configurar e rodar o projeto em um novo ambiente.

### 1. Clonar o Repositório

Abra seu terminal ou prompt de comando e clone o repositório:

```bash
git clone [https://github.com/shayion/identificador_img.git](https://github.com/shayion/identificador_img.git)
cd identificador_img
2. Criar e Ativar o Ambiente Virtual (venv)
É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

Bash

# Criar o ambiente virtual (se ainda não existir)
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
Você verá (venv) no início da linha do seu terminal, indicando que o ambiente virtual está ativo.

3. Instalar as Dependências
Com o ambiente virtual ativo, instale todas as dependências do projeto:

Bash

pip install -r requirements.txt
4. Configurar as Credenciais do Google Cloud Vision
Este projeto utiliza a API Google Cloud Vision. Você precisa de uma conta de serviço e uma chave JSON para autenticação.

Crie um Projeto no Google Cloud: Se ainda não tiver um, crie um novo projeto no Google Cloud Console.

Habilite a API Google Cloud Vision: No seu projeto, vá para "APIs e Serviços" > "Biblioteca" e procure por "Cloud Vision API". Habilite-a.

Crie uma Conta de Serviço:

No Google Cloud Console, vá para "IAM e Admin" > "Contas de Serviço".

Clique em "CRIAR CONTA DE SERVIÇO".

Dê um nome e uma descrição.

Atribua o papel: Usuário da API Cloud Vision (ou Vision AI User). Se não encontrar, o papel Editor temporariamente pode servir para testes, mas não é recomendado para produção.

Continue e finalize a criação.

Gere uma Chave JSON:

Após criar a conta de serviço, clique nela na lista.

Vá para a aba "Chaves".

Clique em "ADICIONAR CHAVE" > "Criar nova chave" > "JSON".

Um arquivo JSON será baixado.

Salve a Chave no Projeto:

Crie uma pasta chamada credentials na raiz do seu projeto (identificador_img/credentials/).

Mova o arquivo JSON baixado para esta pasta e renomeie-o para service_account_key.json.

Importante: Este arquivo contém suas credenciais e não é versionado no Git. Ele está configurado no .gitignore para sua segurança.

A estrutura final relevante deve ser:

identificador_img/
├── app/
├── credentials/
│   └── service_account_key.json
├── venv/                      (ignorada pelo Git)
├── .gitignore
├── database.db                (ignorada pelo Git)
├── requirements.txt
├── README.md                  (este arquivo)
└── uploads/                   (ignorada pelo Git)
5. Rodar a Aplicação
Com todas as dependências instaladas e as credenciais configuradas, você pode iniciar o servidor Uvicorn:

Bash

uvicorn app.main:app --reload
O servidor estará rodando em http://127.0.0.1:8000.

6. Acessar a Documentação da API (Swagger UI)
Você pode acessar a documentação interativa da API (Swagger UI) em seu navegador:

http://127.0.0.1:8000/docs

Uso Básico da API
Registrar um Usuário:

Vá para POST /api/v1/auth/register no Swagger UI.

Crie um novo usuário com username e password.

Fazer Login:

Vá para POST /api/v1/auth/login.

Use o username e password que você acabou de criar.

Você receberá um access_token e um refresh_token.

Autorizar no Swagger UI:

Clique no botão "Authorize" no canto superior direito do Swagger UI.

No campo username e password, use as credenciais do seu usuário.

Isso fará o login e aplicará o token para rotas protegidas.

Analisar uma Imagem:

Vá para POST /api/v1/analyze.

Clique em "Try it out".

Faça o upload de um arquivo de imagem.

Clique em "Execute".

A imagem será salva na pasta uploads/ e seus metadados e labels serão armazenados no database.db.


---
