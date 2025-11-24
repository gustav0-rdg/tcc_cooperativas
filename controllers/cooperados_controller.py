from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection
from typing import Optional, Dict, Any, List
from datetime import datetime

from controllers.usuarios_controller import Usuarios
class Catadores:

    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError("Erro - Catadores: Conexão com o banco de dados inválida.")
        
        self.connection_db = connection_db

    def create(
        self,
        nome: str,
        email: str,
        senha: str,
        
        id_cooperativa: int,
        cpf: str,
        telefone: Optional[str] = None,
        endereco: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None
    ) -> Optional[int]:
        
        cursor = self.connection_db.cursor()
        
        tipo_usuario = 'cooperado'
        
        try:
            senha_hash = Usuarios.criptografar(senha)
        except Exception as e_crypto:
            print(f"Erro ao criptografar senha: {e_crypto}")
            return None
        
        try:
            self.connection_db.start_transaction()

            query_usuario = """
            INSERT INTO usuarios (nome, email, senha_hash, tipo, status)
            VALUES (%s, %s, %s, %s, 'ativo')
            """
            cursor.execute(query_usuario, (nome, email, senha_hash, tipo_usuario))
            
            id_usuario_criado = cursor.lastrowid
            
            if not id_usuario_criado:
                raise Exception("Falha ao obter o ID do usuário criado.")

            query_catador = """
            INSERT INTO cooperados (id_usuario, id_cooperativa, cpf)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query_catador, (
                id_usuario_criado, id_cooperativa, cpf
            ))
            
            id_catador_criado = cursor.lastrowid
            
            if not id_catador_criado:
                raise Exception("Falha ao obter o ID do catador criado.")

            self.connection_db.commit()
            
            print(f"Sucesso: Catador {id_catador_criado} e Usuário {id_usuario_criado} criados.")
            return id_catador_criado

        except Exception as e:
            print(f"Erro - Catadores 'create': {e}")
            self.connection_db.rollback()
            return None
        
        finally:
            cursor.close()

    def get_by_id_catador(self, id_catador: int) -> Optional[Dict[str, Any]]:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = """
            SELECT
                id_cooperado,
                id_usuario,
                cpf,
                telefone,
                endereco,
                cidade,
                estado,
                data_vinculo,
                deletado_em,
                id_cooperativa,
                cooperativa_nome,
                usuario_nome AS nome,
                usuario_email AS email,
                usuario_status AS status
            FROM v_cooperados_detalhados
            WHERE id_cooperado = %s
            """
            cursor.execute(query, (id_catador,))
            resultado = cursor.fetchone()
            
            return resultado
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_id_catador': {e}")
            
            return None
        
        finally:
            cursor.close()

    def get_by_id_usuario(self, id_usuario: int) -> Optional[Dict[str, Any]]:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = """
            SELECT
                id_cooperado,
                id_usuario,
                cpf,
                telefone,
                endereco,
                cidade,
                estado,
                data_vinculo,
                deletado_em,
                id_cooperativa,
                cooperativa_nome,
                usuario_nome AS nome,
                usuario_email AS email,
                usuario_status AS status
            FROM v_cooperados_detalhados
            WHERE id_usuario = %s
            """
            cursor.execute(query, (id_usuario,))
            resultado = cursor.fetchone()
            
            return resultado
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_id_usuario': {e}")
            
            return None
        
        finally:
            cursor.close()

    def get_by_cooperativa(self, id_cooperativa: int, apenas_ativos: bool = True) -> List[Dict[str, Any]]:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            params = [id_cooperativa]
            query = """
            SELECT
                id_cooperado,
                id_usuario,
                cpf,
                data_vinculo,
                usuario_nome AS nome,
                usuario_email AS email
            FROM v_cooperados_detalhados
            WHERE id_cooperativa = %s
            """
            
            if apenas_ativos:
                query += " AND deletado_em IS NULL"
            
            query += " ORDER BY nome ASC"

            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            
            return resultados
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_cooperativa': {e}")
            
            return []
        
        finally:
            cursor.close()
            
    def update_perfil(
        self, 
        id_cooperado: int,
        telefone: Optional[str] = None
    ) -> bool:
        cursor = self.connection_db.cursor()
        
        updates = []
        params = []
        
        if telefone is not None:
            updates.append("telefone = %s")
            params.append(telefone)

        if not updates:
            print("Aviso - Catadores 'update_perfil': Nenhum dado fornecido for atualização.")
            return True 

        try:
            query = f"UPDATE cooperados SET {', '.join(updates)} WHERE id_cooperado = %s"
            params.append(id_cooperado)
            
            cursor.execute(query, tuple(params))
            self.connection_db.commit()
            
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Erro - Catadores 'update_perfil': {e}")
            self.connection_db.rollback()
            return False
        
        finally:
            cursor.close()

    def _set_status_catador(self, id_cooperado: int, novo_status: bool) -> bool:
        cursor = self.connection_db.cursor(dictionary=True)
        
        status_usuario = 'ativo' if novo_status else 'inativo'
        data_desvinculo = None if novo_status else datetime.now() 
        
        try:
            self.connection_db.start_transaction() 

            cursor.execute("SELECT id_usuario FROM cooperados WHERE id_cooperado = %s", (id_cooperado,))
            catador_data = cursor.fetchone()
            
            if not catador_data:
                print(f"Erro: Cooperado {id_cooperado} não encontrado.")
                self.connection_db.rollback() 
                return False
                
            id_usuario = catador_data['id_usuario']

            query_catador = """
            UPDATE cooperados
            SET data_desvinculo = %s
            WHERE id_cooperado = %s
            """
            cursor.execute(query_catador, (data_desvinculo, id_cooperado))

            query_usuario = "UPDATE usuarios SET status = %s WHERE id_usuario = %s"
            cursor.execute(query_usuario, (status_usuario, id_usuario))

            self.connection_db.commit()
            return True

        except Exception as e:
            print(f"Erro - Catadores '_set_status_catador': {e}")
            self.connection_db.rollback()
            return False
        
        finally:
            cursor.close()

    def desativar(self, id_cooperado: int) -> bool:
        print(f"Tentando desativar cooperado {id_cooperado}...")
        return self._set_status_catador(id_cooperado, novo_status=False)

    def reativar(self, id_cooperado: int) -> bool:
        print(f"Tentando reativar cooperado {id_cooperado}...")
        return self._set_status_catador(id_cooperado, novo_status=True)
    


    def search_cooperado(self, id_cooperativa, nome_cooperado):
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                termo_buscado = f"%{nome_cooperado}%"
                query = """
                    SELECT
                        id_usuario,
                        id_cooperado,
                        cpf,
                        data_vinculo,
                        usuario_nome AS nome
                    FROM v_cooperados_detalhados
                    WHERE id_cooperativa = %s AND usuario_nome LIKE %s;
                """
                cursor.execute(query, (id_cooperativa, termo_buscado))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(e)
            return []
        finally:
            cursor.close()
            
    def get_cooperado_e_cooperativa_by_user_id(self, id_usuario: int) -> Optional[dict]:
        """
        Busca um cooperado e o nome da sua cooperativa pelo id_usuario usando v_cooperados_detalhados.
        """
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM v_cooperados_detalhados WHERE id_usuario = %s;
            """, (id_usuario,))
            return cursor.fetchone()

        except Exception as e:
            print(f"Erro em 'get_cooperado_e_cooperativa_by_user_id': {e}")
            return None

        finally:
            cursor.close()

    def delete_cooperado(self, id_usuario: int, id_cooperado: int) -> bool:
        try:
            with self.connection_db.cursor() as cursor:
                print(id_cooperado, id_usuario)
                cursor.execute(
                    "DELETE FROM cooperados WHERE id_cooperado = %s;",
                    (id_cooperado,)
                )
                cursor.execute(
                    "DELETE FROM usuarios WHERE id_usuario = %s;",
                    (id_usuario,)
                )
            self.connection_db.commit()
            return True

        except Exception as e:
            self.connection_db.rollback() # Retornando os dados pro banco de dados caso algum erro aconteça
            print(f"Erro ao deletar cooperado/usuário: {e}")
            return False
