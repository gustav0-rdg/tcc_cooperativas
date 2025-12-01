# ♻️ TCC - RECOOPERA

> "Redes que reciclam, cooperação que transforma "

## 🛠️ Tecnologias Utilizadas

### 🎨 Front-end (Interface)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### ⚙️ Back-end (Servidor e Regras)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

### 🗄️ Banco de Dados
![MySQL](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)

## 📌 Sobre o Projeto

Este projeto é um Trabalho de Conclusão de Curso (TCC) desenvolvido pelos alunos de **Desenvolvimento de Sistemas**.

O objetivo é criar uma **plataforma digital acessível** que traga transparência e oportunidades para o mercado de reciclagem. Através de uma parceria com a **Cooperativa Acácia**, identificamos a necessidade de conectar catadores e cooperativas a compradores competentes, combatendo a desinformação que leva à exploração comercial.

### 🎯 O Problema
Catadores e cooperativas muitas vezes não têm acesso fácil a informações sobre quem está comprando, por quanto e onde. Essa falta de informação gera vulnerabilidade na hora da venda dos materiais recolhidos.

### 💡 A Solução
Uma aplicação web responsiva (Mobile-First) projetada para:
1.  **Informar:** Listar compradores competentes e justos no mercado.
2.  **Conectar:** Criar um ambiente de troca de informações entre cooperativas.
3.  **Fortalecer:** Possibilitar o compartilhamento de experiências.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi estruturado utilizando a arquitetura MVC (Model-View-Controller) para garantir organização e escalabilidade.

* **Back-end:** Python 3, Flask (Microframework).
* **Front-end:** HTML5, CSS3, JavaScript (Jinja2 Templates).
* **Banco de Dados:** SQL (Integrado via conectores Python).
* **Estrutura:**
    * `controllers/`: Lógica de controle das requisições.
    * `routes/`: Definição das rotas da aplicação.
    * `database/`: Scripts e conexão com o banco.
    * `templates/`: Telas da aplicação (HTML).
    * `static/`: Arquivos de estilo e scripts (CSS/JS).

---

## 📦 Como rodar o projeto

### Pré-requisitos
* [Python 3.x](https://www.python.org/downloads/) instalado.
* [Git](https://git-scm.com/) instalado.

### Passo a passo

1.  **Clone o repositório**
    ```bash
    git clone [https://github.com/gustav0-rdg/tcc_cooperativas.git](https://github.com/gustav0-rdg/tcc_cooperativas.git)
    cd tcc_cooperativas
    ```

2.  **Crie um ambiente virtual (Opcional, mas recomendado)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação**
    ```bash
    python app.py
    ```
    *O servidor iniciará geralmente em `http://127.0.0.1:5000`*

---

## 🤝 Agradecimentos

###Um agradecimento especial à **Cooperativa Acácia** e aos professores orientadores que forneceram a direção e o contexto social necessários para este desenvolvimento.

## 💜 Desenvolvedores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/vitor-henri">
        <img src="https://github.com/vitor-henri.png" width="100px;" alt="Foto do Vitor"/><br>
        <sub>
          <b>Vitor Henrique Fonseca</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/gustav0-rdg">
        <img src="https://github.com/gustav0-rdg.png" width="100px;" alt="Foto do Gustavo"/><br>
        <sub>
          <b>Gustavo Rodrigues</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/SamuelMoreiraFerreira">
        <img src="https://github.com/SamuelMoreiraFerreira.png" width="100px;" alt="Foto do Samuel"/><br>
        <sub>
          <b>Samuel Moreira</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ZenonPB">
        <img src="https://github.com/ZenonPB.png" width="100px;" alt="Foto do Zenon"/><br>
        <sub>
          <b>Zenon Parelli</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/AliciaPavao">
        <img src="https://github.com/AliciaPavao.png" width="100px;" alt="Foto da Alicia"/><br>
        <sub>
          <b>Alícia Luíza Pavão</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/LuisBessa01">
        <img src="https://github.com/LuisBessa01.png" width="100px;" alt="Foto do Luis"/><br>
        <sub>
          <b>Felipe Luis Masalskas</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/matheusfagnani">
        <img src="https://github.com/matheusfagnani.png" width="100px;" alt="Foto do Fagnani"/><br>
        <sub>
          <b>Matheus Fagnani</b>
        </sub>
      </a>
    </td>
  </tr>
</table>
