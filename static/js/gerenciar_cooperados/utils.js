// Mascara / buscar CEP

// --- Funções de Máscara ---

function formatCPF(input) {
    let value = input.value.replace(/\D/g, ''); 
    value = value.slice(0, 11); 
    
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    
    input.value = value;
}

function formatTelefone(input) {
    let value = input.value.replace(/\D/g, ''); 
    value = value.slice(0, 11); 

    if (value.length > 10) {
        value = value.replace(/^(\d\d)(\d{5})(\d{4}).*/, '($1) $2-$3');
    } else if (value.length > 6) {
        value = value.replace(/^(\d\d)(\d{4})(\d{0,4}).*/, '($1) $2-$3');
    } else if (value.length > 2) {
        value = value.replace(/^(\d\d)(\d{0,5}).*/, '($1) $2');
    } else if (value.length > 0) {
        value = value.replace(/^(\d*)/, '($1');
    }
    
    input.value = value;
}

function formatCEP(input) {
    let value = input.value.replace(/\D/g, '');
    value = value.slice(0, 8);
    value = value.replace(/^(\d{5})(\d)/, '$1-$2');
    input.value = value;
}

// --- API ViaCEP ---

async function buscarCep(cepValor) {
    const cep = cepValor.replace(/\D/g, ''); 

    if (cep.length !== 8) {
        // Swal para caso o usuario digite um CEP menor que 8 digitos
        Swal.showValidationMessage('CEP inválido. Deve conter 8 dígitos.');
        return; 
    }

    // Mostra um loading simples no SweetAlert
    const swalTitle = Swal.getHtmlContainer().querySelector('.swal2-title');
    swalTitle.insertAdjacentHTML('afterend', '<div id="cep-loading" class="swal2-html-container" style="display: block;">Buscando CEP...</div>');

    try {
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        
        if (!response.ok) throw new Error('CEP não encontrado');

        const data = await response.json();

        if (data.erro) {
            Swal.showValidationMessage('CEP não encontrado. Verifique e tente novamente.');
            return;
        }

        // Popula os campos do modal
        document.getElementById('endereco').value = data.logradouro;
        document.getElementById('bairro').value = data.bairro;
        document.getElementById('cidade').value = data.localidade;
        document.getElementById('estado').value = data.uf;

        // Foca no campo "Número"
        document.getElementById('numero').focus();

    } catch (error) {

        Swal.showValidationMessage(`Erro ao buscar CEP: ${error.message}`);
        
    } finally {
        // Remove o loading
        const loadingDiv = document.getElementById('cep-loading');
        if (loadingDiv) loadingDiv.remove();
    }
}