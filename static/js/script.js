function decryptPassword(id){
    $(document).ready(function() {
        $.ajax({
            data : {
                sno: $('#'+id).text()
                },
            type : 'POST',
            url : '/decrypt_details'
            })
        .done(function(data) {
            if(data.output){
                $('#decrypted-pass').removeAttr('hidden');
                $('#decrypted-pass input').val(data.output);
            }
        });
    });
}

function copyPassword() {
    $("#copy-pass").select();
    document.execCommand("copy");
    // alert("Password copied to clipboard");
}