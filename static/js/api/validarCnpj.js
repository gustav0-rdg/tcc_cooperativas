const btn = document.querySelector('#form');
const values = document.querySelector('#cnpj');

const adequacoesCnpj = {
    id: 2143,
    atvValidas: [3811400,3831901,3831999, 3832700, 3812200]
};

const validarCnpj = async (cnpj) =>{
    try{
        const response = await fetch(`https://open.cnpja.com/office/${cnpj}`);
        if(!response.ok){
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (!data || Object.keys(data).length === 0){
            throw new Error(`Nenhum dado encontrado.`)
        }

        if (data.company.nature.id == adequacoesCnpj.id 
            || data.sideActivities.every((valor, index) => valor === adequacoesCnpj[index])){
            return data
        } else {
            throw new Error("O CNPJ enviado não se adequa aos padrões nacionais de cooperativas.")
        }
    } catch (error){
        console.error('Erro ao buscar dados: ', error.message);
        return null
    }
    
}

btn.addEventListener('submit', async (e) =>{
    
    e.preventDefault();
    const valueDecoded = values.value.replace(/[-_/.]/g, '');
    const dados = await validarCnpj(valueDecoded);
    if (dados){
        Swal.fire({
            background: "#9BCA58",
            html: `
                <h2>Cooperativa válida</h2>
            `,
            icon: "success",
            showCancelButton: true,
            confirmButtonText: 'Fazer login',
            cancelButtonText: 'Cancelar',
            customClass: {
                popup: 'my-popup',
                title: 'my-title',
                content: 'my-content',
                confirmButton: 'my-btn',
                cancelButton: 'my-btn-cancel'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                // Se o botão "Fazer login" for clicado, redireciona para a URL
                // Define o action do formulário aqui, após o SweetAlert
                // Isso vai garantir que o atributo action seja configurado antes do envio
                btn.setAttribute("action", "/post/cooperativa");

                // Envia o formulário após configurar o action
                // (você pode remover o `window.location.href` e usar `submit()` se precisar de envio real)
                btn.submit();
            } else if (result.isDismissed) {
                // Se o botão "Cancelar" for clicado, pode fazer outra ação
                console.log('Ação cancelada');
            }
        });

    } else{
        Swal.fire({
            background: "#9BCA58",
            title: "Dados inválidos",
            icon: "error"
        });
    }
})