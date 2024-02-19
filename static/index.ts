const formElement: HTMLFormElement = document.querySelector('form')!;
const spinner: HTMLDivElement = document.getElementById('spinner') as HTMLDivElement;
const submitButton: HTMLButtonElement = document.getElementById('submit') as HTMLButtonElement;

formElement!.addEventListener('submit', (event: any) => {
    const form = event.currentTarget;
    const url = new URL(form.action);
    const formData = new FormData(form);
    
    /** @type {Parameters<fetch>[1]} */
    const fetchOptions = {
      method: form.method,
      body: formData,
    };

    spinner.setAttribute("class", "spinner")
    submitButton.disabled = true
    const response = fetch(url, fetchOptions)
            .then( res => res.blob() )
            .then( blob => {
                var file = window.URL.createObjectURL(blob);
                window.location.assign(file);
                spinner.removeAttribute("class");
                submitButton.disabled = false
            });

    event.preventDefault();
});