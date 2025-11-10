function mostrarErro (mensagem, form) 
{
    // Remove erro antigo, se houver

    const oldError = document.getElementById('recover-error-msg');
    if (oldError) oldError.remove();

    // Cria o novo elemento de erro

    const errorEl = document.createElement('div');
    errorEl.id = 'recover-error-msg';
    errorEl.className = 'alert alert-danger mt-3';
    errorEl.setAttribute('role', 'alert');
    errorEl.textContent = mensagem;

    form.prepend(errorEl);
}

document.addEventListener('DOMContentLoaded', function () {

    const formRecuperacao = document.getElementById('recoverForm');
    const emailInput = document.getElementById('email');
    const btnSubmit = formRecuperacao.querySelector('button[type="submit"]');
    const mensagemSucesso = document.getElementById('mensagemSucesso');

    if (!formRecuperacao || !btnSubmit || !mensagemSucesso || !emailInput) 
    {
        console.error('Elementos do formulário ausentes.');
        return;
    }

    formRecuperacao.addEventListener('submit', async (e) => {

        e.preventDefault();

        // Desativa o botão e mostra "carregando"

        btnSubmit.disabled = true;
        const originalButtonText = btnSubmit.textContent;
        btnSubmit.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Enviando...
        `;
        
        // Limpa erros antigos

        const erroAntigo = document.getElementById('recover-error-msg');
        if (erroAntigo) erroAntigo.remove();

        const email = emailInput.value;

        try 
        {
            const response = await fetch(
                
                '/api/usuarios/solicitar-recuperacao', 
                
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email })
                }
        
            );

            const data = await response.json();

            if (!response.ok) 
            {
                throw new Error(data.error || 'Falha ao conectar com o servidor.');
            }

            // Sucesso

            formRecuperacao.style.display = 'none';
            mensagemSucesso.textContent = data.texto; 
            mensagemSucesso.classList.remove('d-none');

        } 
        
        catch (error) 
        {
            console.error('Erro ao solicitar recuperação:', error);
            mostrarErro(error.message, formRecuperacao);
            
            // Restaura o botão

            btnSubmit.disabled = false;
            btnSubmit.textContent = originalButtonText;
        }
    });

});