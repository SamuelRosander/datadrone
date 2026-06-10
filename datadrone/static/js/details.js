$(document).ready(function(){
  $(".filter-button").click(function() {
    $(".filter-body").slideToggle("fast");
    $(this).toggleClass('active');
  });

  $(".edit-itemname-toggle").click(function() {
    $(".heading-grid").toggleClass("hidden");
    $("#itemname").focus().select();
    $("#heading-menu").addClass("invisible");
  });
});

document.querySelectorAll('input[name="quickdays"]').forEach(radio => {
    radio.addEventListener('change', function() {
        window.location.href = this.dataset.url;
    });
});