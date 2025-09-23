const btn = document.querySelector('#buscaCnpj');
const values = document.querySelector('#buscaCnpjInput');

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

btn.addEventListener('click', async () =>{
    const valueDecoded = values.value.replace(/[-_/.]/g, '');
    const dados = await validarCnpj(valueDecoded);
    console.log("Dados encontrados: ", dados);
})