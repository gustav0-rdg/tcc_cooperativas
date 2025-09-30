const urlDoArquivo2 = "../../../pages/footer.html"
const footer = document.querySelector('.footer');
fetch(urlDoArquivo2).then(response =>{
    if(!response.ok){
        throw new Error(`Error de rede: ${response.status}`);
    }
    return response.text();
}).then(htmlConteudo =>{
    footer.innerHTML = htmlConteudo;
}).catch(error => {
    console.error('Houve um problema com a operação fetch:', error);
    footer.innerHTML = `<p style="color: red;">Erro ao carregar o conteúdo: ${error.message}</p>`;
});
