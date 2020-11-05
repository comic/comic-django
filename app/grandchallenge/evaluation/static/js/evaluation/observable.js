import {Inspector, Runtime} from "https://cdn.jsdelivr.net/npm/@observablehq/runtime@4/dist/runtime.js";

if (window.self !== window.top) {
    const observableNotebookJS = JSON.parse(document.getElementById("observableNotebookJS").textContent);
    const observableNotebookEdit = JSON.parse(document.getElementById("observableNotebookEdit").textContent);
    const selectedCells = JSON.parse(document.getElementById("observableCells").textContent);
    const evaluations = JSON.parse(document.getElementById("evaluations").textContent);

    import(observableNotebookJS).then(
        module => {
            const runtime = new Runtime()
            let main

            if (selectedCells.length === 1 && selectedCells.every((c) => c === "*")) {
                const cell = document.querySelector("#observableCell");
                cell.textContent = "";
                main = runtime.module(module.default, Inspector.into(cell));
            } else {
                main = runtime.module(module.default, (name) => {
                    let selected = selectedCells.indexOf(name);
                    if (selected > -1) {
                        const id = selectedCells[selected].replace(/[\s*]/g, "");  // remove spaces and * from cell names
                        return new Inspector(document.querySelector("#observableCell" + id));
                    }
                });
            }

            main.redefine("parse_results", evaluations);
        }
    )

    const observableEditLink = document.getElementById("observableEditLink");
    if (observableEditLink !== undefined) {
        let search = new URLSearchParams(evaluations.map(e => ["pk", e.pk]));
        observableEditLink.href = `${observableNotebookEdit}?${search}`;
    }
}
