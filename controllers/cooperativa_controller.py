from data.connection_controller import Connection
from controllers.cnpj_controller import CNPJ
from controllers.cpf_controller import CPF
from mysql.connector.connection import MySQLConnection
from controllers.usuarios_controller import Usuarios

class Cooperativa:

    def __init__ (self, connection_db:MySQLConnection):
        
        if not Connection.validar(connection_db):

            raise ValueError (f'Erro - Cooperativa: Valores inválidos para os parâmetros "connection_db": {connection_db}')
        
        self.connection_db = connection_db

    def get (self, identificador:int|str) -> dict:

        """
        Procura a cooperativa da qual o usuario
        fornecido é o administrador
        """

        #region Exceções

        if not isinstance(identificador, (int, str)):

            raise TypeError ('Cooperativa - "identificador" deve ser id_usuario, id_cooperativa ou cnpj')

        #endregion

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT
                    cooperativas.id_cooperativa,
                    cooperativas.cnpj,
                    cooperativas.razao_social,
                    cooperativas.endereco,
                    cooperativas.cidade,
                    cooperativas.estado,
                    cooperativas.latitude,
                    cooperativas.longitude,
                    cooperativas.aprovado,
                    cooperativas.id_usuario,
                    cooperativas.telefone,
                    cooperativas.email,
                    cooperativas.nome_fantasia,
                    usuarios.status,
                    cooperativas.ultima_atualizacao,
                    cooperativas.data_cadastro,
                    COUNT(vendas.id_venda) AS `total_vendas`,
                    COALESCE(
                        GROUP_CONCAT(
                            DISTINCT materiais_catalogo.nome_especifico ORDER BY materiais_catalogo.nome_especifico SEPARATOR '|'
                        ), NULL
                    ) AS `materiais_vendidos`
                FROM cooperativas
                INNER JOIN
                    usuarios ON usuarios.id_usuario = cooperativas.id_usuario
                LEFT JOIN
                    vendas ON vendas.id_cooperativa = cooperativas.id_cooperativa
                LEFT JOIN
                    vendas_itens ON vendas_itens.id_venda = vendas.id_venda  
                LEFT JOIN materiais_catalogo
                    ON materiais_catalogo.id_material_catalogo = vendas_itens.id_material_catalogo
                WHERE 
                    cooperativas.id_cooperativa = %s OR
                    cooperativas.id_usuario = %s OR
                    cooperativas.cnpj = %s
                GROUP BY
                    cooperativas.id_cooperativa
                LIMIT 1;
                """,

                (identificador, identificador, identificador)

            )

            return cursor.fetchone()

        except Exception as e:

            print(f'Erro - Cooperativa "get_by_id": {e}')

            return False

        finally:

            cursor.close()

    def get_all (self) -> list:

        """
        Consulta todas as cooperativas
        cadastradas no sistema
        """

        cursor = self.connection_db.cursor(dictionary=True)

        try:

            cursor.execute (

                """
                SELECT
                    cooperativas.id_cooperativa,
                    cooperativas.cnpj,
                    cooperativas.razao_social,
                    cooperativas.endereco,
                    cooperativas.cidade,
                    cooperativas.estado,
                    cooperativas.latitude,
                    cooperativas.longitude,
                    cooperativas.aprovado,
                    cooperativas.id_usuario,
                    cooperativas.telefone,
                    cooperativas.email,
                    cooperativas.nome_fantasia,
                    usuarios.status,
                    cooperativas.ultima_atualizacao,
                    cooperativas.data_cadastro,
                    COUNT(vendas.id_venda) AS `total_vendas`,
                    COALESCE(
                        GROUP_CONCAT(
                            DISTINCT materiais_catalogo.nome_especifico ORDER BY materiais_catalogo.nome_especifico SEPARATOR '|'
                        ), NULL
                    ) AS `materiais_vendidos`
                FROM cooperativas
                INNER JOIN
                    usuarios ON usuarios.id_usuario = cooperativas.id_usuario
                LEFT JOIN
                    vendas ON vendas.id_cooperativa = cooperativas.id_cooperativa
                LEFT JOIN
                    vendas_itens ON vendas_itens.id_venda = vendas.id_venda  
                LEFT JOIN materiais_catalogo
                    ON materiais_catalogo.id_material_catalogo = vendas_itens.id_material_catalogo
                GROUP BY
                    cooperativas.id_cooperativa;
                """

            )

            return cursor.fetchall()

        except Exception as e:

            print(f'Erro - Cooperativa "get_all": {e}')

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
                senha,
                tipo='cooperado'

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

    def alterar_aprovacao (self, id_cooperativa:int, aprovado:bool) -> bool:
        
        """
        Altera o estado de aprovação da
        cooperativa, variando entre True or False
        """

        #region Exceções

        if not isinstance(id_cooperativa, int):

            raise TypeError ('Cooperativa - "id_cooperativa" deve ser do tipo Int')
        
        if not isinstance(aprovado, bool):

            raise TypeError ('Cooperativa - "aprovado" deve ser do tipo Booleano')

        #endregion

        cursor = self.connection_db.cursor()

        try:

            cursor.execute (

                """
                UPDATE cooperativas
                SET cooperativas.aprovado = %s
                WHERE cooperativas.id_cooperativa = %s;
                """,

                (aprovado, id_cooperativa)

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
        id_usuario: int, 
        cnpj: str, 
        razao_social: str,
        nome_fantasia: str,
        email: str,
        telefone: str,
        endereco: str, 
        cidade: str, 
        estado: str
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

            # Insere a nova cooperativa com todos os campos
            
            cursor.execute (
                """
                INSERT INTO cooperativas 
                    (id_usuario, cnpj, razao_social, nome_fantasia, email, telefone, endereco, cidade, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    id_usuario, 
                    cnpj,
                    razao_social,
                    nome_fantasia,
                    email,
                    telefone,
                    endereco,
                    cidade,
                    estado
                )
            )

            # Retorna o ID da cooperativa que acabou de ser inserida
            return cursor.lastrowid

        except Exception as e:
            print(f'Erro - Cooperativa "create": {e}')
            return False # Retorna False (Erro)
        
        finally:
            cursor.close()

    def adicionar_documento (self, id_cooperativa: int, arquivo_url: str) -> int | bool:
        """
        Insere um novo documento comprovativo para a cooperativa
        """

        cursor = self.connection_db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO documentos_cooperativa (id_cooperativa, arquivo_url, status)
                VALUES (%s, %s, 'pendente');
                """,
                (id_cooperativa, arquivo_url)
            )
            
            return cursor.lastrowid
        
        except Exception as e:
            print(f'Erro - Cooperativa "adicionar_documento": {e}')
            return
        
        finally:
            cursor.close