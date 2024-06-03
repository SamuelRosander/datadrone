$(document).ready(function(){
  $(".filter-button").click(function() {
    $(".filter-body").slideToggle("fast");
    $(this).toggleClass('active')
  });

  $(".edit-itemname-toggle").click(function() {
    $(".heading-grid").toggleClass("hidden");
    $("#itemname").focus().select()
  });
});
