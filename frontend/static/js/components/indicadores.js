(function () {
    var containers = document.querySelectorAll("[data-indicadores-component][data-endpoint]");
    if (!containers.length) {
        return;
    }

    function formatCurrency(value) {
        if (typeof value !== "number") {
            return "N/D";
        }
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: "CLP",
            maximumFractionDigits: 2,
        }).format(value);
    }

    function formatDate(value) {
        if (!value) {
            return "N/D";
        }
        var date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return String(value);
        }
        return new Intl.DateTimeFormat("es-CL", {
            dateStyle: "medium",
            timeStyle: "short",
        }).format(date);
    }

    function setLoadingState(container, isLoading) {
        var loadingEl = container.querySelector("[data-indicadores-loading]");
        var errorEl = container.querySelector("[data-indicadores-error]");
        var bodyEl = container.querySelector("[data-indicadores-body]");
        var buttonEl = container.querySelector("[data-actualizar-indicadores]");

        if (loadingEl) {
            loadingEl.style.display = isLoading ? "block" : "none";
        }
        if (errorEl && isLoading) {
            errorEl.style.display = "none";
        }
        if (bodyEl && isLoading) {
            bodyEl.style.display = "none";
        }
        if (buttonEl) {
            buttonEl.disabled = isLoading;
        }
    }

    function renderError(container) {
        var errorEl = container.querySelector("[data-indicadores-error]");
        var bodyEl = container.querySelector("[data-indicadores-body]");
        if (errorEl) {
            errorEl.textContent = "No pudimos obtener los indicadores ahora. Intenta actualizar en unos segundos.";
            errorEl.style.display = "block";
        }
        if (bodyEl) {
            bodyEl.style.display = "none";
        }
    }

    function renderData(container, data) {
        var bodyEl = container.querySelector("[data-indicadores-body]");
        var errorEl = container.querySelector("[data-indicadores-error]");
        if (errorEl) {
            errorEl.style.display = "none";
        }

        var ufEl = container.querySelector("[data-valor-uf]");
        var dolarEl = container.querySelector("[data-valor-dolar]");
        var euroEl = container.querySelector("[data-valor-euro]");
        var utmEl = container.querySelector("[data-valor-utm]");
        var fuenteEl = container.querySelector("[data-fuente]");
        var fechaEl = container.querySelector("[data-fecha-consulta]");

        if (ufEl) ufEl.textContent = formatCurrency(data.uf);
        if (dolarEl) dolarEl.textContent = formatCurrency(data.dolar);
        if (euroEl) euroEl.textContent = formatCurrency(data.euro);
        if (utmEl) utmEl.textContent = formatCurrency(data.utm);
        if (fuenteEl) fuenteEl.textContent = data.fuente || "mindicador.cl";
        if (fechaEl) fechaEl.textContent = formatDate(data.fecha_consulta);

        if (bodyEl) {
            bodyEl.style.display = "block";
        }
    }

    function fetchIndicadores(container) {
        var endpoint = container.getAttribute("data-endpoint");
        if (!endpoint) {
            return;
        }

        setLoadingState(container, true);

        fetch(endpoint, {
            method: "GET",
            headers: {
                Accept: "application/json",
            },
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                renderData(container, data || {});
            })
            .catch(function () {
                renderError(container);
            })
            .finally(function () {
                setLoadingState(container, false);
            });
    }

    containers.forEach(function (container) {
        var button = container.querySelector("[data-actualizar-indicadores]");
        if (button) {
            button.addEventListener("click", function () {
                fetchIndicadores(container);
            });
        }
        fetchIndicadores(container);
    });
})();
