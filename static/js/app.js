function mostrarPagina(id, numeroPagina) {
    document.querySelectorAll(".page-step").forEach(p => p.classList.remove("active"));
    document.getElementById(id).classList.add("active");

    const barra = document.getElementById("barraProgreso");
    const estado = document.getElementById("estadoPagina");

    if (numeroPagina === 1) {
        barra.style.width = "33.33%";
        estado.innerText = "Página 1 de 3";
    }

    if (numeroPagina === 2) {
        barra.style.width = "66.66%";
        estado.innerText = "Página 2 de 3";
    }

    if (numeroPagina === 3) {
        barra.style.width = "100%";
        estado.innerText = "Página 3 de 3";
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}
