export const registrarNovoVendedor = async (dados) =>{
    console.log(dados);
    if (dados){
        fetch('/post/dados-comprador', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify(dados.taxId)
        }).then(response => response.json())
        .then(data =>{
            console.log('Sucesso: ', data);
        }).catch((error) =>{
            console.error('erro:', error);
        })
    }
}