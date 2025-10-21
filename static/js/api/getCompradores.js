export async function getCompradores() {
    const response = await fetch("/get/compradores")
    const data = await response.json()
    return data
}

// Função para buscar os compradores pelo NOME do material
export async function getCompradoresPorMaterial(nome_material) {
    try {
        const response = await fetch(`/get/comprador/${nome_material}`);            
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Falha na requisição fetch:", error);
        return [];
    }
}