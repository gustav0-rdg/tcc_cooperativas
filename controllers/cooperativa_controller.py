from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.email_controller import Email
from mysql.connector import Error

class Cooperativa:

    def get_by_cnpj (cnpj:str) -> bool:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT * FROM cooperativa
                WHERE cooperativa.cnpj = %s
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Error as e:

            print(f'Erro - Cooperativa "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def autenticar (codigo_validacao:str) -> bool:

        """
        A função é a etapa final do cadastro, ativa
        a conta após o registro da cooperativa e sua
        confirmação via email
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativa
                SET cooperativa.estado = 'Confirmado'
                INNER JOIN validacoes ON validacoes.codigo = %s
                WHERE cooperativa.cnpj = validacoes.cnpj_cooperativa;

                DELETE FROM validacoes
                WHERE validacoes.codigo = %s;
                """,

                (codigo_validacao, ),

                multi=True

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativa "validar": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def delete (cnpj:str) -> bool:

        """
        Exclui permanentemente a cooperativa
        com o CNPJ fornecido do banco de dados.
        """

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            cursor.execute (

                """
                DELETE FROM cooperativa
                WHERE cooperativa.cnpj = %s;
                """,

                (cnpj, )

            )

            connection_db.commit()

            return cursor.rowcount > 0

        except Error as e:

            print(f'Erro - Cooperativa "delete": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()

    def create (
            
        __self__,

        cnpj:str,

        email:str,
        senha:str,

        validar:bool=True

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        e envia o email de autenticação
        """

        if not CNPJ.validar(cnpj):

            raise ValueError ('')

        connection_db = Connection.create()
        cursor = connection_db.cursor()

        try:

            data_cooperativa = CNPJ.consultar(cnpj)

            if not data_cooperativa:

                return False

            cursor.execute (

                """
                INSERT INTO cooperativa (cnpj, email, senha, estado)
                VALUES (%s, %s, %s, 'Aguardando Confirmação');
                """,

                (cnpj, email, senha)

            )

            connection_db.commit()

            if cursor.rowcount > 0:

                if not validar:

                    return True

                codigo_verificacao = ''

                Email.enviar (

                    data_cooperativa['emails']['address'],

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

            else:

                return False

        except Error as e:

            print(f'Erro - Cooperativa "create": {e}')

            return False

        finally:

            cursor.close()
            connection_db.close()