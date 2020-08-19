$("#login_form").submit(function(event) {
    event.preventDefault();
    console.log("In login_button" );
    var uname = $("#login_uname").val();
    var psw = $("#login_psw").val();
    var data_params = {
        "usrname": uname,
        "password": psw,
    };
    $('#log_info').html("");
    $.ajax({
        url: "go2Dashboard",
        type: "POST",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify(data_params),
        dataType: 'json',
        success: function(response) {
            console.log(response); // data can be loaded correctly !!!!
            if (response.redirect) {
                window.location.href = response.redirect;
            }
            if (response.error) {
                $("#log_info").append("<b>ERROR: </b> <text>" + response.error + "</text>");
                $("#login_uname").val('');
                $("#login_psw").val('');
            }
        },
        complete: function(xhr, textStatus) {
            console.log("AJAX Request complete -> ", xhr, " -> ", textStatus);
        },
        error: function(error){
            console.log(error);
        }
    });
});