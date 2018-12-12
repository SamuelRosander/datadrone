$(document).ready(function(){
  $("#link-show-tags").click(function() {
    $("#link-show-tags").hide();
    $("#link-hide-tags").show();
    $(".tag-box-label").css("display" , "inline-block");
    $(".tag-box-label").removeClass("tag-box-label-disable").addClass("tag-box-label-enable");
  });

  $("#link-hide-tags").click(function() {
    $("#link-show-tags").show();
    $("#link-hide-tags").hide();
    $(".tag-box-label").removeClass("tag-box-label-enable").addClass("tag-box-label-disable");
    $(".tag-box-checkbox:not(:checked) + .tag-box-label").hide();
  });

});
