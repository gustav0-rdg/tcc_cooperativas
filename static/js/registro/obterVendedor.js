export default async function obterVendedores (cnpj){
    const decodedCnpj = cnpj.replace(/[-_/.]/g, '');
    try{
        const response = await fetch(`https://open.cnpja.com/office/${decodedCnpj}`);
        if(!response.ok){
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (!data || Object.keys(data).length === 0){
            throw new Error(`Nenhum dado encontrado.`)
        }

        return data
    } catch (error){
        console.error('Erro ao buscar dados: ', error.message);
        return null
    }
    
}