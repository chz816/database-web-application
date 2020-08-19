$("#add_form").submit(function (event) {
    event.preventDefault();
    console.log("In login_button");
    var email = $("#login_email").val();
    var firstname = $("#login_firstname").val();
    var lastname = $("#login_lastname").val();
    var co_applicant_first_name = $("#login_co_applicant_first_name").val();
    var co_applicant_last_name = $("#login_co_applicant_last_name").val();
    var state = $("#login_state").val();
    var city = $("#login_city").val();
    var street = $("#login_street").val();
    var cellphone = $("#login_cellphone").val();
    var zipcode = $("#login_zipcode").val();
    var date = $("#login_date").val();

    var data_params = {
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "co_applicant_first_name": co_applicant_first_name,
        "co_applicant_last_name": co_applicant_last_name,
        "state": state,
        "city": city,
        "street": street,
        "cellphone": cellphone,
        "zipcode": zipcode,
        "date": date,
    };
    $('#add_info').html("");
    $.ajax({
        url: "go2Addadoptionapplication",
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
                $("#add_info").append("<b>ERROR: </b> <text>" + response.error + "</text>");
                $("#login_email").val('');
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
