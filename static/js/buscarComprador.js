import { getMateriais } from "./api/getMateriais.js";

// Função para buscar os compradores pelo NOME do material
async function getCompradores(nome_material) {
    try {
        // Use encodeURIComponent para garantir que nomes com espaços (ex: "Papel Branco") funcionem na URL
        const response = await fetch(`/comprador/${encodeURIComponent(nome_material)}`);
        
        // Verifica se a resposta foi bem-sucedida (status 2xx)
        if (!response.ok) {
            console.error(`Erro ao buscar compradores para ${nome_material}:`, response.statusText);
            return []; // Retorna um array vazio em caso de erro
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Falha na requisição fetch:", error);
        return [];
    }
}

const buscarCompradoresSec = document.querySelector('.buscar-compradores__cartoes');

// 1. Renderiza os cartões de materiais
async function renderizarMateriais() {
    const materiais = await getMateriais();
    if (!materiais) return; // Se não houver materiais, não faz nada

    // Limpa o conteúdo antes de adicionar novos itens
    buscarCompradoresSec.innerHTML = ''; 

    materiais.forEach(material => {
        // O href agora é '#' para não navegar para outra página.
        // O nome do material é guardado em 'data-material'
        buscarCompradoresSec.innerHTML += `
            <div class="col-12 col-md-6 col-lg-4 w-100 d-flex buscar-comprador__conteiner flex-column">
                <a href="#" class="cartao-material cartao-material--${material.nome_padrao}" data-material="${material.id_material_catalogo}">
                    <span class="cartao-material__rotulo">${material.nome_padrao}</span>
                </a>
                <button class="btn btn-lg buscar-compradores__ver-mais d-flex justify-content-center mt-2 rounded-5 w-70 align-self-center" data-material="${material.nome_padrao}">Ver mais</button>
            </div>
        `;
    });
}

// 2. Adiciona um único Event Listener no container pai
buscarCompradoresSec.addEventListener('click', async (event) => {
    // Impede o comportamento padrão do link (que é recarregar a página com #)
    event.preventDefault();

    // Encontra o link ou botão mais próximo que foi clicado
    const targetElement = event.target.closest('[data-material]');

    if (targetElement) {
        const materialNome = targetElement.dataset.material;
        console.log(`Buscando compradores para: ${materialNome}`);

        // **Apenas agora** nós chamamos a API
        const compradores = await getCompradores(materialNome);

        // 3. Agora você faz algo com os dados recebidos
        console.log(compradores); // Mostra os compradores no console
        // Daqui para frente, você chamaria uma função para renderizar esses compradores em outra seção da página.
        // ex: renderizarListaDeCompradores(compradores);
    }
});


// Inicia o processo
renderizarMateriais();