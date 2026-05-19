(function () {
    var placeholders = {
        id_rut: "12.345.678-9",
        id_telefono: "+56 9 1234 5678",
        id_direccion: "Ej: Av. Principal 1234, Santiago",
        id_oficio: "Ej: Electricista, Gasfiter, Constructor",
        id_nombre_empresa: "Ej: Soluciones Integrales SpA"
    };

    Object.keys(placeholders).forEach(function (id) {
        var field = document.getElementById(id);
        if (field && !field.getAttribute("placeholder")) {
            field.setAttribute("placeholder", placeholders[id]);
        }
    });

    var form = document.querySelector(".registro-form");
    var status = document.getElementById("submit-status");
    var submitBtn = document.getElementById("registro-submit-btn");

    if (form && status && submitBtn) {
        form.addEventListener("submit", function () {
            status.textContent = "Solicitud recibida, nos pondremos en contacto contigo pronto.";
            status.classList.add("registro-form__status--visible");
            submitBtn.classList.add("registro-form__submit--loading");
            submitBtn.setAttribute("aria-busy", "true");
        });
    }
})();
