import { getMateriais } from "./api/getMateriais.js";
import { getSubtipos } from "./api/getSubTipos.js"
import { getCompradoresPorMaterial } from "./api/getCompradores.js";
import { getFeedbackTags, getComentarios } from "./api/getAvaliacoes.js";

const buscarCompradoresSec = document.querySelector('.buscar-compradores__cartoes');
const buscarSubtipos = document.querySelector('#detalhe-material');
const detalheCompradores = document.querySelector('#detalhe-comprador');
async function renderizarMateriais() {
    const materiais = await getMateriais();
    if (!materiais) return; // Se não houver materiais, não faz nada
    buscarCompradoresSec.innerHTML = ''; 

    materiais.forEach(material => {

        buscarCompradoresSec.innerHTML += `
            <div class="col-12 col-md-6 col-lg-4 w-100 d-flex buscar-comprador__conteiner flex-column">
                <a href="#" class="cartao-material cartao-material--${material.nome_padrao}" data-material="${material.id_material_catalogo}">
                    <span class="cartao-material__rotulo">${material.nome_padrao}</span>
                </a>
                <button class="btn btn-lg buscar-compradores__ver-mais d-flex justify-content-center mt-2 rounded-5 w-70 align-self-center" data-material="${material.id_material_catalogo}">Ver mais</button>
            </div>
        `;
    });
}

buscarCompradoresSec.addEventListener('click', async (event) => {
    event.preventDefault();
    const targetMateriais = event.target.closest('[data-material]');
    if (targetMateriais) {
        const materialNome = targetMateriais.dataset.material;
        const subtipos = await getSubtipos(materialNome);
        console.log(subtipos);  
        await renderizarSubtipos(subtipos, materialNome)
    }
});

async function renderizarSubtipos(subtipos, id_material) {
    buscarCompradoresSec.innerHTML = '';
    const htmlSubtipos = subtipos.map((subtipo, index) => `
        <button class="subtipo-card" data-subtipo="${subtipo.id_material_catalogo}">
            <h1>${subtipo.nome_especifico}</h2>
        </button>
    `).join('');
    buscarSubtipos.innerHTML = `
    <div class="subtipos">
        <button class="">Voltar</button>
        ${htmlSubtipos}
    </div>
    `;
    buscarSubtipos.classList.remove('hidden');
    const btn = buscarSubtipos.querySelectorAll('.subtipo-card');
    btn.forEach(e =>{
        e.addEventListener('click', async (event) =>{
            const id_subtipo = event.target.dataset.subtipo;
            const compradores = await getCompradoresPorMaterial(id_material)
            await renderizarCompradores(compradores);
            buscarSubtipos.classList.add('hidden');
        })
    })
}

async function renderizarCompradores(compradores) {
    buscarCompradoresSec.innerHTML = '';
    const htmlCompradores = compradores.length > 0 ? compradores.map((comprador, index) => `
        <div class="comprador-card">
            <div class="comprador-header">
                <div class="comprador-avatar">
                    <span class="material-icons">${comprador.avatar}</span>
                </div>
                <div class="comprador-info">
                    <h3>${comprador.razao_social}</h3>
                    <span>Avaliação: ${comprador.score_confianca} <i class="fa-solid fa-star" style="color: var(--verde-escuro)"></i></span>
                </div>
                <div class="comprador-preco">
                    <p>Preço pago: R$${comprador.valor_total}</p>
                    <small>${comprador.quantidade_kg} Kgs</small>
                </div>
            </div>
            <button class="verMais" data-value="${comprador.cnpj}" data-index="${index}">Ver mais</button>

        </div>
    `).join('') : "<h1>Nenhum comprador disponível.</h1>    ";

    detalheCompradores.innerHTML = htmlCompradores;
    detalheCompradores.classList.remove('hidden')

    const todosOsBotoes = detalheCompradores.querySelectorAll('.verMais');

    todosOsBotoes.forEach(botao => {
        botao.addEventListener('click', async (event) => {
            const compradorIndex = event.target.dataset.index;
            const compradorCnpj = event.target.dataset.value;
            const avaliacoes = await getFeedbackTags(compradorCnpj);
            const comentarios = await getComentarios(compradorCnpj);
            const compradorSelecionado = compradores[compradorIndex];
            console.log(compradorSelecionado);
            Swal.fire({
                title: `${compradorSelecionado.razao_social}`,
                background: "var(--verde-principal)",
                html: `
                    <p><strong>Avaliação:</strong> ${compradorSelecionado.score_confianca} <i class="fa-solid fa-star" style="color: var(--verde-claro)"></i></p>
                    <p><strong>Valor Total Pago:</strong> R$${compradorSelecionado.valor_total}</p>
                    <p><strong>Total Comprado:</strong> ${compradorSelecionado.quantidade_kg} Kgs</p>
                    <button class="comentarios-livres dropdown-btn">
                        Ver comentarios
                    </button> 
                    <div class="dropdown-content hidden">
                    ${
                        comentarios.map(a => `
                            <div class="comentarios-livre">
                                <div class="comentarios-livre__avatar"></div>
                                <div class="comentarios-livre__text">${a.comentario_livre}</div>
                            </div>`
                        ).join('')
                    }
                    </div>
                    <div class="container">
                    ${
                        avaliacoes.map(a => `<div class="item">${a.texto} <span class="badge">${a.quantidade}</span></div>`
                        ).join('')
                    }
                    </div>
                    `,
                didOpen: () =>{
                    const comentariosBtn = Swal.getPopup().querySelector(".dropdown-btn");
                    const comentariosSec = Swal.getPopup().querySelector(".dropdown-content");
                    comentariosBtn.addEventListener('click', () =>{
                        comentariosSec.classList.toggle('hidden');
                    })
                }
            });
        });
    });
}

// Inicia o processo
renderizarMateriais();