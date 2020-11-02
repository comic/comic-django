import {Inspector, Runtime} from "https://cdn.jsdelivr.net/npm/@observablehq/runtime@4/dist/runtime.js";

if (window.self !== window.top) {
    import(JSON.parse(document.getElementById("observableNotebook").textContent)).then(
        module => {
            const evaluations = JSON.parse(document.getElementById("evaluations").textContent)
            const selectedCells = JSON.parse(document.getElementById("observableCells").textContent)
            const runtime = new Runtime()
            let main

            if (selectedCells.length === 1 && selectedCells.every((c) => c === "*")) {
                const cell = document.querySelector("#observableCell")
                cell.textContent = ""
                main = runtime.module(module.default, Inspector.into(cell));
            } else {
                main = runtime.module(module.default, (name) => {
                    let selected = selectedCells.indexOf(name)
                    if (selected > -1) {
                        const id = selectedCells[selected].replace(/[\s*]/g, "")  // remove spaces and * from cell names
                        return new Inspector(document.querySelector("#observableCell" + id))
                    }
                });
            }

            main.redefine("parse_results", evaluations)
        }
    )
}
