from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.email_controller import Email
from mysql.connector.connection import MySQLConnection
from controllers.tokens_controller import Tokens

class Cooperativa:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def autenticar (self, email:str, senha:str) -> bool:

        """
        Verifica a existência de Cooperativa com
        o email e senha fornecidos e retorna seu
        código de sessão (Token)
        """

        if not isinstance(email, str) or not isinstance(senha, str):

            raise TypeError ('Cooperativa: "email" e "senha" devem ser do tipo String')

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT
                    id_usuario
                FROM usuarios
                WHERE 
                    usuarios.email = %s
                AND
                    BYTE usuarios.senha_hash = %s;
                """,

                (email, senha)

            )

            data_user = cursor.fetchone()

            if data_user:

                return Tokens(self.connection_db).create(

                    data_user['id_usuario'],
                    ''

                )

            else:

                return False                

        except Exception as e:

            print(f'Erro - Cooperativa "autenticar": {e}')

            return False

        finally:

            cursor.close()

    def get_by_cnpj (self, cnpj:str) -> bool:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        if not isinstance(cnpj, str):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo String')

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT * FROM cooperativa
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()

    def alterar_status (self, id_usuario:int, novo_status:str) -> bool:

        """
        Altera o status da cooperativa no sistema
        """

        if not isinstance(id_usuario, int) or not isinstance(novo_status, str):

            raise TypeError ('Cooperativa - "id_usuario" e "novo_status" devem ser do tipo String')

        status_validos = ['ativo', 'inativo']

        if not novo_status in status_validos:

            raise ValueError (f'Cooperativa - "novo_status" deve ser um destes valores: {status_validos}')

        cursor = self.connection_db.cursor()

        try:

            self.cursor.execute (

                """
                UPDATE usuarios
                SET usuarios.status = %s
                WHERE usuarios.id_usuario = %s;
                """,

                (novo_status, id_usuario)

            )

            self.connection_db.commit()
            return cursor.rowcount > 0

        except Exception as e:

            print(f'Erro - Cooperativa "alterar_status": {e}')

            return False

        finally:

            cursor.close()

    def ativar (self, codigo_validacao:str) -> bool:

        """
        A função é a etapa final do cadastro, ativa
        a conta após o registro da cooperativa e sua
        confirmação via email
        """

        if not isinstance(codigo_validacao, str):

            raise TypeError ('Cooperativa - "codigo_validacao" deve ser do tipo String')

        try:

            data_token = Tokens(self.connection_db).validar(codigo_validacao)

            if data_token['tipo'] != 'cadastro' or data_token['usado'] == True:

                return False
        
            return self.alterar_status(data_token['id_usuario'], 'ativo')

        except Exception as e:

            print(f'Erro - Cooperativa "ativar": {e}')

            return False

    def delete (self, id_usuario:int) -> bool:

        """
        Exclui permanentemente a cooperativa
        com o CNPJ fornecido do banco de dados.
        """

        if not isinstance(id_usuario, int):

            raise TypeError ('Cooperativa - "id_usuario" deve ser do tipo Int')

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                DELETE FROM usuarios
                WHERE usuarios.id_usuario = %s;
                """,

                (id_usuario, )

            )

            self.connection_db.commit()
            return cursor.rowcount > 0

        except Exception as e:

            print(f'Erro - Cooperativa "delete": {e}')

            return False
        
        finally:

            cursor.close()

    def create (
            
        self,

        nome:str,
        email:str,
        senha:str,
        tipo:str,

        cnpj:str,

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        e envia o email de autenticação
        """

        if not isinstance(cnpj, str) or not isinstance(email, str) or not isinstance(senha, str):

            raise TypeError ('Cooperativa "create" - "cnpj", "email" e "senha" devem ser do tipo String')

        if not CNPJ.validar(cnpj):

            raise ValueError (f'Cooperativa "create" - O "cnpj" fornecido não é válido: {cnpj}')

        cursor = self.connection_db.cursor()

        try:

            data_cooperativa = CNPJ.consultar(cnpj)

            if not data_cooperativa:

                return False

            cursor.execute (

                """
                INSERT INTO usuarios (nome, email, senha_hash, tipo)
                VALUES (%s, %s, %s, %s);
                """,

                (nome, email, senha, tipo)

            )

            id_novo_usuario = cursor.lastrowid
            cursor.execute (

                """
                INSERT INTO cooperativas (id_usuario, cnpj, razao_social, endereco, cidade, estado, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,

                (
                    id_novo_usuario, 
                    cnpj,

                    data_cooperativa['nature']['id'],
                    f'{data_cooperativa['address']['street']}, {data_cooperativa['address']['number']}',    
                    data_cooperativa['address']['city'],
                    data_cooperativa['address']['state'],
                    '',
                    ''       
                )

            )

            self.connection_db.commit()
            if cursor.rowcount > 0:

                codigo_verificacao = Tokens(self.connection_db).create(id_novo_usuario, 'cadastro')
                return self.enviar_email_confirmacao(codigo_verificacao)

            else:

                return False

        except Exception as e:

            print(f'Erro - Cooperativa "create": {e}')

            return False
        
        finally:

            cursor.close()

    def enviar_email_confirmacao (self, destinatario:str, codigo_verificacao:str) -> bool:

        try:

            Email.enviar (

                destinatario,

                'Confirme seu e-mail no ReCoopera',
                
                #region Estrutura HTML do Email

                # CSS Inline e 'table' são usados por questão
                # de compatibilidade com a maioria dos clients
                # de e-mail que não suportam o CSS moderno
                
                # (Outlook por exemplo usa o motor do Microsoft Word 
                # para renderizar e-mails)

                f"""
                <html>
                <body
                    style="
                    font-family: Arial, sans-serif;
                    background-color: #7cc046;
                    background-image: url('https://i.imgur.com/Pv3bCJA.png');
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-position: center;
                    padding: 40px 0;
                    margin: 0;
                    word-break: normal;
                    overflow-wrap: normal;
                    white-space: normal;
                    "
                >
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                    <tr>

                        <!-- Cabeçalho -->

                        <td align="center">
                        <table
                            style="
                            max-width: 500px;
                            width: 100%;
                            background-color: #98ca60;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                            padding: 30px 25px;
                            "
                        >
                            <tr>
                            <td align="center">
                                <table width="100%" cellpadding="0" cellspacing="10">
                                    <tr>

                                        <!-- Logo -->

                                        <td align="center" valign="middle">
                                            <img 
                                                width="100"
                                                src="./image 1.png"
                                                alt="Logo de ReCoopera"
                                            />
                                        </td>

                                        <!-- Nome e Designação -->

                                        <td align="left" valign="middle">
                                            <h1
                                                style="
                                                    color: #2e5b1b;
                                                    font-size: 28px;
                                                    font-weight: 700;
                                                    margin: 0;
                                                "
                                            >
                                                ReCoopera
                                            </h1>

                                            <p
                                                style="
                                                    color: #3e2723;
                                                    font-size: 14px;
                                                    font-weight: 500;
                                                    margin: 0;
                                                "
                                            >
                                                Rede de cooperativas de catadores de recicláveis
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                            </tr>

                            <tr>

                                <td style="text-align: left">

                                    <!-- Título -->

                                    <h2
                                        style="
                                            color: #2e5b1b;
                                            font-size: 20px;
                                            font-weight: 600;
                                            margin-top: 0;
                                        "
                                    >
                                        Confirme seu e-mail
                                    </h2>

                                    <!-- Vocativo e Corpo do Texto -->

                                    <p
                                        style="
                                            color: #2e2723;
                                            line-height: 1.6;
                                            font-size: 15px;
                                            margin-bottom: 25px;
                                        "
                                    >
                                    Olá, seja bem-vindo(a) ao <b>ReCoopera</b>!<br />
                                    Para concluir seu cadastro, precisamos confirmar que este
                                    e-mail pertence a você.
                                    </p>

                                    <!-- Botão Confirmação -->

                                    <div style="text-align: center; margin: 30px 0">
                                    <a
                                        href="{codigo_verificacao}"
                                        style="
                                        background-color: #4f6d30;
                                        color: #ffffff;
                                        text-decoration: none;
                                        padding: 12px 32px;
                                        border-radius: 50px;
                                        font-weight: bold;
                                        display: inline-block;
                                        "
                                    >
                                        Confirmar meu e-mail
                                    </a>
                                    </div>

                                    <!-- Opção Alternativa (Link) -->

                                    <p
                                    style="
                                        color: #2e2723;
                                        font-size: 13px;
                                        line-height: 1.5;
                                    "
                                    >
                                        Se o botão acima não funcionar, copie e cole o link abaixo no
                                        seu navegador:

                                        <a
                                            href="{codigo_verificacao}"
                                            style="color: #2e7d32; text-decoration: underline"
                                        >
                                            {codigo_verificacao}
                                        </a>
                                    </p>

                                    <!-- Pós Escrito -->

                                    <p
                                    style="
                                        color: #444;
                                        font-size: 12px;
                                        line-height: 1.5;
                                        margin-top: 30px;
                                        text-align: center;
                                        padding-bottom: 10px;
                                    "
                                    >
                                    Caso você não tenha solicitado este cadastro, ignore este
                                    e-mail.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->

                            <tr>

                                <!-- Assinatura -->

                                <td
                                    align="center"
                                    style="
                                    border-top: 2px solid #2e5b1b;
                                    padding-top: 20px;
                                    "
                                >
                                
                                    <p
                                        style="
                                            color: #2e5b1b;
                                            font-size: 12px;
                                            font-weight: 500;
                                            margin: 0;
                                        "
                                    >
                                    © 2025 ReCoopera — Transformando reciclagem em oportunidade
                                    </p>

                                </td>
                            </tr>
                        </table>
                        </td>
                    </tr>
                    </table>
                </body>
                </html>
                """

                #endregion

            )

            return True
        
        except Exception as e:

            print(f'Erro - Cooperativa "enviar_email_confirmacao": {e}')

            return False