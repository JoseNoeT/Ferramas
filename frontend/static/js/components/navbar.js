(function () {
    function closeDropdown(dropdown) {
        var toggle = dropdown.querySelector("[data-navbar-dropdown-toggle]");
        var menu = dropdown.querySelector("[data-navbar-dropdown-menu]");
        if (!toggle || !menu) {
            return;
        }

        dropdown.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        menu.hidden = true;
    }

    function openDropdown(dropdown) {
        var toggle = dropdown.querySelector("[data-navbar-dropdown-toggle]");
        var menu = dropdown.querySelector("[data-navbar-dropdown-menu]");
        if (!toggle || !menu) {
            return;
        }

        dropdown.classList.add("is-open");
        toggle.setAttribute("aria-expanded", "true");
        menu.hidden = false;
    }

    function closeAll(dropdowns) {
        dropdowns.forEach(function (dropdown) {
            closeDropdown(dropdown);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        var dropdowns = Array.prototype.slice.call(
            document.querySelectorAll("[data-navbar-dropdown]")
        );

        if (!dropdowns.length) {
            return;
        }

        dropdowns.forEach(function (dropdown) {
            var toggle = dropdown.querySelector("[data-navbar-dropdown-toggle]");
            var menu = dropdown.querySelector("[data-navbar-dropdown-menu]");

            if (!toggle || !menu) {
                return;
            }

            menu.hidden = true;
            toggle.setAttribute("aria-expanded", "false");

            toggle.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();

                var isOpen = dropdown.classList.contains("is-open");
                closeAll(dropdowns);
                if (!isOpen) {
                    openDropdown(dropdown);
                }
            });

            toggle.addEventListener("keydown", function (event) {
                if (event.key !== "Enter" && event.key !== " ") {
                    return;
                }

                event.preventDefault();
                toggle.click();
            });

            menu.addEventListener("click", function (event) {
                event.stopPropagation();
            });
        });

        document.addEventListener("click", function (event) {
            dropdowns.forEach(function (dropdown) {
                if (!dropdown.contains(event.target)) {
                    closeDropdown(dropdown);
                }
            });
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeAll(dropdowns);
            }
        });
    });
})();
