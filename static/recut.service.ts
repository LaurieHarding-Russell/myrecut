import { RecutWord } from "./recut-word";

export type Dictionary<T = any> = {[name: string]: T }

export class RecutService {
    
    private static _instance: RecutService;

    private constructor() {
    }

    public static get Instance(){
        return this._instance || (this._instance = new this());
    }

    public analyze(event: any): Promise<Response> {
        const form = event.currentTarget;
        const url = new URL(form.action);
        const formData = new FormData(form);
        
        const fetchOptions = {
          method: form.method,
          body: formData,
        };
    
        return fetch(url, fetchOptions);
    }

    public recut(value: string): Promise<Blob> {

        return fetch("/recut", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({text: value})
            })
            .then( res => res.blob() )
    }

    public getState(): Promise<Dictionary<Array<RecutWord>>> {
        return fetch("/state")
            .then(response => response.json())
    }
}