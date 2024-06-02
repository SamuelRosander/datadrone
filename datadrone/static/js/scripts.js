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

function toggleMenu() {
    document.getElementById("user-menu").classList.toggle("visible");
}

function toggleHeadingMenu() {
    document.getElementById("heading-menu").classList.toggle("visible");
}

document.onmouseup = function(e) {
    e.preventDefault()
    if ((e.target.id != "user-icon")
            && (e.target.parentElement.id != "user-menu")) {
        document.getElementById("user-menu").classList.remove("visible");
    }
    
    if ((e.target.id != "heading-menu-icon")
            && (e.target.parentElement.id != "heading-menu")) {
        document.getElementById("heading-menu").classList.remove("visible");
    }
}