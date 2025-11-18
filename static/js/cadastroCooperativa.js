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

            if (senha !== confirmaSenha) {
                Swal.fire({
                    icon: "error",
                    title: "Erro",
                    text: "As senhas não coincidem",
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });
                return;
            }

            if (senha.length < 8 || senha.length > 32) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'A senha deve conter entre 8 e 32 caracteres.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });
                return;
            }

            if (!termos) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Atenção',
                    text: 'Você deve aceitar os termos de uso para continuar.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });
                return;
            }

            if (cnpj.length !== 14) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'O CNPJ deve conter 14 dígitos.',
                    confirmButtonColor: 'var(--verde-claro-medio)'
                });
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

                // Solicita o arquivo de comprovação
                const { value: file } = await Swal.fire({
                    title: 'Pré-cadastro realizado!',
                    text: 'Envie um documento (ATA ou similar) que comprove a legitimidade da cooperativa.',
                    input: 'file',
                    inputLabel: 'O documento será analisado por um gestor.',
                    inputAttributes: {
                        'accept': 'image/png, image/jpeg, image/jpg, application/pdf',
                        'aria-label': 'Upload do documento de comprovação'
                    },
                    confirmButtonText: 'Enviar Documento',
                    confirmButtonColor: 'var(--verde-claro-medio)',
                    showCancelButton: true,
                    cancelButtonText: 'Enviar depois',
                    allowOutsideClick: false,
                });

                if (file) {
                    Swal.fire({
                        title: 'Enviando...',
                        text: 'Aguarde enquanto o arquivo é enviado.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    const formData = new FormData();
                    formData.append('documento', file);
                    formData.append('id_cooperativa', idCooperativa);

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
                        confirmButtonText: 'Confirmar',
                        confirmButtonColor: 'var(--verde-claro-medio)'
                    }).then(() => {
                        window.location.href = '/login';
                    });

                } else {
                    Swal.fire({
                        title: 'Pendente!',
                        text: 'Seu pré-cadastro está feito. Envie o documento mais tarde para aprovação!',
                        icon: 'warning',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: 'var(--verde-claro-medio)'
                    }).then(() => {
                        window.location.href = '/login';
                    });
                }

            } catch (error) {
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