document.addEventListener("DOMContentLoaded", () => {
	const cta = document.querySelector(".hero__cta");
	const catalog = document.querySelector("#catalogo");

	if (!cta || !catalog) {
		return;
	}

	cta.addEventListener("click", (event) => {
		event.preventDefault();
		catalog.scrollIntoView({ behavior: "smooth", block: "start" });
	});
});
