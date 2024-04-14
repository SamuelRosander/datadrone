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
        $(".modal-item-tags-container").hide();
    });

    $(".tag-box-checkbox").change(function() {
        var all_checkboxes = $("input:checkbox");
        var target = $(this).attr("target")
        for (var i = all_checkboxes.length-1; i >= 0; i--) {
            if (all_checkboxes[i].getAttribute("target") != target || 
                    all_checkboxes[i].className != "tag-box-checkbox") {
                all_checkboxes.splice(i, 1)
            }
        }
        if (checkedTags(all_checkboxes)) {
            $("#tagswitch-img-" + target).addClass("active")
        }
        else {
            $("#tagswitch-img-" + target).removeClass("active")
        }
    });
});

function sendForm(item_id) {
    $("#timestamp-" + item_id).val(getFormattedDate());

    let clickedButton = $("#add-" + item_id).children("i").eq(0)
    clickedButton.removeClass("bx-plus").addClass("bx-loader-alt")

    if(!$("#geo_switch-" + item_id).is(':checked')) {
        $("#add_entry_form-" + item_id).submit();
    }
    else {
        function success(position) {
            $("#latitude-" + item_id).val(position.coords.latitude);
            $("#longitude-" + item_id).val(position.coords.longitude);

            $("#add_entry_form-" + item_id).submit();
        }

        function error(err) {
            alert(err.message);
            clickedButton.removeClass("bx-loader-alt").addClass("bx-plus")
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                success, error, {
                    enableHighAccuracy: true, maximumAge: 0, timeout: 15000});
        }
        else {
            alert('Location services must be enabled to use this');
            clickedButton.removeClass("bx-loader-alt").addClass("bx-plus")
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

function getFormattedDate() {
var date = new Date();

    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();

    month = (month < 10 ? "0" : "") + month;
    day = (day < 10 ? "0" : "") + day;
    hour = (hour < 10 ? "0" : "") + hour;
    min = (min < 10 ? "0" : "") + min;
    sec = (sec < 10 ? "0" : "") + sec;

    var str = date.getFullYear() + "-" + month + "-" + day + " " +  hour + ":" + min + ":" + sec;

    return str;
}