$(document).ready(function() {

var fullSelects = {
    'exkursion1' : ['#exkursion1', $('#exkursion1').clone()],
    'exkursion2' : ['#exkursion2', $('#exkursion2').clone()],
    'exkursion3' : ['#exkursion3', $('#exkursion3').clone()],
    'exkursion4' : ['#exkursion4', $('#exkursion4').clone()]
};

var resetSelects = function() {
    $.each(fullSelects, function(index, value) {
        var selectObj = $(value[0]);
        var oldVal = selectObj.val();
        selectObj.html(value[1].html());
        selectObj.val(oldVal);
    });
};

var removeEntry = function() {
    $.each(fullSelects, function(index, value) {
        var val = $(value[0]).val();
        if(val != 'egal') {
            $.each(fullSelects, function(innerIndex, innerValue) {
                if(innerIndex != index) {
                    $(innerValue[0]).find('option[value="' + val + '"]').remove();
                }
            });
        }
    });
};

var handleBirthday = function() {
    var needBirthday = false;
    $.each(fullSelects, function(index, value) {
        var val = $(value[0]).val();
        if(val == 'stad') {
            needBirthday = true;
        }
    });

    if(needBirthday) {
        $('#formgroup-birthday').show();
        $('#geburtsdatum').prop('required',true);
    } else {
        $('#formgroup-birthday').hide();
        $('#geburtsdatum').prop('required',false);
    }
};

var selectChangeFunc = function() {
    resetSelects();
    removeEntry();
    handleBirthday();
}

$('#exkursion1').change(selectChangeFunc);
$('#exkursion2').change(selectChangeFunc);
$('#exkursion3').change(selectChangeFunc);
$('#exkursion4').change(selectChangeFunc);

handleBirthday();
});
