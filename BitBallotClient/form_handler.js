$(document).ready(function() {
    $('.btn-primary').click(function() {
        $.ajax({
            type: "POST",
            url: $('form').attr('action'),
            data: $('form').serialize(),
            success: function(d){
                window.location.href = "after_submit.html?status="+d;
            },
            error: function(d){
                console.log(d);
            },
        });
    });
});