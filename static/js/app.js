let infoGeneral = JSON.parse(localStorage.getItem("infoGeneralJSA") || "{}");
let actividades = JSON.parse(localStorage.getItem("actividadesJSA") || "[]");

window.onload = function () {
    cargarInfoGuardada();
    renderListaActividades();
};

function guardarLocal() {
    localStorage.setItem("infoGeneralJSA", JSON.stringify(infoGeneral));
    localStorage.setItem("actividadesJSA", JSON.stringify(actividades));
}

function mostrarPagina(id) {
    document.querySelectorAll(".page-step").forEach(p => p.classList.remove("active"));
    document.getElementById(id).classList.add("active");
}

function irPagina1() {
    mostrarPagina("pagina1");
}

function irPagina2() {
    infoGeneral = {
        area: document.getElementById("area").value.trim(),
        miembros: document.getElementById("miembros").value.trim(),
        fecha: document.getElementById("fecha").value,
        descripcion: document.getElementById("descripcion").value.trim()
    };

    if (!infoGeneral.area || !infoGeneral.miembros || !infoGeneral.fecha || !infoGeneral.descripcion) {
        alert("Complete toda la información general.");
        return;
    }

    guardarLocal();
    mostrarPagina("pagina2");
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
    mostrarPagina("pagina3");
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
            reader.onload = e => resolve(e.target.result);
            reader.readAsDataURL(file);
        });
    }));
}

async function agregarActividad() {
    const actividad = document.getElementById("actividad").value.trim();
    const peligro = document.getElementById("peligro").value.trim();
    const consecuencia = document.getElementById("consecuencia").value.trim();

    const fotosInput = document.getElementById("fotos").files;
    const fotoCamara = document.getElementById("foto_camara").files;

    if (!actividad || !peligro || !consecuencia) {
        alert("Complete actividad, peligro y consecuencia.");
        return;
    }

    const fotos1 = await leerFotos(fotosInput);
    const fotos2 = await leerFotos(fotoCamara);
    const fotos = [...fotos1, ...fotos2];

    actividades.push({
        actividad,
        peligro,
        consecuencia,
        fotos,
        sev: 1,
        likl: 1,
        cont: 1,
        existing_controls: "",
        recommended_controls: "",
        sev_post: 1,
        likl_post: 1,
        cont_post: 1
    });

    guardarLocal();
    renderListaActividades();

    document.getElementById("actividad").value = "";
    document.getElementById("peligro").value = "";
    document.getElementById("consecuencia").value = "";
    document.getElementById("fotos").value = "";
    document.getElementById("foto_camara").value = "";
}

function renderListaActividades() {
    const contenedor = document.getElementById("listaActividades");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    actividades.forEach((a, i) => {
        contenedor.innerHTML += `
            <div class="activity-item">
                <b>${i + 1}. ${a.actividad}</b><br>
                <small>${a.peligro} - ${a.consecuencia}</small><br>
                <button class="danger small" onclick="eliminarActividad(${i})">Eliminar</button>
            </div>
        `;
    });
}

function eliminarActividad(index) {
    actividades.splice(index, 1);
    guardarLocal();
    renderListaActividades();
}

function selectNivel(valor, index, campo) {
    let html = `<select onchange="actualizarCampo(${index}, '${campo}', this.value)">`;
    for (let i = 1; i <= 5; i++) {
        html += `<option value="${i}" ${Number(valor) === i ? "selected" : ""}>${i}</option>`;
    }
    html += `</select>`;
    return html;
}

function calcularRPN(sev, likl, cont) {
    return Number(sev) * Number(likl) * Number(cont);
}

function actualizarCampo(index, campo, valor) {
    actividades[index][campo] = valor;
    guardarLocal();
    renderTablaJSA();
}

function actualizarTexto(index, campo, valor) {
    actividades[index][campo] = valor;
    guardarLocal();
}

function renderTablaJSA() {
    const tbody = document.querySelector("#tablaJSA tbody");
    tbody.innerHTML = "";

    actividades.forEach((a, i) => {
        const rpn = calcularRPN(a.sev, a.likl, a.cont);
        const rpnPost = calcularRPN(a.sev_post, a.likl_post, a.cont_post);

        const fotosHTML = a.fotos.map(f => `<img class="foto-mini" src="${f}">`).join("");

        tbody.innerHTML += `
            <tr>
                <td>${a.actividad}</td>
                <td>${fotosHTML}</td>
                <td><b>${a.peligro}</b><br>${a.consecuencia}</td>
                <td>${selectNivel(a.sev, i, "sev")}</td>
                <td>${selectNivel(a.likl, i, "likl")}</td>
                <td><textarea onchange="actualizarTexto(${i}, 'existing_controls', this.value)">${a.existing_controls || ""}</textarea></td>
                <td>${selectNivel(a.cont, i, "cont")}</td>
                <td class="${colorRPN(rpn)}">${rpn}</td>
                <td><textarea onchange="actualizarTexto(${i}, 'recommended_controls', this.value)">${a.recommended_controls || ""}</textarea></td>
                <td>${selectNivel(a.sev_post, i, "sev_post")}</td>
                <td>${selectNivel(a.likl_post, i, "likl_post")}</td>
                <td>${selectNivel(a.cont_post, i, "cont_post")}</td>
                <td class="${colorRPN(rpnPost)}">${rpnPost}</td>
            </tr>
        `;
    });
}

function colorRPN(rpn) {
    if (rpn <= 10) return "bajo";
    if (rpn <= 30) return "medio";
    return "alto";
}

async function exportarExcel() {
    const formData = new FormData();
    formData.append("info_general", JSON.stringify(infoGeneral));
    formData.append("data", JSON.stringify(actividades));

    const response = await fetch("/exportar_excel", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Error al exportar Excel.");
        return;
    }

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
    if (!confirm("¿Seguro que desea borrar toda la información?")) return;

    localStorage.removeItem("infoGeneralJSA");
    localStorage.removeItem("actividadesJSA");

    infoGeneral = {};
    actividades = [];

    location.reload();
}
