$(document).ready(function(){
  $(".filter-header").click(function() {
    // $(".filter-body").slideToggle("fast");
    $(this).toggleClass('is-active').next(".filter-body").stop().slideToggle(200);

  });

});
