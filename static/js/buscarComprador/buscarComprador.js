import { getMateriais } from '../api/getMateriais.js'

const sectionMateriais = document.querySelector('.buscar-compradores__cartoes');
getMateriais.forEach(e => {
    sectionMateriais.innerHTML += `
    <div class="col-12 col-md-6 col-lg-4 w-100 d-flex buscar-comprador__conteiner flex-column">
        <a href="/material${e}" class="cartao-material cartao-material--plastico" data-material="plastico">
            <span class="cartao-material__rotulo">Plástico</span>
        </a>
        <button class="btn btn-lg buscar-compradores__ver-mais d-flex justify-content-center mt-2 rounded-5 w-70 align-self-center" data-material="plastico">Ver mais</button>
    </div>
    `
});