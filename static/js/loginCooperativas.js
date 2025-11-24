import { PaginaLogin } from './utils/paginaLoginGenerico.js';

function limparCNPJ (cnpj) 
{
    return cnpj.replace(/[^\d]/g, '');  // Remove tudo que não for número
}

// Aguarda o conteúdo da página carregar
document.addEventListener('DOMContentLoaded', () => {
    
    var loginForm = document.getElementById('form-login');
    const cnpjInput = document.getElementById('cnpj');
    const senhaInput = document.getElementById('senha');
    const submitButton = loginForm.querySelector('button[type="submit"]');

    if (!loginForm) {
        console.error('Formulário de login não encontrado.');
        return;
    }

    const loginCooperativa = new PaginaLogin(loginForm);

    loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const cnpj = limparCNPJ(cnpjInput.value);
        const senha = senhaInput.value;

        loginCooperativa.fazerLogin(cnpj, senha, 'CNPJ');

            if (status === 'SUCCESS_LOGIN') 
            {
                Swal.fire({
                    title: 'Sucesso!',
                    text: 'Login realizado. Redirecionando...',
                    icon: 'success',
                    timer: 1500, 
                    showConfirmButton: false,
                    allowOutsideClick: false 
                });
    
                setTimeout(() => {
                    window.location.href = data; // Redireciona para a URL retornada
                }, 1500);
            }

            else 
            {
                showLoginError(data);
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }

        } catch (error) {
            // Pega erros inesperados do próprio JavaScript
            console.error("Erro inesperado no processo de login:", error);
            showLoginError('Um erro inesperado ocorreu. Tente novamente mais tarde.');
            // Reativa o botão
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    });
});