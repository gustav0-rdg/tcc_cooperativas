document.addEventListener('DOMContentLoaded', () => {

    // Contém os dados dos subtipos de material, com imagens da internet
const materiaisData = {
        'plastico': {
            titulo: 'Plásticos',
            subtipos: [
                { 
                    nome: 'PET', 
                    img: '../static/imgs/subtipos/pet.png', // <-- Caminho local
                    codigo: '01', 
                    codigoImg: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Symbol_Resin_Code_01_PET.svg/200px-Symbol_Resin_Code_01_PET.svg.png' 
                },
                { 
                    nome: 'PEAD', 
                    img: '../static/imgs/subtipos/pead.png', // <-- Caminho local
                    codigo: '02', 
                    codigoImg: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnH2VmFODOdx2uO6FYguSzvsEM61Aqvnxmbw&s' 
                },
                {       
                    nome: 'PVC', 
                    img: '../static/imgs/subtipos/pvc.png', // <-- Caminho local
                    codigo: '03', 
                    codigoImg: 'https://www.issosignifica.com/plastico-3-pvc-w400.jpg' 
                },
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
            subtipos: [
                { nome: 'Palete', img: '../static/imgs/subtipos/palete.png', codigo: '', codigoImg: '' }
            ] 
        },
        'pilha': { 
            titulo: 'Pilhas e Baterias', 
            subtipos: [
                { nome: 'Pilha AA', img: '../static/imgs/subtipos/pilha.png', codigo: '', codigoImg: '' }
            ] 
        },
        'borracha': { 
            titulo: 'Borracha', 
            subtipos: [
                { nome: 'Pneu', img: '../static/imgs/subtipos/pneu.png', codigo: '', codigoImg: '' } 
            ] 
        },
        'papelao': { 
            titulo: 'Papelão', 
            subtipos: [
                { nome: 'Caixa', img: '../static/imgs/subtipos/caixa-papelao.png', codigo: '', codigoImg: '' }
            ] 
        },
        'vidro': { 
            titulo: 'Vidro', 
            subtipos: [
                { nome: 'Garrafa', img: '../static/imgs/subtipos/garrafa-vidro.png', codigo: '', codigoImg: '' }
            ] 
        },
    };

    const compradoresData = {
        'PET': [
            { 
                nome: 'Comprador A (PET)', 
                avaliacao: 4.5, 
                preco: 'R$ 0,50/kg', 
                avatar: 'person', 
                infos: 'Compro PET limpo e prensado. Pagamento na hora. Entre em contato para grandes volumes.'
            }
        ],
        'PEAD': [
             { 
                nome: 'Comprador B (PEAD)', 
                avaliacao: 4.2, 
                preco: 'R$ 0,40/kg', 
                avatar: 'person', 
                infos: 'Retiro no local acima de 100kg. Aceito embalagens de detergente, amaciante, etc.'
            }
        ],
        'Garrafa': [
             { 
                nome: 'Comprador C (Vidro)', 
                avaliacao: 4.8, 
                preco: 'R$ 0,15/kg', 
                avatar: 'store', 
                infos: 'Compro garrafas verdes, transparentes e marrons. Não pego vidro quebrado.'
            }
        ],
        'Caixa': [
             { 
                nome: 'Comprador D (Papelão)', 
                avaliacao: 4.6, 
                preco: 'R$ 0,25/kg', 
                avatar: 'store', 
                infos: 'Apenas papelão seco e amarrado.'
            }
        ]
        // Aqui vai a lista de mais compradores
    };

    const comentariosData = {
        'Comprador A (PET)': [
            { autor: 'Catador 1', texto: 'Pagou certinho!', thumbs: '👍' },
            { autor: 'Catador 2', texto: 'Veio buscar rápido.', thumbs: '👍' }
        ],
        'Comprador B (PEAD)': [
            { autor: 'Catador 3', texto: 'A balança estava estranha...', thumbs: '👎' }
        ],
        'Comprador C (Vidro)': [
            { autor: 'Catador 4', texto: 'Pagamento na hora, recomendo.', thumbs: '👍' }
        ],
        'Comprador D (Papelão)': [
             { autor: 'Catador 5', texto: 'Muito exigente com o material, mas paga bem.', thumbs: '👍' }
        ]
    }

    // Pegamos todas as seções e botões que vamos usar
    const secaoPrincipal = document.getElementById('secao-principal');
    const secaoDetalheMaterial = document.getElementById('detalhe-material');
    const secaoDetalheComprador = document.getElementById('detalhe-comprador');
    const secaoDetalheComentarios = document.getElementById('detalhe-comentarios');

    const botoesVerMais = document.querySelectorAll('.buscar-compradores__ver-mais');
    const linksMaterial = document.querySelectorAll('.cartao-material'); // Para clicar na imagem

    const btnVoltarPrincipal = document.getElementById('voltar-para-principal');
    const btnVoltarMateriais = document.getElementById('voltar-para-materiais');
    const btnVoltarComprador = document.getElementById('voltar-para-comprador');
    
    const containerTituloMaterial = document.getElementById('material-titulo');
    const containerSubtipos = document.getElementById('conteudo-material');
    const containerComprador = document.getElementById('conteudo-comprador');
    const containerComentarios = document.getElementById('conteudo-comentarios');

    // Função para mostrar a tela de Subtipos (RF010)
    function mostrarDetalhesMaterial(materialId) {
        const data = materiaisData[materialId];
        if (!data) {
            console.error('Dados não encontrados para:', materialId);
            return;
        }
        
        // 1. Limpa o conteúdo anterior e define o título
        containerSubtipos.innerHTML = '';
        containerTituloMaterial.textContent = data.titulo;

        // 2. Cria o HTML para cada subtipo
        data.subtipos.forEach(subtipo => {
            const cardHTML = `
                <div class="subtipo-card" data-subtipo="${subtipo.nome}">
                    <img src="${subtipo.img}" alt="${subtipo.nome}">
                    <strong>${subtipo.nome}</strong>
                    ${subtipo.codigoImg ? `<img src="${subtipo.codigoImg}" alt="Símbolo ${subtipo.nome}" class="subtipo-card__simbolo">` : ''}
                </div>
            `;
            // data-subtipo="${subtipo.nome}" é como passamos a informação para o próximo clique
            containerSubtipos.innerHTML += cardHTML;
        });

        // 3. Adiciona os 'ouvintes' de clique nos novos cards criados
        adicionarListenersSubtipos();

        // 4. Troca as telas
        secaoPrincipal.classList.add('hidden');
        secaoDetalheMaterial.classList.remove('hidden');
    }

    // Função para mostrar a tela de Compradores (RF011)
    function mostrarCompradores(subtipoId) {
        const data = compradoresData[subtipoId];
        
        // Limpa o container
        containerComprador.innerHTML = '';

        if (!data) {
            console.warn('Nenhum comprador encontrado para:', subtipoId);
            containerComprador.innerHTML = '<h3 class="text-center p-3">Nenhum comprador encontrado para este material.</h3>';
        } else {
            // Cria o HTML para cada comprador
            data.forEach(comprador => {
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
        }
        
        // Adiciona listener para o botão "Comentários"
        adicionarListenerComentarios();

        // Troca as telas
        secaoDetalheMaterial.classList.add('hidden');
        secaoDetalheComprador.classList.remove('hidden');
    }

    // Função para mostrar a tela de Comentários (RF0NSE1)
    function mostrarComentarios(compradorId) {
        const data = comentariosData[compradorId];

        // Limpa o container
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

        // Troca as telas
        secaoDetalheComprador.classList.add('hidden');
        secaoDetalheComentarios.classList.remove('hidden');
    }

    // Adiciona clique em todos os botões "Ver mais" da tela principal
    botoesVerMais.forEach(botao => {
        botao.addEventListener('click', (e) => {
            const materialId = e.target.dataset.material;
            if (materialId) {
                mostrarDetalhesMaterial(materialId);
            }
        });
    });

    // Adiciona clique em todas as IMAGENS (links <a>) da tela principal
    linksMaterial.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Impede o link de recarregar a página
            const materialId = e.currentTarget.dataset.material;
            if (materialId) {
                mostrarDetalhesMaterial(materialId);
            }
        });
    });

    // Adiciona clique nos cards de subtipo (criados dinamicamente)
    function adicionarListenersSubtipos() {
        document.querySelectorAll('.subtipo-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Pega o 'data-subtipo' que definimos no cardHTML
                const subtipoId = e.currentTarget.dataset.subtipo;
                if (subtipoId) {
                    mostrarCompradores(subtipoId);
                }
            });
        });
    }

    // Adiciona clique no link "Comentários >>" (criado dinamicamente)
    function adicionarListenerComentarios() {
        // Limpa listeners antigos para evitar duplicação
        document.querySelectorAll('.btn-comentarios').forEach(btn => {
            btn.replaceWith(btn.cloneNode(true));
        });
        
        // Adiciona o novo listener
        document.querySelectorAll('.btn-comentarios').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const compradorId = e.currentTarget.dataset.compradorId;
                if(compradorId) {
                    mostrarComentarios(compradorId);
                }
            });
        });
    }


    // --- 5. BOTÕES DE VOLTAR ---

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

});