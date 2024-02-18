const formElement = document.querySelector('form');
formElement!.addEventListener('submit', (event: any) => {
    const form = event.currentTarget;
    const url = new URL(form.action);
    const formData = new FormData(form);
    
    /** @type {Parameters<fetch>[1]} */
    const fetchOptions = {
      method: form.method,
      body: formData,
    };
    
    const response = fetch(url, fetchOptions)
            .then( res => res.blob() )
            .then( blob => {
                var file = window.URL.createObjectURL(blob);
                window.location.assign(file);
            });

    event.preventDefault();
});