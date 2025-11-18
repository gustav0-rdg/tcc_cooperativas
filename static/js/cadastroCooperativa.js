document.addEventListener('DOMContentLoaded', () => {
    const formCadastro = document.getElementById('formCadastro');

    if (formCadastro) {
        formCadastro.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Pega os dados do formulário
            const nome = document.getElementById('nomeCompleto').value.trim();
            const email = document.getElementById('email').value.trim();
            const senha = document.getElementById('senha').value;
            const confirmaSenha = document.getElementById('confirmaSenha').value;
            const cnpjInput = document.getElementById('cnpj');
            const cnpj = cnpjInput.value.replace(/\D/g, ''); // Remove máscara
            const termos = document.getElementById('termos').checked;
            const documentoATA = document.getElementById('uploadAta').files[0];

            // Validações básicas
            if (senha !== confirmaSenha) {
                Swal.fire('Erro', 'As senhas não coincidem!', 'error');
                return;
            }

            if (senha.length < 8 || senha.length > 32) {
                Swal.fire('Erro', 'A senha deve conter entre 8 e 32 caracteres.', 'error');
                return;
            }

            if (!documentoATA || documentoATA?.type != 'application/pdf')
            {
                Swal.fire('Atenção', 'Envie um documento oficial da ATA válido', 'error');
                return;
            }

            if (cnpj.length !== 14) {
                Swal.fire('Erro', 'O CNPJ deve conter 14 dígitos.', 'error');
                return;
            }

            if (!termos) {
                Swal.fire('Atenção', 'Você deve aceitar os termos de uso para continuar.', 'warning');
                return;
            }

            try {
                Swal.fire({
                    title: 'Aguarde...',
                    text: 'Validando seus dados e realizando pré-cadastro.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                // Faz o PRÉ-CADASTRO
                const response = await fetch('/api/cooperativas/cadastrar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nome,
                        email,
                        senha,
                        cnpj
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `Erro ${response.status}`);
                }

                const idCooperativa = data.id_cooperativa;

                const fileResponse = await fetch('/api/cooperativas/enviar-documento', {
                    method: 'POST',
                    body: formData
                });

                const fileData = await fileResponse.json();

                if (!fileResponse.ok) {
                    throw new Error(fileData.error || 'Não foi possível enviar o documento.');
                }

                Swal.fire({

                    title: 'Sucesso!',
                    text: 'Arquivo enviado. Aguarde a aprovação por e-mail!',
                    icon: 'success',
                    confirmButtonText: 'Confirmar'
                    
                }).then(() => {
                    window.location.href = '/login';
                });

            } catch (error) {
                console.error("Erro no fetch:", error);
                Swal.fire(
                    'Erro no Cadastro',
                    error.message || 'Não foi possível completar o cadastro. Tente novamente mais tarde.',
                    'error'
                );
            }
        });
    }
});
