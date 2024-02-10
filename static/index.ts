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
    
    fetch(url, fetchOptions);

    event.preventDefault();
});