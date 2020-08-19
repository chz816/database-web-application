$("#update_alteration_form").submit(function (event) {
    event.preventDefault();
    console.log("In updating the alteration status");
    var updated_alteration = $("#new_alteration").val();
    var data_params = {
        "updated_alteration": updated_alteration,
        "dog_id": window.location.href.split('/').pop()
    };
    $('#update_alteration_form').html("");
    $.ajax({
        url: "go2UpdateAlteration",
        type: "POST",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify(data_params),
        dataType: 'json',
        success: function (response) {
            console.log(response); // data can be loaded correctly !!!!
            if (response.redirect) {
                window.location.href = response.redirect + "?dog_id=" + response.dog_id;
            }
            if (response.error) {
                $("#log_info").append("<b>ERROR: </b> <text>" + response.error + "</text>");
                $("#login_uname").val('');
                $("#login_psw").val('');
            }
        },
        complete: function (xhr, textStatus) {
            console.log("AJAX Request complete -> ", xhr, " -> ", textStatus);
        },
        error: function (error) {
            console.log(error);
        }
    });
});
