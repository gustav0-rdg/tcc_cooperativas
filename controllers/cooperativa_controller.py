from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.cpf_controller import CPF
from mysql.connector.connection import MySQLConnection
from controllers.usuarios_controller import Usuarios

class Cooperativa:

    def __init__(self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def get_by_id (self, id_cooperativa:int) -> dict:

        """
        Procura a cooperativa da qual o usuario
        fornecido é o administrador
        """

        #region Exceções

        if not isinstance(id_cooperativa, int):

            raise TypeError ('Cooperativa - "id_cooperativa" deve ser do tipo Int')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT
                    cnpj,
                    razao_social,
                    endereco,
                    cidade,
                    estado,
                    latitude,
                    longitude,
                    aprovado
                FROM cooperativas
                WHERE cooperativas.id_cooperativa = %s;
                """,

                (id_cooperativa, )

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_id": {e}')

            return False

        finally:

            cursor.close()

    def get_by_cnpj (self, cnpj:str) -> dict:

        """
        Consulta o CNPJ e retorna a cooperativa
        com o CNPJ requisitado, caso registrado,
        se não 'null'
        """

        #region Exceções

        if not isinstance(cnpj, str):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo String')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT
                    cnpj,
                    razao_social,
                    endereco,
                    cidade,
                    estado,
                    latitude,
                    longitude,
                    aprovado
                FROM cooperativas
                WHERE cooperativas.cnpj = %s;
                """,

                (cnpj, )

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_cnpj": {e}')

            return False

        finally:

            cursor.close()

    def get_by_usuario (self, id_usuario:int) -> dict:

        """
        Procura a cooperativa da qual o usuario
        fornecido é o administrador
        """

        #region Exceções

        if not isinstance(id_usuario, int):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo Int')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT
                    cnpj,
                    razao_social,
                    endereco,
                    cidade,
                    estado,
                    latitude,
                    longitude,
                    aprovado
                FROM cooperativas
                WHERE cooperativas.id_usuario = %s;
                """,

                (id_usuario, )

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_usuario": {e}')

            return False

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

        if not isinstance(id_cooperativa, str):

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

            cooperado = Usuarios(self.connection_db).create(

                nome,
                email,
                senha

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

                    if data_usuario != None:
                        return None
                
                    if data_usuario['tipo'] == 'cooperado':
                        return vincular(data_usuario['id_usuario'])

                    return None

                case _ if isinstance(cooperado, int):
                    return vincular(cooperado)
            
                case False | _:
                    return False

        except Exception as e:

            print(f'Erro - Cooperativa "vincular_cooperado": {e}')

            return False

        finally:

            cursor.close()

    def alterar_aprovacao (self, cnpj:str, aprovado:bool) -> bool:
        
        """
        Altera o estado de aprovação da
        cooperativa, variando entre True or False
        """

        #region Exceções

        if not isinstance(cnpj, str):

            raise TypeError ('Cooperativa - "cnpj" deve ser do tipo String')
        
        if not isinstance(aprovado, bool):

            raise TypeError ('Cooperativa - "aprovado" deve ser do tipo Booleano')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativas
                SET cooperativas.aprovado = %s
                WHERE cooperativas.cnpj = %s;
                """,

                (aprovado, cnpj)

            )

            self.connection_db.commit()
            return cursor.rowcount > 0 or None

        except Exception as e:

            print(f'Erro - Cooperativa "alterar_aprovacao": {e}')

            return False

        finally:

            cursor.close()

    def create (
            
        self,

        cnpj:str,
        id_usuario:str

    ) -> bool:
        
        """
        Registra a cooperativa no Banco de Dados
        e relaciona-a com o usuário
        """

        #region Exceções

        if not CNPJ.validar(cnpj):

            raise ValueError (f'Cooperativa "create" - O "cnpj" fornecido não é válido: {cnpj}')
        
        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                SELECT cooperativas.cnpj FROM cooperativas
                WHERE cooperativas.cnpj = %s;
                """,

                (cnpj, )

            )

            # Cooperativa já existente

            if cursor.fetchone() != None:
                return None

            data_cooperativa = CNPJ.consultar(cnpj)
            if not data_cooperativa:
                return False
            
            cursor.execute (

                """
                INSERT INTO cooperativas (id_usuario, cnpj, razao_social, endereco, cidade, estado, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,

                (
                    id_usuario, 
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
            return cursor.lastrowid

        except Exception as e:

            print(f'Erro - Cooperativa "create": {e}')

            return False
        
        finally:

            cursor.close()
