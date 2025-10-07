const novoComprador = {
    razao_social: undefined,
    nome_fantasia: undefined,
    cnpj: undefined,
    endereco: undefined,
    cidade: undefined,
    estado: undefined,
    ramo_atividade: undefined,
    score_confianca: undefined,
    numero_avaliacoes: 0,
    data_ultima_venda: undefined,
    latitude: undefined,
    longitude: undefined
}

export const registrarNovoVendedor = async (dados) =>{
    if (dados){
        novoComprador.cidade = dados.address.city;
        dados.alias === null ? novoComprador.nome_fantasia = dados.company.name : novoComprador.nome_fantasia = dados.alias;
        novoComprador.cnpj = dados.taxId;
        novoComprador.endereco = `${dados.address.street}, ${dados.address.number}`;
        novoComprador.estado = dados.address.state;
        novoComprador.razao_social = dados.company.name;
        novoComprador.ramo_atividade = dados.mainActivity.text;
        
        fetch('/post/dados-comprador', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify(novoComprador)
        }).then(response => response.json())
        .then(data =>{
            console.log('Sucesso: ', data);
        }).catch((error) =>{
            console.error('erro:', error);
        })
    }
}