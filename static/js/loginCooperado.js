import { loginGenerico } from './utils/loginGenerico.js';

function limparCPF (cpf) 
{
    return cpf.replace(/[^\d]/g, '');  // Remove tudo que não for número
}

function showLoginError(message) {
    const form = document.getElementById('form-login-cooperado');
    // Verifica se já existe um alerta de erro
    let errorEl = document.getElementById('login-error-msg');
    
    if (!errorEl) {
        // Se não existir, cria um
        errorEl = document.createElement('div');
        errorEl.id = 'login-error-msg';
        // Usa classes do Bootstrap que já estão no seu HTML
        errorEl.className = 'alert alert-danger mt-3'; 
        errorEl.role = 'alert';
        // Adiciona o alerta no topo do formulário
        form.prepend(errorEl);
    }
    // Define o texto do erro
    errorEl.textContent = message;
}

function clearLoginError() {
    const errorEl = document.getElementById('login-error-msg');
    if (errorEl) {
        errorEl.remove();
    }
}

// Aguarda o conteúdo da página carregar
document.addEventListener('DOMContentLoaded', () => {
    
    const loginForm = document.getElementById('form-login-cooperado');
    const cpfInput = document.getElementById('cpf');
    const senhaInput = document.getElementById('senha');
    const submitButton = loginForm.querySelector('button[type="submit"]');

    if (!loginForm) {
        console.error('Formulário de login não encontrado.');
        return;
    }

    // Adiciona o listener de evento "submit" ao formulário
    loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();
        clearLoginError();

        // Pega os valores dos campos
        const cpf = limparCPF(cpfInput.value);
        const senha = senhaInput.value;

        // Salva o texto original e desativa o botão
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Entrando...
        `;

        try {
            // Chama a função genérica de login
            // O 'identificador' para esta tela é o CPF
            const [status, data] = await loginGenerico(cpf, senha);

            if (status === 'SUCCESS_LOGIN') 
            {
                Swal.fire({

                    icon: 'success',
                    title: 'Autenticado com sucesso',
                    showConfirmButton: false,
                    timer: 1500

                });

                setTimeout(

                    function () {
                        window.location.href = data;
                    },

                    1500

                )
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
