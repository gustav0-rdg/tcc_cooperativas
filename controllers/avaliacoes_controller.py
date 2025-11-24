from data.connection_controller import Connection
from mysql.connector.connection import MySQLConnection
import datetime
from typing import List, Dict, Any, Optional
from controllers.config_controller import ConfigController # Importar ConfigController
import math # Para funções matemáticas como exp

class Avaliacoes:
    def __init__(self, connection_db: MySQLConnection):
        if not Connection.validar(connection_db):
            raise ValueError(f'Erro - Avaliacoes: valores inválidos para os parametros "connection_db"')
        self.connection_db = connection_db
        self.config_controller = ConfigController(connection_db) # Instanciar ConfigController

    def _calcular_score_bayesiano(self, id_comprador: int, cursor) -> float:
        """
        Calcula o score bayesiano de um comprador com base nas avaliações existentes e configurações do sistema.
        """
        # Obter configurações do sistema
        peso_prior_bayesiano = self.config_controller.get_config_value('peso_prior_bayesiano') or 3.0
        avaliacao_neutra_novato = self.config_controller.get_config_value('avaliacao_neutra_novato') or 2.5
        decaimento_anual_score = self.config_controller.get_config_value('decaimento_anual_score') or 365
        min_avaliacoes_confianca = self.config_controller.get_config_value('min_avaliacoes_confianca') or 10

        # Obter todas as avaliações do comprador com suas datas
        query_avaliacoes = "SELECT score, data_avaliacao FROM avaliacoes_compradores WHERE id_comprador = %s ORDER BY data_avaliacao ASC"
        cursor.execute(query_avaliacoes, (id_comprador,))
        avaliacoes = cursor.fetchall()

        if not avaliacoes:
            return avaliacao_neutra_novato # Retorna o score neutro se não houver avaliações

        # Parâmetros iniciais para o cálculo bayesiano
        total_score_ponderado = peso_prior_bayesiano * avaliacao_neutra_novato
        total_peso = peso_prior_bayesiano

        data_atual = datetime.datetime.now()

        for avaliacao in avaliacoes:
            score_avaliacao = avaliacao['score']
            data_avaliacao = avaliacao['data_avaliacao']
            
            # Calcular o fator de decaimento (exponencial)
            dias_desde_avaliacao = (data_atual - data_avaliacao).days
            
            # Usar uma função exponencial para o decaimento
            # A constante de decaimento (lambda) é calculada de forma que em 'decaimento_anual_score' dias
            # o peso caia para ~37% (1/e) do valor original.
            # lambda = 1 / decaimento_anual_score
            # peso_atual = exp(-lambda * dias_desde_avaliacao)
            if decaimento_anual_score > 0:
                fator_decaimento = math.exp(-dias_desde_avaliacao / decaimento_anual_score)
            else:
                fator_decaimento = 1.0 # Sem decaimento se o parâmetro for 0 ou negativo

            peso_avaliacao = 1.0 * fator_decaimento # Cada avaliação tem peso inicial de 1, decaindo com o tempo

            total_score_ponderado += score_avaliacao * peso_avaliacao
            total_peso += peso_avaliacao
        
        # Calcular o score bayesiano final
        if total_peso > 0:
            score_final = total_score_ponderado / total_peso
        else:
            score_final = avaliacao_neutra_novato # Fallback

        # Garantir que o score esteja entre 0 e 5
        return round(max(0.0, min(5.0, score_final)), 2)

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

    def inserir_avaliacao_pendente(self, id_venda: int, id_cooperativa: int) -> Optional[int]:
        """
        Insere uma avaliação pendente para uma venda específica e retorna o ID da avaliação pendente.
        Esta função NÃO gerencia a transação (commit/rollback). Isso deve ser feito pelo chamador.

        Args:
            id_venda (int): ID da venda.
            id_cooperativa (int): ID da cooperativa.

        Returns:
            Optional[int]: O ID da avaliação pendente inserida, ou None se a inserção falhar.
        
        Raises:
            Exception: Em caso de erro de banco de dados, a exceção será propagada.
        """
        with self.connection_db.cursor() as cursor:
            query = """
            INSERT INTO avaliacoes_pendentes (id_venda, id_cooperativa, status_avaliacao, data_criacao)
            VALUES (%s, %s, 'pendente', %s);
            """
            cursor.execute(query, (id_venda, id_cooperativa, datetime.datetime.now()))
            if cursor.rowcount > 0:
                return cursor.lastrowid
            return None

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

                # 4. Atualizar o contador de avaliações do comprador
                query_update_num_avaliacoes = "UPDATE compradores SET numero_avaliacoes = numero_avaliacoes + 1 WHERE id_comprador = %s"
                cursor.execute(query_update_num_avaliacoes, (dados_venda['id_comprador'],))

                # 5. Calcular e atualizar o score bayesiano do comprador
                novo_score_bayesiano = self._calcular_score_bayesiano(dados_venda['id_comprador'], cursor)
                query_update_score = "UPDATE compradores SET score_confianca = %s WHERE id_comprador = %s"
                cursor.execute(query_update_score, (novo_score_bayesiano, dados_venda['id_comprador']))

                # 6. Registrar o histórico do score
                query_historico_score = """
                INSERT INTO historico_score (id_comprador, score_calculado, numero_avaliacoes, detalhe_json, data_calculo)
                VALUES (%s, %s, (SELECT numero_avaliacoes FROM compradores WHERE id_comprador = %s), NULL, NOW())
                """
                cursor.execute(query_historico_score, (dados_venda['id_comprador'], novo_score_bayesiano, dados_venda['id_comprador']))

                # 7. Remover da tabela de pendentes
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

    def remover_avaliacao_pendente(self, id_avaliacao_pendente: int) -> bool:
        """
        Remove uma avaliação pendente da tabela `avaliacoes_pendentes`.

        Args:
            id_avaliacao_pendente (int): O ID da avaliação pendente a ser removida.

        Returns:
            bool: True se a avaliação pendente foi removida com sucesso, False caso contrário.
        """
        try:
            with self.connection_db.cursor() as cursor:
                query = "DELETE FROM avaliacoes_pendentes WHERE id_avaliacao_pendente = %s"
                cursor.execute(query, (id_avaliacao_pendente,))
                self.connection_db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao remover avaliação pendente: {e}")
            self.connection_db.rollback()
            return False
