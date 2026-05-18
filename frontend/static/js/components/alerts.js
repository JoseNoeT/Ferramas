/* Reusable behavior for flash messages rendered by Django templates. */
(function () {
	"use strict";

	const ALERT_SELECTOR = ".alert, .auth-card__alert, .dashboard-admin__message, .registro-alert";
	const AUTO_CLOSE_MS = 5500;

	function dismissAlert(element) {
		element.style.transition = "opacity 220ms ease, transform 220ms ease, max-height 220ms ease, margin 220ms ease";
		element.style.opacity = "0";
		element.style.transform = "translateY(-4px)";
		element.style.maxHeight = "0";
		element.style.marginTop = "0";
		element.style.marginBottom = "0";
		window.setTimeout(() => {
			element.remove();
		}, 230);
	}

	function createCloseButton(alertElement) {
		const button = document.createElement("button");
		button.type = "button";
		button.className = "alert-dismiss";
		button.setAttribute("aria-label", "Cerrar mensaje");
		button.textContent = "x";
		button.style.marginLeft = "0.75rem";
		button.style.border = "0";
		button.style.background = "transparent";
		button.style.color = "inherit";
		button.style.cursor = "pointer";
		button.style.fontWeight = "700";
		button.style.fontSize = "0.95rem";

		button.addEventListener("click", () => dismissAlert(alertElement));
		return button;
	}

	function enhanceAlert(alertElement) {
		if (alertElement.dataset.alertReady === "1") {
			return;
		}

		alertElement.dataset.alertReady = "1";
		alertElement.style.overflow = "hidden";
		alertElement.style.maxHeight = alertElement.scrollHeight + "px";

		if (!alertElement.querySelector(".alert-dismiss")) {
			const closeButton = createCloseButton(alertElement);
			alertElement.appendChild(closeButton);
		}

		window.setTimeout(() => {
			if (document.body.contains(alertElement)) {
				dismissAlert(alertElement);
			}
		}, AUTO_CLOSE_MS);
	}

	function initAlerts() {
		document.querySelectorAll(ALERT_SELECTOR).forEach(enhanceAlert);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initAlerts);
	} else {
		initAlerts();
	}
})();
