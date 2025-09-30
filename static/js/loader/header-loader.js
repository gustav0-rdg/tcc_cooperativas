const urlDoArquivo = "../../../pages/header.html"
const header = document.querySelector('.header');
fetch(urlDoArquivo).then(response =>{
    if(!response.ok){
        throw new Error(`Error de rede: ${response.status}`);
    }
    return response.text();
}).then(htmlConteudo =>{
    header.innerHTML = htmlConteudo;
}).catch(error => {
    console.error('Houve um problema com a operação fetch:', error);
    container.innerHTML = `<p style="color: red;">Erro ao carregar o conteúdo: ${error.message}</p>`;
});
