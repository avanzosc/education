$(document).ready(function(require) {
    "use strict";

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
});
