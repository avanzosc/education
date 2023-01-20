$(document).ready(function(require) {
    "use strict";

    $(".input_survey").change(function(){
        if ($(this).checked){
            $(this).parent('td.td_survey').css("background-color", "light-grey !important");
        }
        else{
            $(this).parent('td.td_survey').css("background-color", "white !important");
        }
    });

});