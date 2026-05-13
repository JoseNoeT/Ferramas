(function () {
	const authForm = document.querySelector(".auth-form");
	if (!authForm) {
		return;
	}

	const passwordInputs = authForm.querySelectorAll('input[type="password"]');
	passwordInputs.forEach((input) => {
		const wrapper = document.createElement("div");
		wrapper.className = "auth-form__password-group";
		input.parentNode.insertBefore(wrapper, input);
		wrapper.appendChild(input);

		const toggleButton = document.createElement("button");
		toggleButton.type = "button";
		toggleButton.className = "auth-form__toggle-password";
		toggleButton.textContent = "👁";
		toggleButton.setAttribute("aria-label", "Mostrar contrasena");

		toggleButton.addEventListener("click", () => {
			const isHidden = input.type === "password";
			input.type = isHidden ? "text" : "password";
			toggleButton.textContent = isHidden ? "🙈" : "👁";
			toggleButton.setAttribute("aria-label", isHidden ? "Ocultar contrasena" : "Mostrar contrasena");
		});

		wrapper.appendChild(toggleButton);
	});
})();
