from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
from controllers.tokens_controller import Tokens
import hashlib
from datetime import datetime, timedelta
from controllers.email_controller import Email

class Usuarios:

    def __init__ (self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Usuarios: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    @staticmethod
    def criptografar (texto:str) -> str:

        return hashlib.sha256(texto.encode('utf-8')).hexdigest()
    
    def get_by_id (self, id_usuario:int) -> dict:

        """
        Consulta no banco de dados o
        usuário com o ID fornecido
        """

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Usuarios "get_by_id" - "id_usuario" deve ser do tipo Int')
            
        #endregion

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT
                    usuarios.id_usuario,
                    usuarios.nome,
                    usuarios.email,
                    usuarios.tipo,
                    usuarios.status,
                    usuarios.data_criacao
                FROM usuarios
                WHERE usuarios.id_usuario = %s;
                """,

                (id_usuario, )

            )

            return cursor.fetchone()            

        except Exception as e:

            print(f'Erro - Usuarios "get_by_id": {e}')

            return False

        finally:

            cursor.close()

    def autenticar (self, email:str, senha:str) -> bool:

        """
        Verifica a autenticidade do usuário
        conferindo a existência do seu email
        e senha cadastrados no banco de dados
        """

        #region Exceções

        if not isinstance(email, str):

            raise TypeError ('Usuarios "autenticar" - "email" deve ser do tipo String')
        
        if not isinstance(senha, str):

            raise TypeError ('Usuarios "autenticar" - "senha" deve ser do tipo String')
            
        #endregion

        cursor = self.connection_db.cursor(dictionary=True)
        try:
            senha_hash = Usuarios.criptografar(senha)
            cursor.execute (
                """
                SELECT id_usuario FROM usuarios
                WHERE usuarios.email = %s AND usuarios.senha_hash = %s;
                """, (email, senha_hash) 
            )
            data_user = cursor.fetchone()
            self.connection_db.commit()

            if data_user:
                return data_user['id_usuario'] # Retorna o ID se autenticado
            else:
                return None                

        except Exception as e:

            print(f'Erro - Usuarios "autenticar": {e}')

            return False

        finally:

            cursor.close()

    def trocar_senha (self, id_usuario:int, nova_senha:str) -> bool:

        """
        Alterar a senha do usuário
        no banco de dados
        """

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Usuarios "trocar_senha" - "id_usuario" deve ser do tipo Int')
        
        if not isinstance(id_usuario, int):

            raise TypeError ('Usuarios "trocar_senha" - "nova_senha" deve ser do tipo String')
        
        if len(nova_senha) < 8:

            raise TypeError ('Usuarios "trocar_senha" - "nova_senha" deve ter 8 ou mais caractéres')
            
        #endregion

        cursor = self.connection_db.cursor()

        try:

            nova_senha = Usuarios.criptografar(nova_senha)
            cursor.execute (

                """
                UPDATE usuarios
                SET usuarios.senha_hash = %s
                WHERE usuarios.id_usuario = %s;
                """,

                (nova_senha, id_usuario)

            )

            return cursor.rowcount > 0 or None               

        except Exception as e:

            print(f'Erro - Usuarios "trocar_senha": {e}')

            return False

        finally:

            cursor.close()

    def create (
            
        self,

        nome:str,

        email:str,
        senha:str,

        tipo:str

    ) -> bool:
        
        """
        Cadastra o usuário (de forma genérica) 
        no banco de dados
        """

        #region Exceções

        if not isinstance(nome, str) or not isinstance(email, str) or not isinstance(senha, str) or not isinstance(tipo, str):

            raise TypeError ('Usuarios "create" - "nome", "email", "senha" e "tipo" devem ser do tipo String')
            
        if len(senha) < 8:

            raise ValueError ('Usuarios "create" - "senha" deve ter 8 ou mais caractéres')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT id_usuario FROM usuarios
                WHERE usuarios.email = %s;
                """,

                (email, )

            )

            # Já há um usuário com o email cadastrado

            if cursor.fetchone() != None:
                return None

            senha = Usuarios.criptografar(senha)
            cursor.execute (

                """
                INSERT INTO usuarios (nome, email, senha_hash, tipo)
                VALUES (%s, %s, %s, %s);
                """,

                (nome, email, senha, tipo)

            )

            self.connection_db.commit()
            return cursor.lastrowid

        except Exception as e:

            print(f'Erro - Usuarios "create": {e}')

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

    def alterar_status (self, id_usuario:int, novo_status:str) -> bool:

        """
        Altera o status do usuario no sistema
        """

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Usuarios "alterar_status" - "id_usuario" deve ser do tipo Int')
        
        if not isinstance(novo_status, str):

            raise TypeError ('Usuarios "alterar_status" - "novo_status" deve ser do tipo String')

        status_validos = ['ativo', 'inativo', 'bloqueado', 'pendente']
        if not novo_status in status_validos:

            raise ValueError (f'Usuarios "alterar_status" - "novo_status" deve ser um destes valores: {status_validos}')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE usuarios
                SET usuarios.status = %s
                WHERE usuarios.id_usuario = %s;
                """,

                (novo_status, id_usuario)

            )

            self.connection_db.commit()
            return cursor.rowcount > 0 or None

        except Exception as e:

            print(f'Erro - Usuarios "alterar_status": {e}')

            return False

        finally:

            cursor.close()

    def delete (self, id_usuario:int) -> bool:

        """
        Exclui permanentemente o usuário
        do banco de dados
        """

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Usuarios "delete" - "id_usuario" deve ser do tipo Int')
            
        #endregion

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
            return cursor.rowcount > 0 or None

        except Exception as e:

            print(f'Erro - Usuarios "delete": {e}')

            return False
        
        finally:

            cursor.close()
    