const termos = document.querySelector('#termosDeUso');

termos.addEventListener('click', () =>{
    Swal.fire({
        title: 'Termo de Uso',
        icon: 'info', // Ícone de informação
        width: 500,   // Define uma largura maior para o texto caber bem
        
        // Usamos 'html' para inserir nosso texto formatado
        html: `
            <div style="text-align: left; text-align-last: left;">
                <p>Este é o termo de uso do site <strong>Recoopera</strong>. Ao utilizar este site, você concorda com os seguintes termos e condições:</p>
                
                <ul style="margin-top: 1.5em; margin-bottom: 1.5em; padding-left: 2em;">
                    <li><strong>Uso do Site:</strong> Você concorda em usar este site apenas para fins legais e de acordo com todas as leis aplicáveis.</li>
                    <li><strong>Propriedade Intelectual:</strong> Todo o conteúdo deste site, incluindo textos, imagens e logotipos, é protegido por direitos autorais e outras leis de propriedade intelectual.</li>
                    <li><strong>Privacidade:</strong> Respeitamos sua privacidade. Quaisquer informações pessoais coletadas serão tratadas de acordo com nossa Política de Privacidade.</li>
                    <li><strong>Limitação de Responsabilidade:</strong> Não nos responsabilizamos por quaisquer danos diretos ou indiretos decorrentes do uso deste site.</li>
                    <li><strong>Alterações nos Termos:</strong> Reservamo-nos o direito de modificar estes termos a qualquer momento. Recomendamos que você revise esta página periodicamente.</li>
                </ul>
                
                <p>Se você tiver alguma dúvida sobre estes termos, entre em contato conosco.</p>
            </div>
        `,
        
        confirmButtonText: 'Entendido',
        confirmButtonColor: 'var(--verde-claro-medio)'
    });
})