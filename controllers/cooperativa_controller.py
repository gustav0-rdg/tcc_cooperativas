from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.cpf_controller import CPF
from mysql.connector.connection import MySQLConnection
from controllers.usuarios_controller import Usuarios
from typing import Union, Optional
from controllers.endereco_controller import Endereco


class Cooperativa:

    def __init__ (self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def get(self, identificador: Union[int, str]) -> Optional[dict]:
        """
        Busca uma cooperativa por seu ID de cooperativa ou ID de usuário.
        """
        if not isinstance(identificador, (int, str)):
            raise TypeError('Cooperativa "get" - identificador deve ser int ou str')

        # Converte para int se for uma string de dígitos
        if isinstance(identificador, str) and identificador.isdigit():
            identificador = int(identificador)

        cursor = self.connection_db.cursor(dictionary=True)
        try:
            # A query agora busca em ambas as colunas
            cursor.execute(
                """
                SELECT *
                FROM v_cooperativas_list
                WHERE id_cooperativa = %s OR id_usuario = %s;
                """,
                (identificador, identificador)
            )
            return cursor.fetchone()
        
        except Exception as e:
            print(f'Erro - Cooperativa "get": {e}')
            return None
        finally:
            cursor.close()

    def get_by_id(self, id_cooperativa: int) -> Optional[dict]:
        if not isinstance(id_cooperativa, int):
            raise TypeError('Cooperativa - "id_cooperativa" (get_by_id) deve ser um int')


        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_cooperativa,
                    id_usuario,
                    cnpj,
                    razao_social,
                    email
                FROM v_cooperativas_list
                WHERE id_cooperativa = %s;
                """,
                (id_cooperativa,)
            )
            return cursor.fetchone()
        
        except Exception as e:
            print(f'Erro - Cooperativa "get_by_id": {e}')
            return None
        finally:
            cursor.close()

    def get_by_user_id(self, id_usuario: int) -> Optional[dict]:
        if not isinstance(id_usuario, int):
            raise TypeError('Cooperativa - "id_usuario" (get_by_user_id) deve ser um int')


        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_cooperativa,
                    id_usuario,
                    cnpj,
                    razao_social,
                    email,
                    latitude,
                    longitude
                FROM v_cooperativas_list
                WHERE id_usuario = %s;
                """,
                (id_usuario,)
            )
            return cursor.fetchone()
        
        except Exception as e:
            print(f'Erro - Cooperativa "get_by_user_id": {e}')
            return None
        finally:
            cursor.close()

    def get_all (self) -> list:
        """
        Consulta todas as cooperativas cadastradas no sistema usando a view otimizada.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute ("""
                SELECT * FROM v_cooperativas_list ORDER BY razao_social;
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f'Erro - Cooperativa "get_all": {e}')
            return []
        finally:
            cursor.close()

    def vincular_cooperado(
            
        self, 

        id_cooperativa:int, 
        
        nome:str,
        email:str,
        senha:str,

        cpf:str,
        telefone:str,
        endereco:str,
        cidade:str,
        estado:str
            
    ) -> bool:
        """
        Relaciona o usuário fornecido com a
        cooperativa
        """

        #region Exceções

        if not isinstance(id_cooperativa, int):

            raise TypeError ('Cooperativa - "id_cooperativa" deve ser do tipo Int')
        
        if not isinstance(nome, str):

            raise TypeError ('Cooperativa - "nome" deve ser do tipo String')
        
        if not isinstance(email, str):

            raise TypeError ('Cooperativa - "email" deve ser do tipo String')
        
        if not isinstance(senha, str):

            raise TypeError ('Cooperativa - "senha" deve ser do tipo String')
        
        if not isinstance(cpf, str):

            raise TypeError ('Cooperativa - "cpf" deve ser do tipo String')
        
        if not CPF.validar(cpf):

            raise ValueError ('Cooperativa - "cpf" fornecido é inválido')
        
        if not isinstance(telefone, str):

            raise TypeError ('Cooperativa - "telefone" deve ser do tipo String')
        
        if not isinstance(endereco, str):

            raise TypeError ('Cooperativa - "endereco" deve ser do tipo String')
        
        if not isinstance(cidade, str):

            raise TypeError ('Cooperativa - "cidade" deve ser do tipo String')
        
        if not isinstance(estado, str):

            raise TypeError ('Cooperativa - "estado" deve ser do tipo String')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            def vincular (id_cooperado):

                cursor.execute (

                    """
                    INSERT INTO cooperados (id_usuario, id_cooperativa, cpf, telefone, endereco, cidade, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,

                    (id_cooperado, id_cooperativa, cpf, telefone, endereco, cidade, estado)

                )

                self.connection_db.commit()
                return cursor.lastrowid
            
            def ativar_cooperado(id_usuario):
                if not isinstance(id_usuario, int):
                    raise TypeError("Error - ativar cooperado - id_usuario deve ser do tipo INT")
                cursor.execute("""
                UPDATE usuarios SET status = "ativo" WHERE id_usuario = %s;
                """, (id_usuario,))
                self.connection_db.commit()
                

            cooperado = Usuarios(self.connection_db).create(

                nome,
                email,
                senha,
                tipo='cooperado',
                status='ativo'

            )
            match cooperado:

                case None:

                    cursor.execute (

                        """
                        SELECT
                            usuarios.id_usuario,
                            usuarios.tipo
                        FROM usuarios
                        INNER JOIN
                            cooperados ON cooperados.id_usuario = usuarios.id_usuario
                        WHERE usuarios.email = %s;
                        """,

                        (email, )

                    )

                    data_usuario = cursor.fetchone()

                    if data_usuario is None:
                        return None
                
                    if data_usuario['tipo'] == 'cooperado':
                        ativar_cooperado(data_usuario['id_usuario'])
                        return vincular(data_usuario['id_usuario'])

                    return None

                case _ if isinstance(cooperado, int):
                    
                    return vincular(cooperado)
            
                case False | _:
                    return False

        except Exception as e:

            print(f'Erro - Cooperativa "vincular_cooperado": {e}')
            self.connection_db.rollback()
            return False

        finally:

            cursor.close()

    def alterar_aprovacao(self, id_cooperativa: int, aprovado: bool) -> bool:
        if not isinstance(id_cooperativa, int):
            raise TypeError('Cooperativa - "id_cooperativa" deve ser int')
        if not isinstance(aprovado, bool):
            raise TypeError('Cooperativa - "aprovado" deve ser boolean')

        cursor = self.connection_db.cursor()
        try:
            novo_status = 'ativo' if aprovado else 'reprovado'
            
            # Primeiro, pegamos o id_usuario da cooperativa
            cursor.execute("SELECT id_usuario FROM cooperativas WHERE id_cooperativa = %s", (id_cooperativa,))
            resultado = cursor.fetchone()
            
            if not resultado:
                print(f"Erro: Cooperativa com ID {id_cooperativa} não encontrada.")
                return False
            
            id_usuario = resultado[0]

            # Agora, atualizamos o status do usuário correspondente
            cursor.execute(
                """
                UPDATE usuarios
                SET status = %s
                WHERE id_usuario = %s;
                """,
                (novo_status, id_usuario)
            )
            self.connection_db.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            print(f'Erro - Cooperativa "alterar_aprovacao": {e}')
            self.connection_db.rollback()
            return False
        
        finally:
            cursor.close()

    def create (

        self, 
        id_usuario: int,

        cnpj: str, 
        razao_social: str,
        nome_fantasia: str,

        email: str,
        telefone: str,

        rua: str,
        numero: str,
        distrito: str,
        cidade: str, 
        estado: str,
        cep: str,

        arquivo_url: str

    ) -> int | bool | None:
        
        """
        Insere uma nova cooperativa no banco de dados.
        """
        
        cursor = self.connection_db.cursor()

        try:

            # Verifica se o CNPJ já existe
            cursor.execute (
                """
                SELECT cooperativas.cnpj FROM cooperativas
                WHERE cooperativas.cnpj = %s;
                """,
                (cnpj, )
            )

            if cursor.fetchone() != None:
                return None
            
            latitude = 0
            longitude = 0
            
            coordenadas = Endereco.get_coordenadas(f'{rua}, {cidade}, {estado}, Brasil')
            
            if not coordenadas is None:
                latitude, longitude = coordenadas

        # Extrai o nome do arquivo da URL para usar como nome original
            nome_arquivo_original = arquivo_url.split('/')[-1]

            cursor.execute (
                """
                INSERT INTO cooperativas 
                    (id_usuario, cnpj, razao_social, nome_fantasia, email_contato, telefone, 
                     logradouro, numero, complemento, bairro, cidade, estado, cep, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    id_usuario, cnpj, razao_social, nome_fantasia, email, telefone,
                    rua, numero, None, distrito, cidade, estado, cep, latitude, longitude
                )
            )

            id_cooperativa = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO documentos_cooperativas 
                (id_cooperativa, tipo_documento, nome_arquivo_original, nome_arquivo_armazenado, caminho_completo, tamanho_bytes, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pendente');
                """,
                (id_cooperativa, 'estatuto', nome_arquivo_original, nome_arquivo_original, arquivo_url, 0) # Tamanho 0 como placeholder
            )

            # Retorna o ID da cooperativa que acabou de ser inserida
            return id_cooperativa

        except Exception as e:

            print(f'Erro - Cooperativa "create": {e}')
            return False
        
        finally:
            cursor.close()

    def adicionar_documento(self, id_cooperativa: int, arquivo_url: str) -> Optional[int]:
        cursor = self.connection_db.cursor()
        try:
            nome_arquivo = arquivo_url.split('/')[-1]
            cursor.execute(
                """
                INSERT INTO documentos_cooperativas 
                (id_cooperativa, tipo_documento, nome_arquivo_original, nome_arquivo_armazenado, caminho_completo, tamanho_bytes, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pendente');
                """,
                (id_cooperativa, 'documento_adicional', nome_arquivo, nome_arquivo, arquivo_url, 0)
            )
            self.connection_db.commit()
            return cursor.lastrowid
        
        except Exception as e:
            print(f'Erro - Cooperativa "adicionar_documento": {e}')
            self.connection_db.rollback()
            return None
        
        finally:
            cursor.close()

    def get_pendentes_com_documentos(self) -> list | bool:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = "SELECT * FROM v_cooperativas_pendentes;"
            cursor.execute(query)
            return cursor.fetchall()
        
        except Exception as e:
            print(f'Erro - Cooperativa "get_pendentes_com_documentos": {e}')
            return False
        
        finally:
            cursor.close()

    def rejeitar_documento(self, id_cooperativa: int, id_gestor_avaliador: int, motivo: str, justificativa: str) -> bool:
        cursor = self.connection_db.cursor()
        try:
            motivo_completo = f"Motivo: {motivo}. Justificativa: {justificativa}"
            cursor.execute(
                """
                UPDATE documentos_cooperativas
                SET
                    status = 'negado',
                    motivo_rejeicao = %s,
                    data_avaliacao = NOW(),
                    avaliado_por = %s
                WHERE
                    id_cooperativa = %s AND status = 'pendente';
                """,
                (motivo_completo, id_gestor_avaliador, id_cooperativa)
            )
            self.connection_db.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            print(f'Erro - Cooperativa "rejeitar_documento": {e}')
            self.connection_db.rollback()
            return False
        
        finally:
            cursor.close()