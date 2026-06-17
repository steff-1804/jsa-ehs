let infoGeneral = JSON.parse(localStorage.getItem("infoGeneralJSA") || "{}");
let actividades = JSON.parse(localStorage.getItem("actividadesJSA") || "[]");
let fotosTemporales = [];
let peligrosTemporales = [];

window.onload = function () {
    cargarInfoGuardada();
    renderFotosTemporales();
    renderPeligrosTemporales();
    renderActividades();
    mostrarPagina("pagina1", 1);
};

function guardarLocal() {
    localStorage.setItem("infoGeneralJSA", JSON.stringify(infoGeneral));
    localStorage.setItem("actividadesJSA", JSON.stringify(actividades));
}

function mostrarPagina(id, numeroPagina) {
    document.querySelectorAll(".page-step").forEach(p => p.classList.remove("active"));

    const destino = document.getElementById(id);

    if (!destino) {
        alert("No existe la página: " + id);
        return;
    }

    destino.classList.add("active");

    const barra = document.getElementById("barraProgreso");
    const estado = document.getElementById("estadoPagina");

    if (barra) {
        barra.style.width = numeroPagina === 1 ? "33.33%" : numeroPagina === 2 ? "66.66%" : "100%";
    }

    if (estado) {
        estado.innerText = "Página " + numeroPagina + " de 3";
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}

function irPagina1() {
    mostrarPagina("pagina1", 1);
}

function irPagina2() {
    infoGeneral = {
        area: document.getElementById("area").value.trim(),
        miembros: document.getElementById("miembros").value.trim(),
        fecha: document.getElementById("fecha").value,
        descripcion: document.getElementById("descripcion").value.trim()
    };

    if (!infoGeneral.area || !infoGeneral.miembros || !infoGeneral.fecha || !infoGeneral.descripcion) {
        alert("Complete toda la información de la página 1.");
        return;
    }

    guardarLocal();
    mostrarPagina("pagina2", 2);
}

function irPagina3() {
    if (actividades.length === 0) {
        alert("Debe agregar al menos una actividad.");
        return;
    }

    document.getElementById("res_area").innerText = infoGeneral.area;
    document.getElementById("res_miembros").innerText = infoGeneral.miembros;
    document.getElementById("res_fecha").innerText = infoGeneral.fecha;
    document.getElementById("res_descripcion").innerText = infoGeneral.descripcion;

    renderTablaJSA();
    mostrarPagina("pagina3", 3);
}

function cargarInfoGuardada() {
    document.getElementById("area").value = infoGeneral.area || "";
    document.getElementById("miembros").value = infoGeneral.miembros || "";
    document.getElementById("fecha").value = infoGeneral.fecha || "";
    document.getElementById("descripcion").value = infoGeneral.descripcion || "";
}

function leerFotos(files) {
    return Promise.all([...files].map(file => {
        return new Promise(resolve => {
            const reader = new FileReader();

            reader.onload = function (event) {
                const img = new Image();

                img.onload = function () {
                    const canvas = document.createElement("canvas");
                    const maxWidth = 1600;
                    const maxHeight = 1100;

                    let width = img.width;
                    let height = img.height;

                    const scale = Math.min(maxWidth / width, maxHeight / height, 1);

                    width = Math.round(width * scale);
                    height = Math.round(height * scale);

                    canvas.width = width;
                    canvas.height = height;

                    const ctx = canvas.getContext("2d");
                    ctx.imageSmoothingEnabled = true;
                    ctx.imageSmoothingQuality = "high";
                    ctx.drawImage(img, 0, 0, width, height);

                    resolve(canvas.toDataURL("image/jpeg", 0.80));
                };

                img.src = event.target.result;
            };

            reader.readAsDataURL(file);
        });
    }));
}

document.addEventListener("change", async function (event) {
    if (event.target.id === "fotos" || event.target.id === "foto_camara") {
        const nuevasFotos = await leerFotos(event.target.files);
        fotosTemporales.push(...nuevasFotos);
        renderFotosTemporales();
        event.target.value = "";
    }
});

function renderFotosTemporales() {
    const contenedor = document.getElementById("previewFotos");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    fotosTemporales.forEach((foto, index) => {
        contenedor.innerHTML += `
            <div class="foto-item">
                <img src="${foto}">
                <button type="button" class="danger small" onclick="eliminarFotoTemporal(${index})">Eliminar</button>
            </div>
        `;
    });
}

function eliminarFotoTemporal(index) {
    fotosTemporales.splice(index, 1);
    renderFotosTemporales();
}

function agregarPeligroTemporal() {
    const peligro = document.getElementById("peligro").value.trim();
    const consecuencia = document.getElementById("consecuencia").value.trim();

    if (!peligro || !consecuencia) {
        alert("Ingrese peligro y consecuencia.");
        return;
    }

    peligrosTemporales.push({
        peligro,
        consecuencia,
        sev: 1,
        likl: 1,
        cont: 1,
        existing_controls: "",
        recommended_controls: "",
        sev_post: 1,
        likl_post: 1,
        cont_post: 1
    });

    document.getElementById("peligro").value = "";
    document.getElementById("consecuencia").value = "";

    renderPeligrosTemporales();
}

function renderPeligrosTemporales() {
    const contenedor = document.getElementById("listaPeligrosTemp");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    peligrosTemporales.forEach((peligro, index) => {
        contenedor.innerHTML += `
            <div class="activity-item">
                <b>Peligro:</b> ${peligro.peligro}<br>
                <b>Consecuencia:</b> ${peligro.consecuencia}<br>
                <button type="button" class="danger small" onclick="eliminarPeligroTemporal(${index})">Eliminar peligro</button>
            </div>
        `;
    });
}

function eliminarPeligroTemporal(index) {
    peligrosTemporales.splice(index, 1);
    renderPeligrosTemporales();
}

function guardarActividad() {
    const actividad = document.getElementById("actividad").value.trim();

    if (!actividad) {
        alert("Ingrese la actividad.");
        return;
    }

    if (peligrosTemporales.length === 0) {
        alert("Agregue al menos un peligro.");
        return;
    }

    actividades.push({
        actividad: actividad,
        fotos: fotosTemporales,
        peligros: peligrosTemporales
    });

    fotosTemporales = [];
    peligrosTemporales = [];

    document.getElementById("actividad").value = "";
    document.getElementById("peligro").value = "";
    document.getElementById("consecuencia").value = "";

    guardarLocal();
    renderFotosTemporales();
    renderPeligrosTemporales();
    renderActividades();

    alert("Actividad guardada correctamente.");
}

function renderActividades() {
    const contenedor = document.getElementById("listaActividades");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    actividades.forEach((actividad, index) => {
        contenedor.innerHTML += `
            <div class="activity-item activity-saved">
                <b>${index + 1}. ${actividad.actividad}</b><br>
                <small>Fotos: ${actividad.fotos.length}</small><br>
                <small>Peligros: ${actividad.peligros.length}</small><br>
                <button type="button" class="danger small" onclick="eliminarActividad(${index})">Eliminar actividad</button>
            </div>
        `;
    });
}

function eliminarActividad(index) {
    actividades.splice(index, 1);
    guardarLocal();
    renderActividades();
}

function selectNivel(valor, actividadIndex, peligroIndex, campo) {
    let html = `<select onchange="actualizarCampo(${actividadIndex}, ${peligroIndex}, '${campo}', this.value)">`;

    for (let i = 1; i <= 5; i++) {
        html += `<option value="${i}" ${Number(valor) === i ? "selected" : ""}>${i}</option>`;
    }

    html += "</select>";
    return html;
}

function actualizarCampo(actividadIndex, peligroIndex, campo, valor) {
    actividades[actividadIndex].peligros[peligroIndex][campo] = Number(valor);
    guardarLocal();
    renderTablaJSA();
}

function actualizarTexto(actividadIndex, peligroIndex, campo, valor) {
    actividades[actividadIndex].peligros[peligroIndex][campo] = valor;
    guardarLocal();
}

function calcularRPN(sev, likl, cont) {
    return Number(sev) * Number(likl) * Number(cont);
}

function colorRPN(rpn) {
    if (rpn <= 10) return "bajo";
    if (rpn <= 30) return "medio";
    return "alto";
}

function renderTablaJSA() {
    const tbody = document.querySelector("#tablaJSA tbody");
    tbody.innerHTML = "";

    actividades.forEach((actividad, actividadIndex) => {
        const totalPeligros = actividad.peligros.length;

        actividad.peligros.forEach((peligro, peligroIndex) => {
            const rpn = calcularRPN(peligro.sev, peligro.likl, peligro.cont);
            const rpnPost = calcularRPN(peligro.sev_post, peligro.likl_post, peligro.cont_post);

            let columnaActividad = "";
            let columnaFotos = "";

            if (peligroIndex === 0) {
                const fotosHTML = actividad.fotos
                    .map(foto => `<img class="foto-mini" src="${foto}">`)
                    .join("");

                columnaActividad = `
                    <td rowspan="${totalPeligros}" class="celda-combinada actividad-combinada">
                        ${actividad.actividad}
                    </td>
                `;

                columnaFotos = `
                    <td rowspan="${totalPeligros}" class="celda-combinada fotos-combinadas">
                        ${fotosHTML}
                    </td>
                `;
            }

            tbody.innerHTML += `
                <tr>
                    ${columnaActividad}
                    ${columnaFotos}
                    <td>${peligro.peligro}</td>
                    <td>${peligro.consecuencia}</td>
                    <td>${selectNivel(peligro.sev, actividadIndex, peligroIndex, "sev")}</td>
                    <td>${selectNivel(peligro.likl, actividadIndex, peligroIndex, "likl")}</td>
                    <td><textarea onchange="actualizarTexto(${actividadIndex}, ${peligroIndex}, 'existing_controls', this.value)">${peligro.existing_controls || ""}</textarea></td>
                    <td>${selectNivel(peligro.cont, actividadIndex, peligroIndex, "cont")}</td>
                    <td class="${colorRPN(rpn)}">${rpn}</td>
                    <td><textarea onchange="actualizarTexto(${actividadIndex}, ${peligroIndex}, 'recommended_controls', this.value)">${peligro.recommended_controls || ""}</textarea></td>
                    <td>${selectNivel(peligro.sev_post, actividadIndex, peligroIndex, "sev_post")}</td>
                    <td>${selectNivel(peligro.likl_post, actividadIndex, peligroIndex, "likl_post")}</td>
                    <td>${selectNivel(peligro.cont_post, actividadIndex, peligroIndex, "cont_post")}</td>
                    <td class="${colorRPN(rpnPost)}">${rpnPost}</td>
                </tr>
            `;
        });
    });
}

async function exportarExcel() {
    const formData = new FormData();

    formData.append("info_general", JSON.stringify(infoGeneral));
    formData.append("actividades", JSON.stringify(actividades));

    try {
        const response = await fetch("/exportar_excel", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            alert("Error al exportar Excel: " + errorText);
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const enlace = document.createElement("a");
        enlace.href = url;
        enlace.download = "Matriz_JSA.xlsx";

        document.body.appendChild(enlace);
        enlace.click();
        enlace.remove();

        window.URL.revokeObjectURL(url);

    } catch (error) {
        alert("Error de conexión al exportar Excel: " + error.message);
    }
}

function limpiarTodo() {
    if (!confirm("¿Seguro que desea borrar toda la información?")) return;

    localStorage.removeItem("infoGeneralJSA");
    localStorage.removeItem("actividadesJSA");

    infoGeneral = {};
    actividades = [];
    fotosTemporales = [];
    peligrosTemporales = [];

    location.reload();
}
