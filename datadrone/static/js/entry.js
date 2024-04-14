$(document).ready(function(){
    $(".tag-box-checkbox:checked + .tag-box-label").removeClass("hidden")

    $("#hide-location").click(function() {
        $("#latitude").val(null);
        $("#longitude").val(null);
    });
    $("#edit-tags").click(function() {
        $("#edit-tags").toggleClass("active")
        if ($("#edit-tags").hasClass("active")) {
            $(".tag-box-label").removeClass("disabled");
            $(".tag-box-label").removeClass("hidden")
        }
        else {
            $(".tag-box-label").addClass("disabled");
            $(".tag-box-checkbox:not(:checked) + .tag-box-label").addClass("hidden")
        }
    });
});
