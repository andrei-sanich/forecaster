$(document).ready(function() {
    $("form[id^='add_forecast_']").each(function() {
        $(this).validate({
            rules: {
                home_team: {
                    required: true,
                    digits: true,
                },
                guest_team: {
                    required: true,
                    digits: true,
                },
            },
            messages: {
                home_team: {
                    required: "Обязательно к заполнению",
                    digits: "Вводите только цифры"
                },
                guest_team: {
                    required: "Обязательно к заполнению",
                    digits: "Вводите только цифры" 
                }
            }
        });
    });
});
