$(document).ready(function(require) {
    "use strict";

    let ajax = require("web.ajax");

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

    $(".duplicate_meeting").one("click", function(){
        var value = this.id;
        $('#input_duplicate').attr('value', value);
        $('form#real_done').submit();
    });

//    $("button.duplicate_meeting").click(function(){
//        var value = this.id;
//        $('#download_xls').attr('value', value);
//        $('form#real_done').submit();
//    });

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
           var all_rows = $("tr");
           var last_row = all_rows.last();
           var last_row_index = last_row[0].rowIndex;
           var col = $(this).closest("td").index();
           var next_tr = $(this).closest('tr').next();
           var current_row = $(this).closest('tr')[0].rowIndex;
           var inputs_len = 0;
           if (next_tr.length == 0 && $(this).closest('tr')[0].rowIndex === last_row_index){
                inputs_len = 1;
           }
           var next_mark_input = next_tr.find('td:eq('+col+')').find('input');
           var row = current_row+1;
           inputs_len = next_mark_input.length;
           while(inputs_len === 0){
               next_tr = next_tr.next();
               next_mark_input = next_tr.find('td:eq('+col+')').find('input');
               if(next_tr.length > 0 || row === next_tr[0].rowIndex){
                   if (next_mark_input.length === 1){
                        inputs_len = 1;
                   }
               }
               row++;
           }
           if(next_mark_input.length != 0){
               next_mark_input.prop("readonly", false);
               next_mark_input.focus();
           }
        }
    });
});
