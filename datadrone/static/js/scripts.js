function confirmDelete(name, url) {
    if (confirm("Are you sure you want to delete " + name + "?")) {
        window.location.href=url;
    }
}

function dismiss(element){
    element.parentNode.classList.add("hidden");
};

flashes = document.getElementsByClassName("flash");
for (let i=0; i<flashes.length; i++) {
    flashes[i].addEventListener("transitionend", () =>  { 
        flashes[i].style.display = "none"; 
    }) 
}

function toggleUserMenu() {
    document.getElementById("user-menu").classList.toggle("visible");
    document.getElementById("user-icon").classList.toggle("active");
}

function toggleMenu() {
    document.getElementById("user-menu").classList.remove("visible");
}

document.onmouseup = function(e) {
    e.preventDefault()
    if ((e.target.id != "user-icon")
            && (e.target.parentElement.id != "user-menu")) {
        document.getElementById("user-menu").classList.remove("visible");
        document.getElementById("user-icon").classList.remove("active");
    }
}