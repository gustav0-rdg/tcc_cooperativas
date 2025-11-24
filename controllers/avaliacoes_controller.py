from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
import datetime
from typing import List, Dict, Any, Optional

class Avaliacoes:
    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Avaliacoes: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db

    def get_avaliacoes_pendentes(self, id_cooperativa: int) -> List[Dict[str, Any]]:
        """
        Busca todas as avaliações pendentes para uma cooperativa específica, utilizando a view otimizada.

        Args:
            id_cooperativa (int): ID da cooperativa.

        Returns:
            list: Lista de dicionários com as avaliações pendentes.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT
                    id_avaliacao_pendente, id_venda, data_venda, valor_total,
                    quantidade_total_kg, materiais_vendidos, comprador_nome,
                    comprador_cnpj, score_confianca, comprador_cidade,
                    comprador_estado, comprador_telefone, comprador_email
                FROM v_avaliacoes_pendentes_detalhadas
                WHERE id_cooperativa = %s
                ORDER BY data_venda DESC;
                """
                cursor.execute(query, (id_cooperativa,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Erro em get_avaliacoes_pendentes: {e}")
            return []

    def inserir_avaliacao_pendente(self, id_venda: int, id_cooperativa: int) -> bool:
        """
        Insere uma avaliação pendente para uma venda específica.

        Args:
            id_venda (int): ID da venda.
            id_cooperativa (int): ID da cooperativa.

        Returns:
            bool: True se inserido com sucesso, False caso contrário.
        """
        try:
            with self.connection_db.cursor() as cursor:
                query = """
                INSERT INTO avaliacoes_pendentes (id_venda, id_cooperativa, status_avaliacao, data_criacao)
                VALUES (%s, %s, 'pendente', %s);
                """
                cursor.execute(query, (id_venda, id_cooperativa, datetime.datetime.now()))
                self.connection_db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro em inserir_avaliacao_pendente: {e}")
            self.connection_db.rollback()
            return False

    def _get_feedback_tag_ids(self, cursor, tags_recebidas: List[Any]) -> List[int]:
        """
        Método auxiliar para converter uma lista de nomes de tags ou IDs em uma lista de IDs de inteiros.
        """
        if not tags_recebidas:
            return []

        # Se o primeiro item for um inteiro, assume-se que todos são IDs.
        if isinstance(tags_recebidas[0], int):
            return tags_recebidas

        # Se forem strings, busca os IDs no banco.
        if isinstance(tags_recebidas[0], str):
            placeholders = ', '.join(['%s'] * len(tags_recebidas))
            query_busca_id = f"SELECT id_feedback_tag FROM feedback_tags WHERE texto IN ({placeholders})"
            cursor.execute(query_busca_id, tuple(tags_recebidas))
            resultados = cursor.fetchall()
            
            if len(resultados) != len(tags_recebidas):
                print(f"AVISO: Algumas tags não foram encontradas. Recebidas: {tags_recebidas}, Encontradas: {resultados}")

            return [item['id_feedback_tag'] for item in resultados]
        
        return []

    def finalizar_avaliacao_pendente(self, id_avaliacao_pendente: int, dados_avaliacao: dict) -> bool:
        """
        Finaliza uma avaliação pendente.
        Esta operação é transacional: insere na tabela de avaliações, associa as tags de feedback
        e remove o registro da tabela de pendentes. Se qualquer passo falhar, tudo é revertido.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                # 1. Buscar dados da venda associada à avaliação pendente
                query_dados = """
                SELECT ap.id_venda, ap.id_cooperativa, v.id_comprador
                FROM avaliacoes_pendentes ap
                JOIN vendas v ON ap.id_venda = v.id_venda
                WHERE ap.id_avaliacao_pendente = %s
                """
                cursor.execute(query_dados, (id_avaliacao_pendente,))
                dados_venda = cursor.fetchone()
                
                if not dados_venda:
                    print(f"Aviso: Avaliação pendente com ID {id_avaliacao_pendente} não encontrada.")
                    return False

                # 2. Inserir na tabela principal de avaliações
                score = int(dados_avaliacao.get('nota', 0))
                if not (0 <= score <= 5):
                    raise ValueError("O score da avaliação deve estar entre 0 e 5.")

                query_avaliacao = """
                INSERT INTO avaliacoes_compradores (id_venda, id_comprador, id_cooperativa, score, comentario_livre, data_avaliacao)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(query_avaliacao, (
                    dados_venda['id_venda'], dados_venda['id_comprador'], dados_venda['id_cooperativa'],
                    score, dados_avaliacao.get('analise', '')
                ))
                id_avaliacao = cursor.lastrowid

                # 3. Processar e inserir tags de feedback
                tags_recebidas = dados_avaliacao.get('comentarios_rapidos', [])
                if tags_recebidas:
                    ids_tags_para_inserir = self._get_feedback_tag_ids(cursor, tags_recebidas)
                    
                    if ids_tags_para_inserir:
                        query_insert_relacao = "INSERT INTO avaliacao_feedback_selecionado (id_avaliacao, id_feedback_tag) VALUES (%s, %s)"
                        tags_para_inserir_tuplas = [(id_avaliacao, tag_id) for tag_id in ids_tags_para_inserir]
                        cursor.executemany(query_insert_relacao, tags_para_inserir_tuplas)

                # 4. Remover da tabela de pendentes
                cursor.execute("DELETE FROM avaliacoes_pendentes WHERE id_avaliacao_pendente = %s", (id_avaliacao_pendente,))

                self.connection_db.commit()
                return True

        except Exception as e:
            print(f"Erro em finalizar_avaliacao_pendente: {e}")
            self.connection_db.rollback()
            return False

    def get_avaliacao_pendente_por_id(self, id_avaliacao_pendente: int) -> Optional[Dict[str, Any]]:
        """
        Busca uma avaliação pendente específica por ID, utilizando a view otimizada.

        Args:
            id_avaliacao_pendente (int): ID da avaliação pendente.

        Returns:
            dict | None: Dados da avaliação pendente ou None se não encontrada.
        """
        try:
            with self.connection_db.cursor(dictionary=True) as cursor:
                query = """
                SELECT
                    id_avaliacao_pendente, id_venda, data_venda, valor_total,
                    quantidade_total_kg, materiais_vendidos, comprador_nome,
                    comprador_cnpj, score_confianca, comprador_cidade,
                    comprador_estado, comprador_telefone, comprador_email
                FROM v_avaliacoes_pendentes_detalhadas
                WHERE id_avaliacao_pendente = %s;
                """
                cursor.execute(query, (id_avaliacao_pendente,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Erro em get_avaliacao_pendente_por_id: {e}")
            return None
