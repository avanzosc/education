$(document).ready(function() {
    "use strict";

    function generate_new_values(changed_vals, changed_input){
        var new_val = {
            record_id: changed_input.attr('id'),
            new_val: changed_input.val()
        }
        if(changed_vals == ''){
            var changed_vals_obj = [new_val];
        }
        else{
            var changed_vals_obj = JSON.parse(changed_vals);
            changed_vals_obj.push(new_val);
        }
        return changed_vals_obj;
    }

    $("#teacher_schedule_table input").change(function(){
        $(this).css("background-color", "lightsteelblue");
        var changed_vals = $('#changed_input_ids').val();
        var changed_vals_obj = generate_new_values(changed_vals, $(this));
        $('#changed_input_ids').val(JSON.stringify(changed_vals_obj));
    });
    $("#teacher_schedule_table input").click(function(){
        $('input').prop("readonly", true);
        $(this).prop("readonly", false);
        $('#editing_msg').show();
        $('#save_schedule_btn').show();
    });
    $("#teacher_schedule_table .exceptionality_select").change(function(){
        $(this).removeClass("select_disabled");
        $('#editing_msg').show();
        $('#save_schedule_btn').show();
        var changed_vals = $('#changed_select_ids').val();
        var changed_vals_obj = generate_new_values(changed_vals, $(this));
        $('#changed_select_ids').val(JSON.stringify(changed_vals_obj));
    });
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
