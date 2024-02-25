import { RecutWord } from "./recut-word";
import { Dictionary, RecutService } from "./recut.service";

const formElement: HTMLFormElement = document.querySelector('form')!;
const spinner: HTMLDivElement = document.getElementById('spinner') as HTMLDivElement;
const submitButton: HTMLButtonElement = document.getElementById('submit') as HTMLButtonElement;
const recutButton: HTMLButtonElement = document.getElementById('recut') as HTMLButtonElement;
const recutText: HTMLTextAreaElement = document.getElementById('recut-text') as HTMLTextAreaElement;
const listOfThings = document.getElementById('list-of-uploaded') as HTMLUListElement;
const recutService = RecutService.Instance;

var currentState: Dictionary<Array<RecutWord>> = {};

recutService.getState()
  .then(state => {
    currentState = state
    listOfThings.innerHTML = "";
    for(let movie in currentState) {
      listOfThings.innerHTML = listOfThings.innerHTML + `
      <li>${movie} ${currentState[movie][0].confidence}</li>
      `
    }
  })

formElement!.addEventListener('submit', (event: any) => {
    spinner.setAttribute("class", "spinner")
    submitButton.disabled = true
    const response = recutService.analyze(event)
            .then( res => {
              console.log("Analysis finsihed", res)
              submitButton.disabled = false
              spinner.setAttribute("class", "")
            })

    event.preventDefault();
});

recutButton.addEventListener("click", (event: any) => {
  recutService.recut(recutText.value)
    .then( blob => {
      var file = window.URL.createObjectURL(blob);
      window.location.assign(file);
      spinner.removeAttribute("class");
      submitButton.disabled = false
  });
})