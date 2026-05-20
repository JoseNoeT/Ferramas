(function () {
    // Auto-submit del filtro de ordenamiento
    var selectOrdenamiento = document.getElementById('ordenamiento');
    if (selectOrdenamiento) {
        selectOrdenamiento.addEventListener('change', function () {
            var form = document.getElementById('ofertas-filter-form');
            if (form) form.submit();
        });
    }

    var slider = document.getElementById('ofertas-slider');
    if (!slider) return;

    var slides = slider.querySelectorAll('.ofertas-slide');
    var dots = document.querySelectorAll('.slider-dot');
    var prevBtn = document.getElementById('slider-prev');
    var nextBtn = document.getElementById('slider-next');
    var currentIndex = 0;
    var autoplayInterval;

    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function showSlide(index) {
        slides.forEach(function (slide, i) {
            slide.classList.toggle('active', i === index);
        });
        dots.forEach(function (dot, i) {
            dot.classList.toggle('active', i === index);
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        showSlide(currentIndex);
    }

    function startAutoplay() {
        if (reducedMotion) return;
        autoplayInterval = setInterval(nextSlide, 5000);
    }

    function resetAutoplay() {
        clearInterval(autoplayInterval);
        startAutoplay();
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { prevSlide(); resetAutoplay(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { nextSlide(); resetAutoplay(); });

    dots.forEach(function (dot, i) {
        dot.addEventListener('click', function () {
            currentIndex = i;
            showSlide(i);
            resetAutoplay();
        });
    });

    // Soporte swipe táctil en mobile
    var touchStartX = 0;
    slider.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    slider.addEventListener('touchend', function (e) {
        var diff = touchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 40) {
            if (diff > 0) { nextSlide(); } else { prevSlide(); }
            resetAutoplay();
        }
    }, { passive: true });

    showSlide(currentIndex);
    startAutoplay();

    if (!reducedMotion) {
        slider.addEventListener('mouseenter', function () { clearInterval(autoplayInterval); });
        slider.addEventListener('mouseleave', startAutoplay);
    }
})();
