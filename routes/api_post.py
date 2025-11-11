from flask import redirect, Blueprint, request, jsonify
from controllers.comprador_controller import Compradores
from controllers.vendas_controller import Vendas
from data.connection_controller import Connection
from controllers.materiais_controller import Materiais
from controllers.tokens_controller import Tokens
from controllers.cooperados_controller import Catadores
from controllers.cooperativa_controller import Cooperativa
import json
import xml.etree.ElementTree as ET
import xmltodict
from html import escape

api_post = Blueprint('api_post', __name__, url_prefix="/post")

@api_post.route("/dados-xml", methods=["POST"])
def enviar_dados_com_xml():
    if 'meu_xml' not in request.files:
        return "Nenhum arquivo encontrado!", 400
    
    # Pega o objeto do arquivo enviado
    arquivo_xml = request.files['meu_xml']
    
    # Verifica se o nome do arquivo não está vazio
    if arquivo_xml.filename == '':
        return "Nenhum arquivo selecionado!", 400
    conn = Connection('local')
    try:
        conteudo_xml = arquivo_xml.read()
        dados_dict = xmltodict.parse(conteudo_xml, force_list=('det',))
        infNFe = dados_dict['nfeProc']['NFe']['infNFe']

        # Dados de quem emitiu a NF
        emit_nome = infNFe['emit']['xNome']
        emit_cnpj = infNFe['emit']['CNPJ']

        # Dados de quem é o destinatário
        dest_nome = infNFe['dest']['xNome']
        dest_cnpj = infNFe['dest']['CNPJ']

        # Dados do produto
        prod_infos = infNFe['det'][0]
        prod_nome = (prod_infos['prod']['xProd'])
        termos_categorias = prod_nome.split()
        prod_categoria = termos_categorias[0]
        prod_subcat = prod_infos['prod']['xProd']

        prod_peso = float(prod_infos['prod']['qCom'])
        prod_valor_unitario = float(prod_infos['prod']['vUnCom'])
        valor_total = float(prod_infos['prod']['vProd'])

        dados_frontend = {
            "cnpj": emit_cnpj,  # cooperativa
            "vendedor": {
                "cnpj": dest_cnpj  # comprador
            },
            "material": {
                "categoria": prod_categoria,
                "subtipo": prod_subcat
            },
            "quantidade": prod_peso,
            "preco_por_kg": prod_valor_unitario,
            "total": valor_total,
            "avaliacao": {
                "nota": 5,
                "analise": f"Avaliação automática: venda do produto {prod_nome}.",
                "comentarios_rapidos": ["Pagou adiantado"]
            }
        }

        
        vendas = Vendas(conn.connection_db).registrar_nova_venda(dados_frontend)
        if vendas:
            return jsonify({"mensagem": "Venda registrada com sucesso!"}), 200
        else:
            return jsonify({
                "erro": "Falha desconhecida ao registrar venda",
                "material_invalido": f"{prod_categoria} não existe",
                "nome_material_invalido": f"{prod_categoria
                                             }"}), 400

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400 

    except KeyError as e:
        return jsonify({"erro": f"Estrutura do XML inválida. Tag não encontrada: {e}"}), 400

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro inesperado: {e}"}), 500
    
    finally:
        conn.close()

@api_post.route("/dados-venda", methods=["POST"])
def postar_dados_de_venda():

    try:
        dados_recebidos = request.get_json()
        conn = Connection('local')
        processar_venda = Vendas(conn.connection_db).registrar_nova_venda(dados_recebidos["id_cooperativa"], dados_recebidos)
        return jsonify({"status": "sucesso", "mensagem": "Dados da venda recebidos!"}), 200
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()

@api_post.route("/dados-comprador", methods=["POST"])
def postar_dados_comprador():
    try:
        conn = Connection('local')
        dados_recebidos = request.get_json()
        Compradores(conn.connection_db).create(str(dados_recebidos))
        return({"status":"sucesso", "mensagem":"Dados do comprador recebidos"})
    except Exception as e:
        print(e)
    finally:
        conn.close()

# eu que fiz samuel corrija

@api_post.route("/cadastrar-sinonimo", methods=["POST"])
def registrar_sinonimo():
    data = request.get_json()

    nome_padrao = data.get('nome_padrao')
    sinonimo = data.get('sinonimo') 

    token = request.headers.get('Authorization')
    conn = Connection('local')
    try:
        if not token:
            return jsonify({ 'error': 'Para este tipo de ação é necessário token de autorização' }), 400
        data_token = Tokens(conn.connection_db).validar(token)
        user_info = Cooperativa(conn.connection_db).get_cooperativa_by_user_id(data_token['id_usuario'])

        if not user_info:
            return jsonify({'error':'Cooperativa não encontrada.'}),400

        if not all([nome_padrao, sinonimo]):
            return jsonify({'message': 'Faltam dados para registrar o sinônimo.'}), 400
                    
        resposta = Materiais(conn.connection_db).post_cadastrar_sinonimo(nome_padrao, sinonimo, user_info["id_cooperativa"])
    except Exception as e:
        print(e)
    
    finally:
        if conn:
            conn.close()
    return resposta

@api_post.route("/cadastrar-subtipo", methods=["POST"])
def cadastrar_subtipo():
    try:
        data = request.get_json()
        conn = Connection('local')
        resposta = Materiais(conn.connection_db).cadastrar_subtipo(data["nome_especifico"], data["id_material_base"])
        return resposta
    except Exception as e:
        print(e)
    finally:
        conn.close()

@api_post.route("/material/<identificador>", methods=["POST"])
def cadastrar_material(identificador):
    conn = Connection('local')
    token = request.headers.get('Authorization')
    data = request.get_json()
    try:
        if not token:
            return jsonify({'error':'token é obrigatório.'})
        data_token = Tokens(conn.connection_db).validar(token)
        user_info = Cooperativa(conn.connection_db).get_by_user_id(data_token['id_usuario']),400
        if not user_info:
            return jsonify({'error':'cooperativa não encontrada.'}),400
        resp = Materiais(conn.connection_db).cadastrar_subtipo_com_base(data["nome_padrao"], identificador)
        if resp:
            return jsonify({'sucess': f'produto cadastrado com sucesso. {data["nome_padrao"]}'})

    except Exception as e:
        print(e)

    finally:
        if conn:
            conn.close()