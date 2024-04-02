var editor;
var current_json_id = '';
var current_label_id = '';
var current_version_id = '';

function loadJsonEditor() {
    var container = document.getElementById("jsoneditor");
    editor = new JSONEditor(container, {mode: 'text', modes: ['text', 'code']});

    window.addEventListener('DOMContentLoaded', (event) => {
        editFormData('id_testparameters_set-0-parameters', 'id_testparameters_set-0-param_name', 'id_testparameters_set-0-version');   
        
        // hide default Django delete checkboxes
        var elementsContainingDelete = $("input[type='checkbox'][id*='-DELETE']");
        elementsContainingDelete.each(function(){
            $(this).addClass('hidden-field');
        });
    }); 
}

function editFormData(form_json_id, form_label_id, form_version_id) {
    if (current_json_id != '') {
        document.getElementById(current_json_id).textContent = getJsonData();
        document.getElementById(current_label_id).value = document.getElementById('id_editor_label').value;
        document.getElementById(current_version_id).value = document.getElementById('id_editor_version').value;


        //document.getElementById(current_label_id + '_table').innerText = document.getElementById(current_label_id).value;
    }
    current_json_id = form_json_id;
    current_label_id = form_label_id;
    current_version_id = form_version_id;
    editor.set(JSON.parse(document.getElementById(current_json_id).textContent));
    document.getElementById('id_editor_label').value = document.getElementById(current_label_id).value;
    document.getElementById('id_editor_version').value = document.getElementById(current_version_id).value;
}

function beforeSubmit() {
    try {
        document.getElementById(current_json_id).textContent = getJsonData();
        document.getElementById(current_label_id).value = document.getElementById('id_editor_label').value; 
        document.getElementById(current_version_id).value = document.getElementById('id_editor_version').value; 
        document.getElementById('id_repo_detail_form').submit();
    } catch (err) {
        //alert(err);
    }
}

function getJsonData() {
    return JSON.stringify(editor.get());
}

function deleteFormData(form_id, param_name) {
    var modal = $('#modal_delete_dialog');
    var yes = document.getElementById('confirm_delete');
    var no = document.getElementById('cancel_delete');
    var close = document.getElementById('close_delete');
    document.getElementById('param_set_name_modal').textContent = param_name;

    yes.addEventListener('click', function() { 
        document.getElementById(form_id).checked = true;   
        modal.modal("hide");
        document.getElementById('id_repo_detail_form').submit();    
    });

    no.addEventListener('click', function() {   
        modal.modal("hide");
    });

    close.addEventListener('click', function() {   
        modal.modal("hide");
    });

    modal.modal('show');
}

function loadJsonViewer(data) {
    var container = document.getElementById("jsoneditor");
    var editor = new JSONEditor(
        container, 
        {
            mode: 'text',
            onEditable: function(node) {
                return false;
            }
        }
    );
    editor.set(JSON.parse(data));
}

