const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".main-nav");
if (toggle && nav) {
    toggle.addEventListener("click", function () {
        const open = nav.classList.toggle("open");
        toggle.setAttribute("aria-expanded", open);
    });
}

document.addEventListener("submit", function (event) {
    const form = event.target;
    if (form.matches("[data-confirm]") && !window.confirm(form.getAttribute("data-confirm"))) {
        event.preventDefault();
    }
});
