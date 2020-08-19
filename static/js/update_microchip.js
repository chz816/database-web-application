$("#update_microchip_form").submit(function (event) {
    event.preventDefault();
    console.log("In updating the microchip ID");
    var updated_microchip = $("#new_microchip").val();
    var data_params = {
        "updated_microchip": updated_microchip,
        "dog_id": window.location.href.split('/').pop()
    };
    $('#update_microchip_form').html("");
    $.ajax({
        url: "go2UpdateMicrochip",
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
