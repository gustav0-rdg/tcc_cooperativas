async function getUsuarioInfo (session_token) 
{
    
    const response = await fetch (
        
        '/api/usuarios/get', 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data = await response?.json();

    if (!response.ok) 
    {
        throw new Error(data.error || 'Não foi possível buscar os dados do usuário.');
    }

    return data;
}

async function loginGenerico (identificador, senha, tipoIdentificador)
{
    if (!identificador)
    {
        return ['IDENTIFICADOR_INVALIDO', `O campo de ${tipoIdentificador} é obrigatório.`];
    }

    if (senha?.length < 8) 
    {
        return ['SENHA_LENGTH_INVALIDA', 'A senha deve ter no mínimo 8 caracteres.'];
    }

    try 
    {
        const response = await fetch(
            
            '/api/usuarios/login', 
            
            {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({

                    identificador: identificador,
                    senha: senha

                })
            }
        );

        const data = await response?.json();

        if (!response.ok) 
        {
            throw new Error(data.error || 'Erro desconhecido ao tentar fazer login.');
        }

        localStorage.setItem('session_token', data.token);
        document.cookie = `session_token=${data.token}; path=/; max-age=2592000`; // 30 dias

        console.log(data)

        const user_info = await getUsuarioInfo(data.token);
        sessionStorage.setItem('usuario', JSON.stringify(user_info));

        const redirect_url = {

            'gestor': '/pagina-inicial/gestor',
            'root': '/pagina-inicial/gestor',
            'cooperativa': '/pagina-inicial',
            'cooperado': '/pagina-inicial'

        }

        return ['SUCCESS_LOGIN', redirect_url[user_info.tipo]];

    } 
    
    catch (error) 
    {
        return ['ERROR_LOGIN', (error.message || 'Erro Desconhecido')];
    }
}

export
{
    loginGenerico,
    getUsuarioInfo
}