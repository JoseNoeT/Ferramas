document.addEventListener("DOMContentLoaded", () => {
	const cta = document.querySelector(".hero__cta");
	const catalog = document.querySelector("#catalogo");

	if (cta && catalog) {
		cta.addEventListener("click", (event) => {
			event.preventDefault();
			catalog.scrollIntoView({ behavior: "smooth", block: "start" });
		});
	}

	const slider = document.querySelector("[data-season-slider]");
	if (!slider) {
		return;
	}

	const track = slider.querySelector("[data-season-track]");
	const prev = slider.querySelector("[data-season-prev]");
	const next = slider.querySelector("[data-season-next]");
	const dotsContainer = document.querySelector("[data-season-dots]");

	if (!track || !prev || !next || !dotsContainer) {
		return;
	}

	const items = Array.from(track.querySelectorAll(".hero-offers__item"));
	if (!items.length) {
		return;
	}

	let index = 0;
	let timer = null;

	const totalPages = () => items.length;

	const renderDots = () => {
		dotsContainer.innerHTML = "";
		for (let i = 0; i < totalPages(); i += 1) {
			const dot = document.createElement("button");
			dot.type = "button";
			dot.className = "hero-offers__dot";
			dot.dataset.seasonDot = "true";
			dot.setAttribute("aria-label", `Ir a oferta ${i + 1}`);
			dot.addEventListener("click", () => {
				index = i;
				update();
				restartAutoplay();
			});
			dotsContainer.appendChild(dot);
		}
	};

	const update = () => {
		if (index >= totalPages()) {
			index = 0;
		}
		if (index < 0) {
			index = totalPages() - 1;
		}
		track.style.transform = `translateX(-${index * 100}%)`;

		const dots = dotsContainer.querySelectorAll("[data-season-dot]");
		dots.forEach((dot, i) => {
			dot.classList.toggle("is-active", i === index);
		});
	};

	const nextSlide = () => {
		index = index + 1 >= totalPages() ? 0 : index + 1;
		update();
	};

	const prevSlide = () => {
		index = index - 1 < 0 ? totalPages() - 1 : index - 1;
		update();
	};

	const startAutoplay = () => {
		timer = window.setInterval(nextSlide, 3500);
	};

	const stopAutoplay = () => {
		if (timer) {
			window.clearInterval(timer);
			timer = null;
		}
	};

	const restartAutoplay = () => {
		stopAutoplay();
		startAutoplay();
	};

	next.addEventListener("click", () => {
		nextSlide();
		restartAutoplay();
	});

	prev.addEventListener("click", () => {
		prevSlide();
		restartAutoplay();
	});

	slider.addEventListener("mouseenter", stopAutoplay);
	slider.addEventListener("mouseleave", startAutoplay);

	window.addEventListener("resize", () => {
		update();
	});

	renderDots();
	update();
	startAutoplay();
});
