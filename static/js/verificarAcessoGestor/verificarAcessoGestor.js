document.addEventListener('DOMContentLoaded', async () => {
    
    const token = localStorage.getItem('session_token');

    function expulsarParaLogin(mensagem) {
        console.error('Erro de autenticação:', mensagem);
        localStorage.removeItem('session_token');
        Swal.fire({
            title: 'Acesso Negado!',
            text: mensagem,
            icon: 'error',
            confirmButtonColor: '#d33'
        }).then(() => {
            window.location.href = '/login/admin';
        });
    }

    if (!token) {
        expulsarParaLogin('Você precisa estar logado para acessar esta página.');
        return;
    }

    try {
        const response = await fetch('/api/usuarios/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Token inválido ou expirado');
        }

        if (data.tipo !== 'gestor' && data.tipo !== 'root') {
            expulsarParaLogin('Você não tem permissão para acessar esta área.');
            return;
        }

        if (data.tipo === 'root') {
            const cardGestores = document.getElementById('card-gestores');
            if (cardGestores) {
                cardGestores.style.display = 'block';
            }
        }

        const welcomeTitle = document.querySelector('.welcome-title h1');
        if (welcomeTitle && data.nome) {
            welcomeTitle.textContent = `Boas-vindas, ${data.nome.split(' ')[0]}!`;
        }

    } catch (error) {

        expulsarParaLogin(error.message);
    }
});