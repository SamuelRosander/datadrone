$(document).ready(function(){
  $("#login-google-btn").click(function() {
    let url = "/auth/google";

    if ($("#remember").is(":checked")) {
      url += "?remember=true"
    }

    $("#login-google-btn").attr("href", url)
  });
});
