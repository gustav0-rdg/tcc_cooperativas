from flask import Blueprint, request, jsonify
from controllers.tokens_controller import Tokens
from data.connection_controller import Connection
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa
from controllers.cnpj_controller import CNPJ

api_cooperativas = Blueprint(
    
    'api_cooperativas', 
    __name__, 

    url_prefix='/api/cooperativas'
    
)

CNAES_PERMITIDOS = [3811400, 3831901, 3831999, 3832700, 3812200]
NATUREZAS_JURIDICAS_PERMITIDAS = [2143, 3999] 

@api_cooperativas.route('/cadastrar', methods=['POST'])
def cadastrar ():

    conn = None

    try:

        data_cadastro = request.get_json()
        campos_obrigatorios = ['nome', 'email', 'senha', 'cnpj']

        # 400 - Campos obrigatórios incompletos

        if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
            return jsonify({ 'error': f'Dados de cadastro inválidos, todos os campos são obrigatórios: {campos_obrigatorios}' }), 400

        # 400 - Senha com menos de 8 caractéres

        if len(data_cadastro['senha']) < 8:
            return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
        
        # 400 - CNPJ Inválido

        if CNPJ.validar(data_cadastro['cnpj']):
            return jsonify({ 'error': 'CNPJ inválido. Revise e tente novamente' }), 400

        dados_cnpj = CNPJ.consultar(data_cadastro['cnpj'])

        # 503 - Erro ao consultar CNPJ (CNPJá)

        if not dados_cnpj:
            return jsonify({'error': 'Não foi possível consultar o CNPJ. Tente novamente mais tarde.'}), 503
        
        #region Verificação de Natureza Jurídica

        natureza_cooperativa = dados_cnpj.get('company', {}).get('nature', {}).get('id')

        # 400 - Código de Natureza Jurídica Inválido

        if not natureza_cooperativa in NATUREZAS_JURIDICAS_PERMITIDAS:
            return jsonify({'error': 'O CNPJ informado não pertence a uma Cooperativa ou Associação.'}), 400
        
        #endregion

        #region Verificação de CNAE

        cnae_principal_id = dados_cnpj.get('mainActivity', {}).get('id')
        cnaes_secundarios_ids = [act.get('id') for act in dados_cnpj.get('sideActivities', [])]

        cnae_valido = False

        if cnae_principal_id in CNAES_PERMITIDOS:
            cnae_valido = True

        else:

            for cnae_sec_id in cnaes_secundarios_ids:

                if cnae_sec_id in CNAES_PERMITIDOS:
                    cnae_valido = True
                    break

        # 400 - CNAE Inválido

        if not cnae_valido:
            return jsonify({'error': 'O CNPJ informado não possui CNAE compatível com cooperativas de reciclagem.'}), 400

        #endregion

        id_status_atividade_cooperativa = dados_cnpj.get('status', {}).get('id')

        # IDS de Status:
        #
        # 1 = Nulo
        # 2 = Ativa
        # 3 = Suspensa
        # 4 = Inapta
        # 8 = Baixada

        # 400 - CNPJ Inativo

        if id_status_atividade_cooperativa != 2:
            return jsonify({'error': 'O CNPJ informado está inativo.'}), 400

        conn = Connection('online')

        conn.connection_db.start_transaction()
        print("Transação iniciada")

        id_usuario_criado = Usuarios(conn.connection_db).create(

            nome=data_cadastro['nome'],
            email=data_cadastro['email'],
            senha=data_cadastro['senha'],
            tipo='cooperativa'

        )

        match id_usuario_criado:

            # 409 - Email já cadastrado

            case None:
                return jsonify({'error': 'Este email já está cadastrado.'}), 409
            
            # Usuário da cooperativa criado

            case _ if isinstance(id_usuario_criado, int):

                addr = dados_cnpj.get('address', {})
                endereco_completo = f"{addr.get('street', '')}, {addr.get('number', '')} {addr.get('details', '')} - {addr.get('district', '')}"

                id_cooperativa_criada = Cooperativa(conn.connection_db).create(

                    id_usuario=id_usuario_criado,
                    cnpj=data_cadastro['cnpj'],
                    razao_social=dados_cnpj.get('company', {}).get('name', 'Razão Social não encontrada'),
                    endereco=endereco_completo.strip(" ,-"),
                    cidade=addr.get('city'),
                    estado=addr.get('state')
                    # Latitude e longitude (não essencial por agora)

                )

                match id_cooperativa_criada:

                    # 409 - CNPJ já cadastrado

                    case None:
                        return jsonify({'error': 'Este CNPJ já está cadastrado.'}), 409

                    # 201 - Cooperativa criada pendente e aguardando aprovação

                    case _ if isinstance(id_cooperativa_criada, int):
                        return jsonify({'texto': 'Cadastro realizado com sucesso! Sua conta está pendente e está aguardando aprovação.'}), 201

                    # 500 - Erro Interno

                    case False | _:
                        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500

            # 500 - Erro Interno

            case False | _:
                return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    except Exception as e:

        if conn and conn.connection_db.is_connected():

            try:

                if conn.connection_db.in_transaction():
                    conn.connection_db.rollback()

            except Exception as rollback_err:

                print(f"Erro durante o rollback: {rollback_err}")

        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    finally:

        if conn:
            conn.close()

@api_cooperativas.route('/get/<identificador>', methods=['POST'])
def get (identificador:int|str):

    if identificador.isdigit():
        identificador = int(identificador)

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection()

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        dados_cooperativa = Cooperativa(conn.connection_db).get(identificador)

        match dados_cooperativa:

            # 200 - Cooperativa consultada com sucesso

            case _ if isinstance(dados_cooperativa, dict):
        
                return jsonify({ 'dados_cooperativa': dados_cooperativa }), 200

            # 500 - Erro ao consultar cooperativa

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/get-all', methods=['POST'])
def get_all ():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        dados_cooperativas = Cooperativa(conn.connection_db).get_all()

        match dados_cooperativas:

            # 200 - Todas as cooperativas foram consultadas com sucesso

            case _ if isinstance(dados_cooperativas, list):
        
                return jsonify({ 'dados_cooperativas': dados_cooperativas }), 200

            # 500 - Erro ao consultar cooperativas

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/alterar-aprovacao/<id_cooperativa>', methods=['POST'])
def alterar_aprovacao (id_cooperativa:int):

    if not id_cooperativa.isdigit():
        return jsonify({ 'error': '"id_cooperativa" é inválido' }), 400
    
    id_cooperativa = int(id_cooperativa)

    aprovacao = request.get_json().get('aprovacao')

    if not aprovacao or not isinstance(aprovacao, bool):
        return jsonify({ 'error': '"aprovacao" deve ser do tipo Booleano' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é parâmetro obrigatório' }), 400

    conn = Connection()

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] in ['gestor', 'root']:
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        match Cooperativa(conn.connection_db).alterar_aprovacao(id_cooperativa, aprovacao):

            # 404 - Cooperativa não encontrada

            case None:
                return jsonify({ 'error': 'Cooperativa não encontrado' }), 404

            # 200 - Aprovação alterada

            case True:
                return jsonify({ 'texto': 'Aprovação da cooperativa alterada' }), 200

            # 500 - Erro ao alterar a aprovação da cooperativa

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_cooperativas.route('/vincular-cooperado', methods=['POST'])
def vincular_cooperado ():

    data_cooperado = request.get_json()

    if not data_cooperado or not all(key in data_cooperado for key in ['nome', 'email', 'senha', 'cpf', 'telefone', 'endereco', 'cidade', 'estado']):
        
        return jsonify({ 'error': 'Dados de cadastro inválidos, todos os campos são obrigatórios: nome, senha, email, cpf, telefone, endereco, cidade e estado' }), 400
    
    if len(data_cooperado['senha']) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        # Token Inválido

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" inválido' }), 400

        data_adm_cooperativa = Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])

        # Autor da requisição inválido

        if not data_adm_cooperativa or data_adm_cooperativa['tipo'] != 'cooperativa':
            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
        
        data_cooperativa = Cooperativa(conn.connection_db).get(data_adm_cooperativa['id_usuario'])

        id_cooperado = Cooperativa(conn.connection_db).vincular_cooperado(

            data_cooperativa['id_cooperativa'],

            data_cooperado['nome'],
            data_cooperado['email'],
            data_cooperado['senha'],
            
            data_cooperado['cpf'],
            data_cooperado['telefone'],
            data_cooperado['endereco'],
            data_cooperado['cidade'],
            data_cooperado['estado']

        )

        match id_cooperado:

            # 409 - Email já cadastrado

            case None:
                return jsonify({ 'error': 'Email já cadastrado' }), 409

            # 200 - Usuário cooperado vinculado

            case _ if isinstance(id_cooperado, int):
                
                return jsonify({ 'texto': 'Cooperado vinculado' }), 200

            # 500 - Erro ao vincular usuário cooperado

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()