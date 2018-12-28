$(document).ready(function(){
  $("#add-item-btn").click(function() {
    $("#add-item-modal-fade").show();
    $("#add-item-modal-newitem").show();
    $("#add-item-input").focus();
  });

  $("#add-item-modal-fade").click(function() {
    $("#add-item-modal-fade").hide();
    $("#add-item-modal-newitem").hide();
  });

  $(".jq-tag-icon").click(function() {
    $("#tags-modal-fade").show();
    $("#modal-item-tags-" + $(this).attr("target")).show();
  });

  $(".jq-tag-button").click(function() {
    $("#tags-modal-fade").hide();
    $(".modal-item-tags-outer-container").hide();
  });

  $(".tag-box-checkbox").change(function() {
    var all_checkboxes = $("input:checkbox");
    var target = $(this).attr("target")
    for (var i = all_checkboxes.length-1; i >= 0; i--) {
      if (all_checkboxes[i].getAttribute("target") != target || all_checkboxes[i].className != "tag-box-checkbox") {
        all_checkboxes.splice(i, 1)
      }
    }
    if (checkedTags(all_checkboxes)) {
      $("#tagswitch-img-" + target).attr("src", "static/img/tag_active.png")
    } else {
      $("#tagswitch-img-" + target).attr("src", "static/img/tag_inactive.png")
    }
  });
});

function sendForm(item_id) {
  if(!$("#geo_switch-" + item_id).is(':checked')) {
    document.getElementById("add_entry_form-" + item_id).submit();
  } else {
    var ua = navigator.userAgent.toLowerCase(), isAndroid = ua.indexOf("android") > -1, geoTimeout = isAndroid ? '15000' : '1000';

    function success(position) {
      $("#latitude-" + item_id).val(position.coords.latitude);
      $("#longitude-" + item_id).val(position.coords.longitude);

      document.getElementById("add_entry_form-" + item_id).submit();
    }

    function error(err) {
      alert(err.message);
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(success, error, {enableHighAccuracy: true, maximumAge: 3000, timeout: geoTimeout});
    } else {
      alert('Location services must be enabled to use this');
    }
  }
}

/*
*   Returns true if one or more checkboxes are checked. False if none
*/
function checkedTags(checkboxes) {
  for (var i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i].checked) {
      return true;
    }
  }
  return false
}
