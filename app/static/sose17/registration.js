$(document).ready(function() {

/*
 * The HTML5 date field is so far only supported by Chrome and Opera.
 * Use WebShims to support it.
 */
webshim.setOptions('basePath', 'sose17/webshim-1.16.0/js-webshim/minified/shims/');
webshim.setOptions('forms-ext', {types: 'date'});
webshim.polyfill('forms forms-ext');

var fullSelects = [
    ['#exkursion1', $('#exkursion1').clone(), '#formgroup-exkursion1'],
    ['#exkursion2', $('#exkursion2').clone(), '#formgroup-exkursion2'],
    ['#exkursion3', $('#exkursion3').clone(), '#formgroup-exkursion3'],
    ['#exkursion4', $('#exkursion4').clone(), '#formgroup-exkursion4']
];

var resetSelects = function() {
    $.each(fullSelects, function(index, value) {
        var selectObj = $(value[0]);
        var oldVal = selectObj.val();
        selectObj.html(value[1].html());
        selectObj.val(oldVal);
        $(value[2]).show()
    });
};

var removeEntry = function() {
    $.each(fullSelects, function(index, value) {
        var val = $(value[0]).val();
        if(val != 'egal' && val != 'keine') {
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

var handleKeine = function() {
    var indexKeine = -1;
    $.each(fullSelects, function(index, value) {
        var val = $(value[0]).val();
        if(val == 'keine' && indexKeine == -1) {
            indexKeine = index;
        }
    });

    if(indexKeine != -1) {
        for(i = indexKeine + 1; i < fullSelects.length; i++) {
            var editSelect = $(fullSelects[i][0]);
            var editFormGroup = $(fullSelects[i][2])
            editSelect.val('keine')
            editFormGroup.hide()
        }
    }
}

var selectChangeFunc = function() {
    resetSelects();
    removeEntry();
    handleBirthday();
    handleKeine();
}

$('#exkursion1').change(selectChangeFunc);
$('#exkursion2').change(selectChangeFunc);
$('#exkursion3').change(selectChangeFunc);
$('#exkursion4').change(selectChangeFunc);

handleBirthday();
handleKeine();
});
