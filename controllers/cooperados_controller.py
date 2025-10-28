from mysql.connector.connection import MySQLConnection
from data.connection_controller import Connection
from typing import Optional, Dict, Any, List
from datetime import datetime

from usuarios_controller import Usuarios 

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
        
        tipo_usuario = 'catador'
        status_usuario = 'ativo'
        
        try:
            senha_hash = Usuarios.criptografar(senha)
        except Exception as e_crypto:
            print(f"Erro ao criptografar senha: {e_crypto}")
            return None
        
        try:
            self.connection_db.start_transaction()

            query_usuario = """
            INSERT INTO usuarios (nome, email, senha_hash, tipo, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_usuario, (nome, email, senha_hash, tipo_usuario, status_usuario))
            
            id_usuario_criado = cursor.lastrowid
            
            if not id_usuario_criado:
                raise Exception("Falha ao obter o ID do usuário criado.")

            query_catador = """
            INSERT INTO catadores (id_usuario, id_cooperativa, cpf, telefone, 
                                   endereco, cidade, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_catador, (
                id_usuario_criado, id_cooperativa, cpf, telefone,
                endereco, cidade, estado
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
                cat.*, 
                u.nome, 
                u.email, 
                u.status
            FROM catadores cat
            JOIN usuarios u ON cat.id_usuario = u.id_usuario
            WHERE cat.id_catador = %s
            """
            cursor.execute(query, (id_catador,))
            resultado = cursor.fetchone()
            
            self.connection_db.commit() 
            
            return resultado
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_id_catador': {e}")
            
            self.connection_db.rollback() 
            
            return None
        
        finally:
            cursor.close()

    def get_by_id_usuario(self, id_usuario: int) -> Optional[Dict[str, Any]]:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                cat.*, 
                u.nome, 
                u.email, 
                u.status
            FROM catadores cat
            JOIN usuarios u ON cat.id_usuario = u.id_usuario
            WHERE cat.id_usuario = %s
            """
            cursor.execute(query, (id_usuario,))
            resultado = cursor.fetchone()
            
            self.connection_db.commit()
            
            return resultado
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_id_usuario': {e}")
            
            self.connection_db.rollback()
            
            return None
        
        finally:
            cursor.close()

    def get_by_cooperativa(self, id_cooperativa: int, apenas_ativos: bool = True) -> List[Dict[str, Any]]:
        cursor = self.connection_db.cursor(dictionary=True)
        try:
            params = [id_cooperativa]
            query = """
            SELECT 
                cat.id_catador, cat.id_usuario, cat.cpf, cat.telefone, 
                cat.cidade, cat.ativo, cat.data_vinculo,
                u.nome, u.email
            FROM catadores cat
            JOIN usuarios u ON cat.id_usuario = u.id_usuario
            WHERE cat.id_cooperativa = %s
            """
            
            if apenas_ativos:
                query += " AND cat.ativo = TRUE"
            
            query += " ORDER BY u.nome ASC"

            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            
            self.connection_db.commit()
            
            return resultados
        
        except Exception as e:
            print(f"Erro - Catadores 'get_by_cooperativa': {e}")
            
            self.connection_db.rollback()
            
            return []
        
        finally:
            cursor.close()
            
    def update_perfil(
        self, 
        id_catador: int,
        telefone: Optional[str] = None,
        endereco: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None
    ) -> bool:
        cursor = self.connection_db.cursor()
        
        updates = []
        params = []
        
        if telefone is not None:
            updates.append("telefone = %s")
            params.append(telefone)
        if endereco is not None:
            updates.append("endereco = %s")
            params.append(endereco)
        if cidade is not None:
            updates.append("cidade = %s")
            params.append(cidade)
        if estado is not None:
            updates.append("estado = %s")
            params.append(estado)

        if not updates:
            print("Aviso - Catadores 'update_perfil': Nenhum dado fornecido para atualização.")
            return True 

        try:
            query = f"UPDATE catadores SET {', '.join(updates)} WHERE id_catador = %s"
            params.append(id_catador)
            
            cursor.execute(query, tuple(params))
            self.connection_db.commit()
            
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Erro - Catadores 'update_perfil': {e}")
            self.connection_db.rollback()
            return False
        
        finally:
            cursor.close()

    def _set_status_catador(self, id_catador: int, novo_status: bool) -> bool:
        cursor = self.connection_db.cursor(dictionary=True)
        
        status_usuario = 'ativo' if novo_status else 'inativo'
        data_desvinculo = None if novo_status else datetime.now() 
        
        try:
            self.connection_db.start_transaction() 

            cursor.execute("SELECT id_usuario FROM catadores WHERE id_catador = %s", (id_catador,))
            catador_data = cursor.fetchone()
            
            if not catador_data:
                print(f"Erro: Catador {id_catador} não encontrado.")
                self.connection_db.rollback() 
                return False
                
            id_usuario = catador_data['id_usuario']

            query_catador = """
            UPDATE catadores
            SET ativo = %s, data_desvinculo = %s
            WHERE id_catador = %s
            """
            cursor.execute(query_catador, (novo_status, data_desvinculo, id_catador))

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

    def desativar(self, id_catador: int) -> bool:
        print(f"Tentando desativar catador {id_catador}...")
        return self._set_status_catador(id_catador, novo_status=False)

    def reativar(self, id_catador: int) -> bool:
        print(f"Tentando reativar catador {id_catador}...")
        return self._set_status_catador(id_catador, novo_status=True)