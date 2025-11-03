const URL_LOGIN_ADMIN = '/login/admin';
const cardGestores = document.getElementById('card-gestores');
const welcomeTitle = document.querySelector('.welcome-title h1');

document.addEventListener('DOMContentLoaded', async () => {
    
    var session_token = localStorage.getItem('session_token');
    if (!session_token) window.location.href = URL_LOGIN_ADMIN;

    try 
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
    
        const data_usuario = await response?.json();
    
        if (!response.ok)
        {
            throw new Error (
    
                'error' in data_usuario
                ?
                data_usuario.error
                :
                'Erro Interno. Tente novamente mais tarde.'
    
            );
        }

        if (!['root', 'gestor'].includes(data_usuario.tipo)) 
        {
            Swal.fire({

                title: 'Acesso Negado!',
                text: 'Área restrita para gestores.',
                icon: 'error',
                timer: 1500
                
            })

            .then(() => window.location.href = URL_LOGIN_ADMIN);
        }

        if (data_usuario.tipo === 'root') 
        {
            if (cardGestores) cardGestores.style.display = 'block';
        }

        // Mensagem de Boas Vindas
        if (welcomeTitle && data_usuario.nome) welcomeTitle.textContent = `Boas-vindas, ${data_usuario.nome.split(' ')[0]}!`;
    } 
    
    catch (error) 
    {
        throw new Error (error.message);
    }
});