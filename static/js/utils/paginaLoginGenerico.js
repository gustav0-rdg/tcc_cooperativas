import { loginGenerico } from './loginGenerico.js';

export class PaginaLogin
{

    constructor (formLogin)
    {
        if (!formLogin)
        {
            throw new Error ('Revise os parâmetros da classe PaginaLogin');
        }

        this.formLogin = formLogin;
        this.submitButton = formLogin.querySelector('button[type="submit"]');
        this.errorEl = document.getElementById('login-error-msg');

    }

    limparErros () 
    {
        if (this.errorEl) this.errorEl.remove();
    }

    mostrarErro (mensagem) 
    {
        // Verifica se já existe um alerta de erro
        if (!this.errorEl) 
        {
            // Se não existir, cria um
            this.errorEl = document.createElement('div');
            this.errorEl.id = 'login-error-msg';
            this.errorEl.className = 'alert alert-danger mt-3'; 
            this.errorEl.role = 'alert';

            // Adiciona o alerta no topo do formulário
            this.formLogin.prepend(this.errorEl);
        }

        // Define o texto do erro
        this.errorEl.textContent = mensagem;
    }

    async fazerLogin (identificador, senha, tipoIdentificador)
    {
        const originalButtonText = this.submitButton.innerHTML;

        // Desativa o botão de Login
        this.submitButton.disabled = true;
        this.submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Entrando...
        `;

        try 
        {
            const [status, data] = await loginGenerico(identificador, senha, tipoIdentificador);

            if (status === 'SUCCESS_LOGIN') 
            {
                Swal.fire({

                    icon: 'success',
                    title: 'Autenticado com sucesso',

                    footer: `<a href="${data}" class="link_a">Caso não seja redirecionado clique aqui.</a>`,

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
                this.mostrarErro(data);

                // Reativa o botão de Login
                this.submitButton.disabled = false;
                this.submitButton.innerHTML = originalButtonText;
            }

        } 
        
        catch (error) 
        {
            console.error("Erro inesperado no processo de login:", error);
            mostrarErro('Um erro inesperado ocorreu. Tente novamente mais tarde.');

            // Reativa o botão de Login
            this.submitButton.disabled = false;
            this.submitButton.innerHTML = originalButtonText;
        }
    }

}