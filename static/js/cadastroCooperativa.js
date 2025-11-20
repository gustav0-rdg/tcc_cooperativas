const cnpjInput = document.getElementById('cnpj');

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

            if (senha !== confirmaSenha) 
            {
                Swal.fire({
                    icon: "error",
                    title: "Erro",
                    text: "As senhas não coincidem",
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });

                return;
            }

            if (senha.length < 8 || senha.length > 32) 
            {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'A senha deve conter entre 8 e 32 caracteres.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });

                return;
            }

            if (!termos) 
            {
                Swal.fire({
                    icon: 'warning',
                    title: 'Atenção',
                    text: 'Você deve aceitar os termos de uso para continuar.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });

                return;
            }

            if (cnpj.length !== 14) 
            {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'O CNPJ deve conter 14 dígitos.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });

                return;
            }

            if (!documentoATA) 
            {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Envie a ATA de sua cooperativa',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });

                return;
            }

            try 
            {
                Swal.fire({
                    title: 'Aguarde...',
                    text: 'Validando seus dados e realizando seu cadastro.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                const dataCadastro = new FormData();

                dataCadastro.append('nome', nome);
                dataCadastro.append('email', email);
                dataCadastro.append('senha', senha);
                dataCadastro.append('cnpj', cnpj);
                dataCadastro.append('documento', documentoATA);

                const response = await fetch(
                    
                    '/api/cooperativas/cadastrar', 
                    
                    {
                        method: 'POST',
                        body: dataCadastro
                    }
                );

                const data = await response.json();

                console.log(data);
                console.log(response);

                if (!response.ok) {
                    throw new Error(data.error || `Erro ${response.status}`);
                }

                Swal.fire({
                    title: 'Sucesso!',
                    text: 'Arquivo enviado. Aguarde a aprovação por e-mail!',
                    icon: 'success',
                    confirmButtonText: 'Confirmar',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                }).then(() => {
                    window.location.href = '/login';
                });

            } 
            
            catch (error) 
            {
                console.error("Erro no fetch:", error);

                Swal.fire({
                    title: 'Erro no Cadastro',
                    text: error.message || 'Não foi possível completar o cadastro. Tente novamente mais tarde.',
                    icon: 'error',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });
            }
        });
    }
});

// Mascara CNPJ
if (cnpjInput) {
    cnpjInput.addEventListener('input', function () {
        let value = this.value.replace(/\D/g, ""); // remove tudo que não é número

        // limita a 14 números
        if (value.length > 14) value = value.slice(0, 14);

        // aplica a máscara
        value = value.replace(/^(\d{2})(\d)/, "$1.$2");
        value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
        value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
        value = value.replace(/(\d{4})(\d)/, "$1-$2");

        this.value = value;
    });
}