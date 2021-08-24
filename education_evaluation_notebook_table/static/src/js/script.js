$(document).ready(function() {
    "use strict";

    $(".eval_button").click(function(){
        var evaluation = this.id;
        $('.eval_button').removeClass('btn-highlight');
        $(this).addClass('btn-highlight');
        $('td').hide();
        if(evaluation == 'all'){
            $('td').show();
        }
        else{
            $('.student_schedule_td').show();
            $('.td_eval_' + evaluation).show();
            if(evaluation == 'final'){
                $('.final_td').show();
            }
        }
    });

});
