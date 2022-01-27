$(document).ready(function(require) {
    "use strict";
    var ajax = require("web.ajax");

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
        show_save_button($(this));
    });
    $("#teacher_schedule_table select").change(function(){
        show_save_button($(this));
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
    $(".mark_input").keypress(function (e) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
           var col = $(this).closest("td").index();
           var next_mark_input = $(this).closest('tr').next().find('td:eq('+col+')').find('input');
           next_mark_input.prop("readonly", false);
           next_mark_input.focus();
        }
    });

    function show_save_button(clicked_item){
        $('input').prop("readonly", true);
        clicked_item.prop("readonly", false);
        $('#editing_msg').show();
        $('#save_schedule_btn').show();
    }

    var update_json = $.Deferred();
    update_json.resolve();
    $(".drop_action_nline").click(function(){
        var schedule = $('#schedule_id').text();
        var n_line = $(this).attr('id');
        var classes = {};
        $($(this).attr('class').split(' ')).each(function() {
           if (this !== '') {
               classes[this] = this;
           }
        });
        $.ajax({
            type: "POST",
            url: "/schedule/action",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'schedule_id': schedule, 'vals': classes, 'n_line': n_line,}}),
            success: function(resp){
               console.log("Finished. " + resp); //just use the resp here
               location.reload();
            },
            error : function(err){
                console.log("Error: " + err); //just use the err here
            }
        });
    });

});
