$("#submit_form").submit(function (event) {
    event.preventDefault();
    console.log("In login_button");
    var userID = $("#login_userID").val();
    var uname = $("#login_uname").val();
    var uage = $("#login_uage").val();
    var usex = $("#usex").val();
    var udesc = $("#login_udescription").val();
    var umicochipID = $("#login_umicochipID").val();
    var usurrenderDate = $("#login_usurrenderDate").val();
    var usurrenderReason = $("#login_usurrenderReason").val();
    var usurrenderbyanimalcontrol = $("#surrenderbyAnimalControl").val();
    var breed = $("#breed").val();
    var alteration = $("#alteration").val();

    var data_params = {
        "userID": userID,
        "name": uname,
        "alterationstatus": alteration,
        "age": uage,
        "sex": usex,
        "desc": udesc,
        "micochipID": umicochipID,
        "surrenderDate": usurrenderDate,
        "surrenderReason": usurrenderReason,
        "surrenderbyanimalcontrol": usurrenderbyanimalcontrol,
        "breed": breed,
    };
    $('#logg_info').html("");
    $.ajax({
        url: "go2Adddog",
        type: "POST",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify(data_params),
        dataType: 'json',
        success: function (response) {
            console.log(response); // data can be loaded correctly !!!!
            if (response.redirect) {
                window.location.href = response.redirect;
            }
            if (response.error) {
                $("#logg_info").append("<b>ERROR: </b> <text>" + response.error + "</text>");
                $("#login_uname").val('');
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
