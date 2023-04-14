$(document).ready(function(require) {
    "use strict";

    var selected_eval = $('input[name=selected_eval]').attr('value');
    if(selected_eval){
        show_eval_info(selected_eval);
    }
    inputs_to_disable();

    function inputs_to_disable(){
        var disable_inputs = $('input.meeting_real_input.disabled');
        disable_inputs.attr('disabled', true);
    }

    function update_new_values(changed_vals, changed_input){
        var new_val = {
            record_id: changed_input.attr('name'),
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

    $(".meeting_real_input").change(function(){
        var changed_vals = $('#changed_input_ids').val();
        var changed_vals_obj = update_new_values(changed_vals, $(this));
        $('#changed_input_ids').val(JSON.stringify(changed_vals_obj));
    });

    $(".eval_button_tutor").click(function(){
        var evaluation = this.id;
        $('input[name=selected_eval]').attr('value', evaluation);
        $('.eval_button_tutor').removeClass('btn-highlight');
        $(this).addClass('btn-highlight');
        show_eval_info(evaluation);
    });

    function show_eval_info(evaluation){
        $('td').hide();
        $('th').hide();
        if(evaluation == 'all'){
            $('td').show();
            $('th').show();
        }
        else{
            $('.blank').show();
            $('.td_student_name').show();
            $('.td_' + evaluation).show();
        }
    }

    $(".meeting_real_input").keypress(function (e) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
           var col = $(this).closest("td").index();
           var next_mark_input = $(this).closest('tr').next().find('td:eq('+col+')').find('input');
           next_mark_input.prop("readonly", false);
           next_mark_input.focus();
        }
    });
});
