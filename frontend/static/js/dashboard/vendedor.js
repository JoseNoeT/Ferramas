/* ═══════════════════════════════════════════════════════════
   Dashboard Vendedor — JS
   14 Leyes UX/UI:
   [3-Hick]    Confirmación en acciones destructivas reduce errores
   [5-Postel]  Búsqueda flexible, acepta cualquier texto
   [13-Tesler] Complejidad mínima en confirmaciones (Sí/No)
   [14-Doherty] Feedback instantáneo (<400ms) en búsqueda y tabs
   ═══════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

    /* ─ Tabs [14-Doherty] cambio instantáneo ─────────── */
    const tabs = document.querySelectorAll(".dv-tabs__btn");
    const panels = document.querySelectorAll(".dv-panel");

    tabs.forEach((btn) => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;

            tabs.forEach((t) => {
                t.classList.remove("dv-tabs__btn--active");
                t.setAttribute("aria-selected", "false");
            });
            btn.classList.add("dv-tabs__btn--active");
            btn.setAttribute("aria-selected", "true");

            panels.forEach((p) => p.classList.remove("dv-panel--active"));
            const panel = document.getElementById("tab-" + target);
            if (panel) panel.classList.add("dv-panel--active");
        });
    });

    /* ─ Navegación por teclado en tabs ──────────────── */
    const tabList = document.querySelector(".dv-tabs");
    if (tabList) {
        tabList.addEventListener("keydown", (e) => {
            const btns = Array.from(tabs);
            const idx = btns.indexOf(document.activeElement);
            if (idx === -1) return;

            let next = -1;
            if (e.key === "ArrowRight") next = (idx + 1) % btns.length;
            if (e.key === "ArrowLeft")  next = (idx - 1 + btns.length) % btns.length;

            if (next !== -1) {
                e.preventDefault();
                btns[next].focus();
                btns[next].click();
            }
        });
    }

    /* ─ Buscador de productos [14-Doherty][5-Postel] ── */
    const input = document.getElementById("buscar-producto");
    const tabla = document.getElementById("tabla-productos");
    const resultados = document.getElementById("resultados-busqueda");

    if (input && tabla) {
        input.addEventListener("input", () => {
            const filtro = input.value.toLowerCase().trim();
            const filas = tabla.querySelectorAll("tbody tr");
            let visibles = 0;

            filas.forEach((fila) => {
                const texto = fila.textContent.toLowerCase();
                const visible = filtro === "" || texto.includes(filtro);
                fila.style.display = visible ? "" : "none";
                if (visible) visibles++;
            });

            if (resultados) {
                resultados.textContent = filtro
                    ? visibles + " producto" + (visibles !== 1 ? "s" : "") + " encontrado" + (visibles !== 1 ? "s" : "")
                    : "";
            }
        });
    }

    /* ─ Confirmación en acciones destructivas ──────── */
    /* [3-Hick] Reduce error al confirmar antes de actuar
       [13-Tesler] Solo Sí/No, complejidad mínima */
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();

            const titulo = form.dataset.confirm;
            const texto = form.dataset.confirmText || "¿Estás seguro?";

            const overlay = document.createElement("div");
            overlay.className = "dv-confirm-overlay";
            overlay.innerHTML =
                '<div class="dv-confirm-dialog">' +
                    '<h3>' + titulo + '</h3>' +
                    '<p>' + texto + '</p>' +
                    '<div class="dv-confirm-dialog__actions">' +
                        '<button type="button" class="btn btn--ghost btn--sm" data-action="cancel">Cancelar</button>' +
                        '<button type="button" class="btn btn--danger btn--sm" data-action="confirm">Confirmar</button>' +
                    '</div>' +
                '</div>';

            document.body.appendChild(overlay);

            overlay.querySelector('[data-action="cancel"]').addEventListener("click", () => {
                overlay.remove();
            });

            overlay.querySelector('[data-action="confirm"]').addEventListener("click", () => {
                overlay.remove();
                form.removeAttribute("data-confirm");
                form.submit();
            });

            overlay.addEventListener("click", (ev) => {
                if (ev.target === overlay) overlay.remove();
            });
        });
    });

    /* ─ Loading state en botones de submit ─────────── */
    /* [14-Doherty] Feedback visual inmediato al hacer clic */
    document.querySelectorAll(".dv-actions form").forEach((form) => {
        if (form.dataset.confirm) return;
        form.addEventListener("submit", () => {
            const btn = form.querySelector("button[type=submit]");
            if (btn) {
                btn.disabled = true;
                btn.classList.add("btn--loading");
            }
        });
    });
});
