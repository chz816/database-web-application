$("#expense_form").submit(function(event) {
    event.preventDefault();
    console.log("In submit_expense_button");
    var date = $("#expense_date").val();
    var vendor = $("#expense_vendor").val();
    var amount = $("#expense_amount").val();
    var description = $("#expense_description").val();
    var data_params = {
        "date": date,
        "vendor": vendor,
        "amount": amount,
        "description": description,
        "dog_id": window.location.href.split('/').pop()
    };
    $('#expense_info').html("");
    $.ajax({
        url: "/go2Expense",
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