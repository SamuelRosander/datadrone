function confirmDelete(name, url) {
    if (confirm("Are you sure you want to delete " + name + "?")) {
        window.location.href=url;
    }
}

function dismiss(element){
    element.parentNode.classList.add("invisible");
};

flashes = document.getElementsByClassName("flash");
for (let i=0; i<flashes.length; i++) {
    flashes[i].addEventListener("transitionend", () =>  { 
        flashes[i].style.display = "none"; 
    }) 
}

function toggleMenu() {
    document.getElementById("user-menu").classList.toggle("invisible");
}

function toggleHeadingMenu() {
    document.getElementById("heading-menu").classList.toggle("invisible");
}

document.onclick = function(e) {
    if ((e.target.id != "user-icon")
            && (e.target.parentElement.id != "user-menu")) {
        document.getElementById("user-menu").classList.add("invisible");
    }
    
    if ((e.target.id != "heading-menu-btn")
            && (e.target.parentElement.id != "heading-menu-btn")
            && (e.target.parentElement.id != "heading-menu")) {
        document.getElementById("heading-menu").classList.add("invisible");
    }
}