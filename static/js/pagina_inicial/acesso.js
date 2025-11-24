const user_data = JSON.parse(sessionStorage.getItem('usuario'));
const pagInfos = document.querySelector('.pag_infos');
const registrarVenda = document.querySelector('.registrar_venda');
const acoes__cooperativa = document.querySelector('.acoes__cooperativa');
if (user_data.tipo == 'cooperado'){
    registrarVenda.style.display = 'none';
    

    acoes__cooperativa.classList.add('centralizado');
}