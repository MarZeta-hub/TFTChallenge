
function botonModalChangeSummon(){
   $('#myModal').modal("toggle")
}

function closeModal(){
    $('#myModal').modal('hide')
}


$(document).ready(function() {
    var messages = "{{ get_flashed_messages() }}";
    console.log(messages)
    if (typeof messages != 'undefined' && messages != '[]') {
        $('#myModalError').modal("toggle")
    };
});

