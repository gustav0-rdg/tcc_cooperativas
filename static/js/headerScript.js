import { getUsuarioInfo } from "./utils/loginGenerico.js";

document.addEventListener('DOMContentLoaded', async () => {

    const token = localStorage.getItem('session_token');
    const homeLink = document.getElementById('home-link');
    const logoutLink = document.getElementById('logout-link');
    const headerInfoCoop = document.getElementById('header-info-cooperativa');
    const headerNomeCoop = document.getElementById('header-nome-cooperativa');
    const headerEndCoop = document.getElementById('header-endereco-cooperativa');
    const headerInfoAdmin = document.getElementById('header-info-admin');
    const headerNomeAdmin = document.getElementById('header-nome-admin');

    function handleLogout() {
        localStorage.removeItem('session_token');
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Desconectado',
                text: 'Você saiu da sua conta.',
                icon: 'info',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                window.location.href = '/'; 
            });
        } else {
            alert('Você foi desconectado.');
            window.location.href = '/'; 
        }
    }

    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    if (!token || !homeLink) {
        if(logoutLink) logoutLink.style.display = 'none';
        if(homeLink) homeLink.style.display = 'none'; 
        return; 
    }
    
    try 
    {
        
        //#region Validação dos dados do usuário

        let user_data = JSON.parse(sessionStorage.getItem('usuario', null));

        if (user_data == null) 
        {
            const session_token = localStorage.getItem('session_token', null);

            if (session_token == null)
            {
                user_data = await getUsuarioInfo(session_token);
                sessionStorage.setItem('usuario', user_data);
            }

            else window.location.href = '/';
        }

        //#endregion

        if (user_data.tipo === 'gestor' || user_data.tipo === 'root') {
            homeLink.href = '/pagina-inicial/gestor';
            if(headerInfoAdmin && headerNomeAdmin && user_data.nome) {
                headerNomeAdmin.textContent = user_data.nome.split(' ')[0];
                headerInfoAdmin.style.display = 'block';
            }
        } else if (user_data.tipo === 'cooperativa') {
            homeLink.href = '/pagina-inicial';
             if(headerInfoCoop && headerNomeCoop && user_data.nome) { 
                headerNomeCoop.textContent = user_data.nome; 
                headerInfoCoop.style.display = 'block';
             }
        } else if (user_data.tipo === 'cooperado') {
             homeLink.href = '/pagina-inicial'; 
        }

    } 
    
    catch (error) 
    {
        console.error('Erro ao buscar dados do usuário para o header:', error);
    }
});