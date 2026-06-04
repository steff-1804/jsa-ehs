let matriz = JSON.parse(localStorage.getItem("matriz_jsa") || "[]");
let peligrosActividad = [];
let fotoActividadBase64 = "";

window.onload = function () {
    renderTabla();
};

function guardarLocal() {
    localStorage.setItem(
        "matriz_jsa",
        JSON.stringify(matriz)
    );
}

function calcularRPN(sev, likl, cont) {
    return Number(sev) * Number(likl) * Number(cont);
}

function colorRPN(rpn) {
    if (rpn <= 10) return "bajo";
    if (rpn <= 30) return "medio";
    return "alto";
}

function copiarHazard() {
    const select = document.getElementById("hazard_select");
    const peligro = document.getElementById("peligro");

    if (select.value === "Otro") {
        peligro.value = "";
        peligro.focus();
    } else {
        peligro.value = select.value;
    }
}

function configurarFotoInput(id) {

    const elemento = document.getElementById(id);

    if (!elemento) return;

    elemento.addEventListener("change", function () {

        const archivo = this.files[0];

        if (!archivo) return;

        const reader = new FileReader();

        reader.onload = function (e) {

            fotoActividadBase64 = e.target.result;

            const preview = document.getElementById("preview_foto");

            if (preview) {
                preview.src = fotoActividadBase64;
                preview.style.display = "block";
            }
        };

        reader.readAsDataURL(archivo);
    });
}

configurarFotoInput("foto_upload");
configurarFotoInput("foto_camera");

function agregarPeligroAActividad() {

    const peligro = document.getElementById("peligro").value.trim();
    const consecuencia = document.getElementById("consecuencia").value.trim();

    if (!peligro) {
        alert("Ingrese un peligro");
        return;
    }

    if (!consecuencia) {
        alert("Ingrese una consecuencia");
        return;
    }

    const item = {
        peligro: peligro,
        consecuencia: consecuencia,
        tipo_riesgo: document.getElementById("tipo_riesgo").value,
        sev: document.getElementById("sev").value,
        likl: document.getElementById("likl").value,
        cont: document.getElementById("cont").value,
        existing_controls: document.getElementById("existing_controls").value,
        recommended_controls: document.getElementById("recommended_controls").value,
        sev_post: document.getElementById("sev_post").value,
        likl_post: document.getElementById("likl_post").value,
        cont_post: document.getElementById("cont_post").value
    };

    peligrosActividad.push(item);

    renderPeligrosTemporales();

    document.getElementById("peligro").value = "";
    document.getElementById("consecuencia").value = "";
}

function renderPeligrosTemporales() {

    const tbody = document.querySelector("#tabla_peligros_temp tbody");

    if (!tbody) return;

    tbody.innerHTML = "";

    peligrosActividad.forEach((item, index) => {

        const rpn = calcularRPN(
            item.sev,
            item.likl,
            item.cont
        );

        tbody.innerHTML += `
        <tr>
            <td>${item.peligro}</td>
            <td>${item.consecuencia}</td>
            <td>${item.tipo_riesgo}</td>
            <td>${item.sev}</td>
            <td>${item.likl}</td>
            <td>${item.cont}</td>
            <td>${rpn}</td>
            <td>
                <button onclick="eliminarPeligroTemporal(${index})">
                    X
                </button>
            </td>
        </tr>
        `;
    });
}

function eliminarPeligroTemporal(index) {

    peligrosActividad.splice(index, 1);

    renderPeligrosTemporales();
}

function guardarActividadConPeligros() {

    const area = document.getElementById("area").value.trim();
    const actividad = document.getElementById("actividad").value.trim();

    if (!area || !actividad) {
        alert("Complete área y actividad");
        return;
    }

    if (peligrosActividad.length === 0) {
        alert("Agregue al menos un peligro");
        return;
    }

    peligrosActividad.forEach((peligro, index) => {

        matriz.push({
            area: area,
            actividad: actividad,
            foto: index === 0 ? fotoActividadBase64 : "",
            ...peligro
        });
    });

    guardarLocal();

    renderTabla();

    peligrosActividad = [];

    renderPeligrosTemporales();

    document.getElementById("area").value = "";
    document.getElementById("actividad").value = "";

    fotoActividadBase64 = "";

    const preview = document.getElementById("preview_foto");

    if (preview) {
        preview.style.display = "none";
    }
}

function renderTabla() {

    const tbody = document.querySelector("#tabla tbody");

    if (!tbody) return;

    tbody.innerHTML = "";

    matriz.forEach((item, index) => {

        const rpn = calcularRPN(
            item.sev,
            item.likl,
            item.cont
        );

        const rpnPost = calcularRPN(
            item.sev_post,
            item.likl_post,
            item.cont_post
        );

        tbody.innerHTML += `
        <tr>
            <td>${item.area}</td>

            <td>
                ${
                    item.foto
                    ? `<img src="${item.foto}" width="80">`
                    : ""
                }
            </td>

            <td>${item.actividad}</td>
            <td>${item.peligro}</td>
            <td>${item.consecuencia}</td>
            <td>${item.tipo_riesgo}</td>
            <td>${item.sev}</td>
            <td>${item.likl}</td>
            <td>${item.existing_controls}</td>
            <td>${item.cont}</td>
            <td>${rpn}</td>
            <td>${item.recommended_controls}</td>
            <td>${item.sev_post}</td>
            <td>${item.likl_post}</td>
            <td>${item.cont_post}</td>
            <td>${rpnPost}</td>

            <td>
                <button onclick="eliminarFila(${index})">
                    X
                </button>
            </td>
        </tr>
        `;
    });
}

function eliminarFila(index) {

    matriz.splice(index, 1);

    guardarLocal();

    renderTabla();
}

async function exportarExcel() {

    const formData = new FormData();

    formData.append(
        "data",
        JSON.stringify(matriz)
    );

    const response = await fetch(
        "/exportar_excel",
        {
            method: "POST",
            body: formData
        }
    );

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "Matriz_JSA.xlsx";

    document.body.appendChild(a);

    a.click();

    a.remove();

    window.URL.revokeObjectURL(url);
}

function limpiarTodo() {

    if (!confirm("¿Borrar toda la matriz?")) return;

    matriz = [];

    guardarLocal();

    renderTabla();
}
