// Dev by vito

document.addEventListener('DOMContentLoaded', () => {

    const materiaisData = {
        'plastico': {
            titulo: 'Plásticos',
            subtipos: [
                { nome: 'PET', img: '../static/imgs/subtipos/pet.png', codigo: '01', codigoImg: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Symbol_Resin_Code_01_PET.svg/200px-Symbol_Resin_Code_01_PET.svg.png' },
                { nome: 'PEAD', img: '../static/imgs/subtipos/pead.png', codigo: '02', codigoImg: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Symbol_Resin_Code_02_PE-HD.svg/200px-Symbol_Resin_Code_02_PE-HD.svg.png' },
                { nome: 'PVC', img: '../static/imgs/subtipos/pvc.png', codigo: '03', codigoImg: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Symbol_Resin_Code_03_PVC.svg/200px-Symbol_Resin_Code_03_PVC.svg.png' },
            ]
        },
        'papel': {
            titulo: 'Papel',
            subtipos: [
                { nome: 'Papel Branco', img: '../static/imgs/subtipos/papel-branco.png', codigo: '', codigoImg: '' },
                { nome: 'Papel Misto (Revista)', img: '../static/imgs/subtipos/revista.png', codigo: '', codigoImg: '' },
                { nome: 'Jornal', img: '../static/imgs/subtipos/jornal.png', codigo: '', codigoImg: '' },
            ]
        },
        'metal': {
            titulo: 'Metais',
            subtipos: [
                { nome: 'Alumínio (Lata)', img: '../static/imgs/subtipos/lata-aluminio.png', codigo: '', codigoImg: '' },
                { nome: 'Ferro (Sucata)', img: '../static/imgs/subtipos/sucata-ferro.png', codigo: '', codigoImg: '' },
            ]
        },
        'madeira': { 
            titulo: 'Madeira', 
            subtipos: [{ nome: 'Palete', img: '../static/imgs/subtipos/palete.png', codigo: '', codigoImg: '' }] 
        },
        'pilha': { 
            titulo: 'Pilhas e Baterias', 
            subtipos: [{ nome: 'Pilha AA', img: '../static/imgs/subtipos/pilha.png', codigo: '', codigoImg: '' }] 
        },
        'borracha': { 
            titulo: 'Borracha', 
            subtipos: [{ nome: 'Pneu', img: '../static/imgs/subtipos/pneu.png', codigo: '', codigoImg: '' }] 
        },
        'papelao': { 
            titulo: 'Papelão', 
            subtipos: [{ nome: 'Caixa', img: '../static/imgs/subtipos/caixa-papelao.png', codigo: '', codigoImg: '' }] 
        },
        'vidro': { 
            titulo: 'Vidro', 
            subtipos: [{ nome: 'Garrafa', img: '../static/imgs/subtipos/garrafa-vidro.png', codigo: '', codigoImg: '' }] 
        },
    };

    const compradoresData = {
        'PET': [
            { nome: 'Comprador A (PET)', avaliacao: 4.5, preco: 'R$ 0,50/kg', avatar: 'person', infos: 'Compro PET limpo e prensado. Pagamento na hora. Entre em contato para grandes volumes.' },
            { nome: 'Sucatas B (PET)', avaliacao: 4.0, preco: 'R$ 0,45/kg', avatar: 'store', infos: 'Apenas PET. Não aceito PET sujo de óleo.' },
        ],
        'PEAD': [
             { nome: 'Comprador C (PEAD)', avaliacao: 4.2, preco: 'R$ 0,40/kg', avatar: 'person', infos: 'Retiro no local acima de 100kg. Aceito embalagens de detergente, amaciante, etc.' }
        ],
        'Garrafa': [
             { nome: 'Comprador D (Vidro)', avaliacao: 4.8, preco: 'R$ 0,15/kg', avatar: 'store', infos: 'Compro garrafas verdes, transparentes e marrons. Não pego vidro quebrado.' }
        ],
        'Caixa': [
             { nome: 'Comprador E (Papelão)', avaliacao: 4.6, preco: 'R$ 0,25/kg', avatar: 'store', infos: 'Apenas papelão seco e amarrado.' }
        ],
        'Alumínio (Lata)': [
             { nome: 'Comprador F (Alumínio)', avaliacao: 4.9, preco: 'R$ 5,00/kg', avatar: 'person', infos: 'O melhor preço da região! Compro qualquer quantidade de latinha.' }
        ],
        'Pneu': [
             { nome: 'Comprador G (Borracha)', avaliacao: 4.0, preco: 'R$ 0,05/kg', avatar: 'store', infos: 'Apenas pneus de carro e moto. Não aceito pneu de trator.' }
        ]
    };

    const comentariosData = {
        'Comprador A (PET)': [
            { autor: 'Catador 1', texto: 'Pagou certinho!', thumbs: '👍' },
            { autor: 'Catador 2', texto: 'Veio buscar rápido.', thumbs: '👍' }
        ],
        'Sucatas B (PET)': [
            { autor: 'Catador 8', texto: 'Tudo certo.', thumbs: '👍' },
        ],
        'Comprador C (PEAD)': [
            { autor: 'Catador 3', texto: 'A balança estava estranha...', thumbs: '👎' }
        ],
        'Comprador D (Vidro)': [
            { autor: 'Catador 4', texto: 'Pagamento na hora, recomendo.', thumbs: '👍' }
        ],
        'Comprador E (Papelão)': [
             { autor: 'Catador 5', texto: 'Muito exigente com o material, mas paga bem.', thumbs: '👍' }
        ],
        'Comprador F (Alumínio)': [
             { autor: 'Catador 6', texto: 'Preço justo e paga na hora!', thumbs: '👍' }
        ],
        'Comprador G (Borracha)': [
             { autor: 'Catador 7', texto: 'Demorou pra buscar.', thumbs: '👎' }
        ]
    }

    const secaoPrincipal = document.getElementById('secao-principal');
    const secaoDetalheMaterial = document.getElementById('detalhe-material');
    const secaoDetalheComprador = document.getElementById('detalhe-comprador');
    const secaoDetalheComentarios = document.getElementById('detalhe-comentarios');

    const botoesVerMais = document.querySelectorAll('.buscar-compradores__ver-mais');
    const linksMaterial = document.querySelectorAll('.cartao-material'); 
    const inputFiltroCompradores = document.getElementById('filtro-compradores'); 

    const btnVoltarPrincipal = document.getElementById('voltar-para-principal');
    const btnVoltarMateriais = document.getElementById('voltar-para-materiais');
    const btnVoltarComprador = document.getElementById('voltar-para-comprador');
    
    const containerTituloMaterial = document.getElementById('material-titulo');
    const containerSubtipos = document.getElementById('conteudo-material');
    const containerComprador = document.getElementById('conteudo-comprador');
    const containerComentarios = document.getElementById('conteudo-comentarios');

    let compradoresAtuais = []; 

    // Função para mostrar a tela de Subtipos 
    function mostrarDetalhesMaterial(materialId) {
        const data = materiaisData[materialId];
        if (!data) return;
        
        containerSubtipos.innerHTML = '';
        containerTituloMaterial.textContent = data.titulo;

        data.subtipos.forEach(subtipo => {
            const cardHTML = `
                <div class="subtipo-card" data-subtipo="${subtipo.nome}">
                    <img src="${subtipo.img}" alt="${subtipo.nome}">
                    <strong>${subtipo.nome}</strong>
                    ${subtipo.codigoImg ? `<img src="${subtipo.codigoImg}" alt="Símbolo ${subtipo.nome}" class="subtipo-card__simbolo">` : ''}
                </div>
            `;
            containerSubtipos.innerHTML += cardHTML;
        });

        adicionarListenersSubtipos();

        secaoPrincipal.classList.add('hidden');
        secaoDetalheMaterial.classList.remove('hidden');
    }

    // "desenha" os compradores na tela
    function renderizarCompradores(listaDeCompradores) {
        containerComprador.innerHTML = ''; 

        if (listaDeCompradores.length === 0) {
            containerComprador.innerHTML = '<h3 class="text-center p-3">Nenhum comprador encontrado.</h3>';
            return;
        }

        listaDeCompradores.forEach(comprador => {
            const cardHTML = `
                <div class="comprador-card">
                    <div class="comprador-header">
                        <div class="comprador-avatar">
                            <span class="material-icons">${comprador.avatar}</span>
                        </div>
                        <div class="comprador-info">
                            <h3>${comprador.nome}</h3>
                            <span>Avaliação: ${comprador.avaliacao} ⭐</span>
                        </div>
                        <div class="comprador-preco">
                            ${comprador.preco}
                        </div>
                    </div>
                    <p>${comprador.infos}</p>
                </div>

                <div class="historico-card">
                    <h4>Histórico de compras 📊</h4>
                    <p>Aqui vai o histórico de compras...</p>
                    <a class="btn-comentarios" data-comprador-id="${comprador.nome}">Comentários >></a>
                </div>
            `;
            containerComprador.innerHTML += cardHTML;
        });
        
        // REMOVEMOS A CHAMADA PARA adicionarListenerComentarios() DAQUI
    }


    // FUNÇÃO ATUALIZADA: Agora ela prepara a página de compradores
    function mostrarPaginaCompradores(subtipoId) {
        compradoresAtuais = compradoresData[subtipoId] || [];
        inputFiltroCompradores.value = '';
        renderizarCompradores(compradoresAtuais);
        secaoDetalheMaterial.classList.add('hidden');
        secaoDetalheComprador.classList.remove('hidden');
    }

    // Função para mostrar a tela de Comentários 
    function mostrarComentarios(compradorId) {
        const data = comentariosData[compradorId];
        containerComentarios.innerHTML = ''; 

        if (!data) {
            containerComentarios.innerHTML = '<h3 class="text-center p-3">Nenhum comentário para este comprador.</h3>';
        } else {
            data.forEach(comentario => {
                const cardHTML = `
                    <div class="comentario-card">
                        <div class="comprador-header">
                            <div class="comprador-avatar">
                                <span class="material-icons">account_circle</span>
                            </div>
                            <div class="comprador-info">
                                <h3>${comentario.autor}</h3>
                            </div>
                            <div class="comprador-preco">
                                ${comentario.thumbs}
                            </div>
                        </div>
                        <p>${comentario.texto}</p>
                    </div>
                `;
                containerComentarios.innerHTML += cardHTML;
            });
        }

        secaoDetalheComprador.classList.add('hidden');
        secaoDetalheComentarios.classList.remove('hidden');
    }

    // Adiciona clique nos cards da tela principal (Ver Mais e Imagem)
    botoesVerMais.forEach(botao => {
        botao.addEventListener('click', (e) => {
            const materialId = e.target.dataset.material;
            if (materialId) mostrarDetalhesMaterial(materialId);
        });
    });

    linksMaterial.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); 
            const materialId = e.currentTarget.dataset.material;
            if (materialId) mostrarDetalhesMaterial(materialId);
        });
    });

    // Adiciona clique nos cards de subtipo (criados dinamicamente)
    function adicionarListenersSubtipos() {
        document.querySelectorAll('.subtipo-card').forEach(card => {
            // Limpa listeners antigos (precaução)
            const cardClone = card.cloneNode(true);
            card.parentNode.replaceChild(cardClone, card);

            // Adiciona o listener no clone
            cardClone.addEventListener('click', (e) => {
                const subtipoId = e.currentTarget.dataset.subtipo;
                if (subtipoId) {
                    mostrarPaginaCompradores(subtipoId);
                }
            });
        });
    }

    btnVoltarPrincipal.addEventListener('click', () => {
        secaoDetalheMaterial.classList.add('hidden');
        secaoPrincipal.classList.remove('hidden');
    });

    btnVoltarMateriais.addEventListener('click', () => {
        secaoDetalheComprador.classList.add('hidden');
        secaoDetalheMaterial.classList.remove('hidden');
    });

    btnVoltarComprador.addEventListener('click', () => {
        secaoDetalheComentarios.classList.add('hidden');
        secaoDetalheComprador.classList.remove('hidden');
    });

    // Listener para o input de filtro de compradores
    inputFiltroCompradores.addEventListener('keyup', (e) => {
        const termoBusca = e.target.value.toLowerCase();
        
        const compradoresFiltrados = compradoresAtuais.filter(comprador => {
            return comprador.nome.toLowerCase().includes(termoBusca) ||
                   comprador.infos.toLowerCase().includes(termoBusca);
        });
        
        renderizarCompradores(compradoresFiltrados);
    });

    containerComprador.addEventListener('click', (e) => {
        // Verifica se o elemento clicado (ou um pai próximo) é o .btn-comentarios
        const botaoAlvo = e.target.closest('.btn-comentarios');

        if (botaoAlvo) {
            // Se for, pega o ID e chama a função
            const compradorId = botaoAlvo.dataset.compradorId;
            if (compradorId) {
                mostrarComentarios(compradorId);
            }
        }
    });

});