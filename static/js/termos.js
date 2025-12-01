const termos = document.querySelector('#termosDeUso');

termos.addEventListener('click', () =>{
    Swal.fire({
        title: 'Termo de Uso',
        icon: 'info',
        width: 500,
        html: `
            <div style="text-align: left; text-align-last: left;">
                <p>Este é o termo de uso do site <strong>Recoopera</strong>. Ao utilizar este site, você concorda com os seguintes termos e condições:</p>
                
                <p class="text-muted">Se você tiver alguma dúvida sobre estes termos, entre em contato conosco.</p>
            </div>
        `,
        
        confirmButtonText: 'Entendido',
        confirmButtonColor: 'var(--verde-claro-medio)'
    });
})