$(document).ready(function(){
  $(".filter-button").click(function() {
    $(".filter-body").slideToggle("fast");
    $(this).toggleClass('active')
  });
});
