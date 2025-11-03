document.addEventListener('DOMContentLoaded', () => {
    const formCadastro = document.getElementById('formCadastro');
    
    if (formCadastro) {
        formCadastro.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Pega os dados do formulário
            const nome = document.getElementById('nomeCompleto').value;
            const email = document.getElementById('email').value;
            const senha = document.getElementById('senha').value;
            const confirmaSenha = document.getElementById('confirmaSenha').value;
            const cnpjInput = document.getElementById('cnpj'); // Pega o input do CNPJ
            const cnpj = cnpjInput.value.replace(/\D/g, ''); // Remove máscara
            const termos = document.getElementById('termos').checked;

            if (senha !== confirmaSenha) {
                Swal.fire('Erro', 'As senhas não coincidem!', 'error');
                return;
            }

            if (senha.length < 8 || senha.length > 32) {
                Swal.fire('Erro', 'A senha deve conter entre 8-32 caracteres', 'error');
            }

            if (!termos) {
                Swal.fire('Atenção', 'Você deve aceitar os termos de uso para continuar.', 'warning');
                return;
            }

            // Validação básica do CNPJ (14 dígitos)
            if (cnpj.length !== 14) {
                Swal.fire('Erro', 'O CNPJ deve conter 14 dígitos.', 'error');
                return;
           }

           Swal.fire({
                title: 'Cadastrando...',
                text: 'Aguarde enquanto validamos e salvamos seus dados...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
           });

           const formData = {
                nome: nome,
                email: email,
                senha: senha,
                cnpj: cnpj // envia o CNPJ sem máscara
           }

           try {
                const response = await fetch('/api/cooperativas/cadastrar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        nome: nome,
                        email: email,
                        senha: senha,
                        cnpj: cnpj
                    })
                });

                const data = await response.json()
                if (response.ok) {
                    Swal.fire({
                        title: 'Sucesso!',
                        text: data.message || 'Cadastro realizado! Aguarde a aprovação por um gestor.',
                        icon: 'success',
                        confirmButtonText: 'Ok'
                    }).then(() => {
                        window.location.href = '/login';
                    });
                } else {
                    throw new Error(data.error || `Erro ${response.status}`);
                }
           } catch (error) {
                console.error("Erro no fetch:", error);
                Swal.fire(
                    'Erro no Cadastro',
                    error.message || 'Não foi possível completar o cadastro. Verifique os dados ou tente novamente mais tarde.',
                    'error'
                );
           }
        });
    } else {
        console.error('Elemento #formCadastro não encontrado."');
    }

    const cnpjInputMask = document.getElementById('cnpj');
     if (cnpjInputMask) {
         cnpjInputMask.addEventListener('input', (e) => {
             let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
             value = value.slice(0, 14); // Limita a 14 dígitos

             if (value.length > 12) {
                 value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
             } else if (value.length > 8) {
                 value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{0,4})/, '$1.$2.$3/$4');
             } else if (value.length > 5) {
                 value = value.replace(/^(\d{2})(\d{3})(\d{0,3})/, '$1.$2.$3');
             } else if (value.length > 2) {
                 value = value.replace(/^(\d{2})(\d{0,3})/, '$1.$2');
             }
             e.target.value = value;
         });
     }
});