from flask import Blueprint, request, jsonify
from controllers.usuarios_controller import Usuarios
from controllers.cooperativa_controller import Cooperativa
from controllers.cnpj_controller import CNPJ
from data.connection_controller import Connection
from controllers.tokens_controller import Tokens
from datetime import datetime, timedelta

api_usuarios = Blueprint(
    
    'api_usuarios', 
    __name__, 

    url_prefix='/api/usuarios'
    
)

# CNAEs permitidos
CNAES_PERMITIDOS = [3811400, 3831901, 3831999, 3832700, 3812200]
NATUREZA_JURIDICA_COOPERATIVA = 2143 # Código para Cooperativa

@api_usuarios.route('/cadastrar', methods=['POST'])
def cadastrar ():
    conn = None

    try:
        data_cadastro = request.get_json()
        campos_obrigatorios = ['nome', 'email', 'senha', 'cnpj']

        # Validação dos dados
        if not data_cadastro or not all(key in data_cadastro for key in campos_obrigatorios):
            return jsonify({'error': f'Dados de cadastros inválidos. Campos obrigatórios: {", ".join(campos_obrigatorios)}'}),400

        if len(data_cadastro['senha']) < 8:
            return jsonify({'error': 'A senha deve ter no mínimo 8 caracteres'}), 400
        
        cnpj_limpo = ''.join(filter(str.isdigit, data_cadastro['cnpj']))
        if len(cnpj_limpo) != 14:
            ({'error': 'CNPJ inválido. Deve conter 14 dígitos'}), 400

        # Validação de negócio
        print(f"Consultando CNPJ: {cnpj_limpo}")
        dados_cnpj = CNPJ.consultar(cnpj_limpo)

        if not dados_cnpj:
            print("Erro: API CNPJ não retornou dados")
            return jsonify({'error': 'Não foi possível validar o CNPJ. Tente novamente mais tarde.'}), 503 # Código de serviço indisponível
        
        # Verificação de natureza
        natureza_id = dados_cnpj.get('company', {}).get('nature', {}).get('id')
        if natureza_id != NATUREZA_JURIDICA_COOPERATIVA:
            print(f"Natureza jurídica inválida: {natureza_id}")
            return jsonify({'error': 'O CNPJ informado não pertence a uma Cooperativa (Natureza Jurídica incorreta).'}), 400
        
        # Verificação de CNAE
        cnae_principal_id = dados_cnpj.get('company', {}).get('cnae', {}).get('id')
        cnaes_secundarios_ids = [act.get('id') for act in dados_cnpj.get('sideActivities', [])]

        cnae_valido = False
        if cnae_principal_id in CNAES_PERMITIDOS:
            cnae_valido = True
        else:
            for cnae_sec_id in cnaes_secundarios_ids:
                if cnae_sec_id in CNAES_PERMITIDOS:
                    cnae_valido = True
                    break

        if not cnae_valido:
            print(f"CNAE inválido. Principal: {cnae_principal_id}, Secundários: {cnaes_secundarios_ids}")
            return jsonify({'error': 'O CNPJ informado não possui CNAE compatível com cooperativas de reciclagem.'}), 400

        print("CNPJ validado com sucesso!")

        # Banco de dados
        conn = Connection('local')
        db = conn.connection_db
        usuarios_ctrl = Usuarios(db)
        cooperativa_ctrl = Cooperativa(db)

        id_usuario_criado = None
        id_cooperativa_criada = None

        db.start_transaction()
        print("Transação iniciada")

        id_usuario_criado = usuarios_ctrl.create(
            nome=data_cadastro['nome'],
            email=data_cadastro['email'],
            senha=data_cadastro['senha'],
            tipo='cooperativa' # Status já é dado como 'pendente' default
        )
        
        if not id_usuario_criado:
            # Verifica a natureza do erro
            cursor_check = db.cursor()
            cursor_check.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (data_cadastro['email'],))
            if cursor_check.fetchone():
                cursor_check.close()
                db.rollback()
                print("Rollback: Email duplicado.")
                return jsonify({'error': 'Este email já está cadastrado.'}), 409 # Conflict
            else:
                cursor_check.close()
                db.rollback()
                print("Rollback: Erro desconhecido ao criar usuário.")
                raise Exception("Falha ao criar usuário por motivo desconhecido") # Cai no except geral

        print(f"Usuário criado: {id_usuario_criado}")

        addr = dados_cnpj.get('address', {})
        endereco_completo = f"{addr.get('street', '')}, {addr.get('number', '')} {addr.get('details', '')} - {addr.get('district', '')}"

        id_cooperativa_criada = cooperativa_ctrl.create(
            id_usuario=id_usuario_criado,
            cnpj=cnpj_limpo,
            razao_social=dados_cnpj.get('company', {}).get('name', 'Razão Social não encontrada'),
            endereco=endereco_completo.strip(" ,-"),
            cidade=addr.get('city'),
            estado=addr.get('state')
            # Latitude e longitude (não essencial por agora)
        )

        if not id_cooperativa_criada:
            db.rollback()
            print("Rollback: Erro ao criar cooperativa (verificar logs do controller).")
             # Poderia ser CNPJ duplicado ou outro erro
            cursor_check = db.cursor()
            cursor_check.execute("SELECT id_cooperativa FROM cooperativas WHERE cnpj = %s", (cnpj_limpo,))
            if cursor_check.fetchone():
                 cursor_check.close()
                 return jsonify({'error': 'Este CNPJ já está cadastrado.'}), 409
            else:
                 cursor_check.close()
                 raise Exception("Falha ao criar cooperativa por motivo desconhecido") # Cai no except geral

        print(f"Cooperativa criada: {id_cooperativa_criada}")

        db.commit()
        print("Commit realizado.")
        return jsonify({'message': 'Cadastro realizado com sucesso! Sua conta está pendente e está aguardando aprovação.'}), 201
    
    except Exception as e:
        print(f"Erro GERAL na rota /cadastrar: {e}")
        if conn and conn.connection_db.is_connected():
            try:
                # Tenta fazer rollback
                if conn.connection_db.in_transaction():
                    print("Realizando rollback devido a erro...")
                    conn.connection_db.rollback()
            except Exception as rollback_err:
                print(f"Erro durante o rollback: {rollback_err}")

        return jsonify({'error': 'Ocorreu um erro interno no servidor durante o cadastro.'}), 500
    
    finally:
        if conn:
            conn.close()
            print("Conexão fechada")

@api_usuarios.route('/login', methods=['POST'])
def login ():

    data = request.get_json()

    email = data.get('email')
    if not email:
        return jsonify({ 'texto': '"email" é parâmetro obrigatório' }), 400
        
    senha = data.get('senha')
    if not senha:
        return jsonify({ 'texto': '"senha" é parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        autenticar_usuario = Usuarios(conn.connection_db).autenticar(email, senha)
        match autenticar_usuario:

            # 404 - Usuário não encontrado (Email ou Senha incorretos)

            case None:
                return jsonify({ 'error': 'Email ou senha incorretos' }), 404

            # 200 - Usuário autêntico

            case _ if isinstance(autenticar_usuario, int):

                return jsonify({ 
                    
                    'token': Tokens(conn.connection_db).create(

                        autenticar_usuario,
                        'sessao',

                        # Data de expiração em 30 dias
                        datetime.now() + timedelta(days=30)

                    )

                }), 200

            # 500 - Erro ao verificar a autenticidade do usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()
    
@api_usuarios.route('/alterar-senha', methods=['POST'])
def alterar_senha ():

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({ 'texto': '"token" é parâmetro obrigatório' }), 400

    data = request.get_json()
    nova_senha = data.get('nova-senha')

    if not nova_senha:
        return jsonify({ 'texto': '"nova-senha" é parâmetro obrigatório' }), 400
    
    if len(nova_senha) < 8:
        return jsonify({ 'texto': 'A senha deve ter no minímo 8 caractéres' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'recuperacao_senha':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        match Usuarios(conn.connection_db).trocar_senha(data_token['id_usuario']):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Senha do usuário alterada

            case True:

                Tokens(conn.connection_db).set_state(data_token['id_token'])
                return jsonify({ 'texto': 'Senha alterada com sucesso' }), 200

            # 500 - Erro ao alterar a senha do usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500

    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/delete', methods=['POST'])
@api_usuarios.route('/delete/<id_usuario>', methods=['POST'])
def delete (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)

        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Excluindo a conta de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403
            
        #endregion
        
        match Usuarios(conn.connection_db).delete(id_usuario):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Usuário Excluído

            case True:
                return jsonify({ 'texto': 'Usuário excluído' }), 200

            # 500 - Erro ao excluir usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/get', methods=['POST'])
@api_usuarios.route('/get/<id_usuario>', methods=['POST'])
def get_info (id_usuario:int=None):

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        
        if not data_token or data_token['tipo'] != 'sessao':
            return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
        
        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        #region Consultando info de terceiros

        if data_token['id_usuario'] != id_usuario and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] == 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        data_usuario = Usuarios(conn.connection_db).get_by_id(id_usuario)
        match data_usuario:

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Informações do usuário consultadas

            case _ if isinstance(data_usuario, dict):
                return jsonify({ 'data': data_usuario }), 200

            # 500 - Erro ao consultar as informações usuário

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()

@api_usuarios.route('/alterar-status', methods=['POST'])
@api_usuarios.route('/alterar-status/<id_usuario>', methods=['POST'])
def alterar_status (id_usuario:int=None):

    data = request.get_json()

    novo_status = data.get('novo-status')
    if not novo_status:
        return jsonify({ 'error': '"novo-status" é um parâmetro obrigatório' }), 400

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({ 'error': '"token" é um parâmetro obrigatório' }), 400
    
    conn = Connection('local')

    try:

        data_token = Tokens(conn.connection_db).validar(token)
        if not data_token:
            return jsonify({ 'error': 'Token inválido' }), 400

        if id_usuario != None:

            if not id_usuario.isdigit():
                return jsonify({ 'error': '"id_usuario" deve ser um Int' }), 400

            id_usuario = int(id_usuario)

        else:

            id_usuario = data_token['id_usuario']

        match novo_status:

            case 'ativo':

                if not (data_token['tipo'] == 'cadastro' or (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa')):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403
                
            case 'inativo' | 'bloqueado':

                if not (data_token['tipo'] == 'sessao' and Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa'):

                    return jsonify({ 'error': 'Você não tem permissão para tal ação' }), 403

            case _:

                return jsonify({ 'error': '"novo-status" inválido' }), 400

        #region Alterando o status de terceiros

        if data_token['id_usuario'] != id_usuario and not Usuarios(conn.connection_db).get_by_id(data_token['id_usuario'])['tipo'] != 'cooperativa':

            return jsonify({ 'error': 'Você não tem permissão para realizar tal ação' }), 403

        #endregion

        match Usuarios(conn.connection_db).alterar_status(id_usuario, novo_status):

            # 404 - Usuário não encontrado

            case None:
                return jsonify({ 'error': 'Usuário não encontrado' }), 404

            # 200 - Status do usuário alterado

            case True:
                return jsonify({ 'texto': 'Status do usuário alterado' }), 200

            # 500 - Erro ao alterar o status

            case False | _:
                return jsonify({ 'error': 'Ocorreu um erro, tente novamente' }), 500
    
    except Exception as e:

        return jsonify({ 'error': f'Erro no servidor: {e}' }), 500

    finally:

        conn.close()
