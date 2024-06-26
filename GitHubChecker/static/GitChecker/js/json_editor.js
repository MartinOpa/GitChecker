var editor;
var current_json_id = '';
var current_label_id = '';
var current_version_id = '';
var current_editor_active_id = '';

function loadJsonEditor() {
    var container = document.getElementById("jsoneditor");
    editor = new JSONEditor(container, {mode: 'text', modes: ['text', 'code']});

    window.addEventListener('DOMContentLoaded', (event) => {
        editFormData('id_testparameters_set-0-parameters', 'id_testparameters_set-0-param_name', 'id_testparameters_set-0-version', 'id_testparameters_set-0-active');   
        
        // hide default Django delete checkboxes
        var deleteCheckboxes = $("input[type='checkbox'][id*='-DELETE']");
        deleteCheckboxes.each(function(){
            $(this).addClass('hidden-field');
        });
    }); 
}

function editFormData(form_json_id, form_label_id, form_version_id, form_editor_active_id) {
    if (current_json_id != '') {
        document.getElementById(current_json_id).textContent = getJsonData();
        document.getElementById(current_label_id).value = document.getElementById('id_editor_label').value;
        document.getElementById(current_version_id).value = document.getElementById('id_editor_version').value;
        document.getElementById(current_editor_active_id).checked = document.getElementById('id_editor_active').checked;
        //document.getElementById(current_label_id + '_table').innerText = document.getElementById(current_label_id).value;
    }
    current_json_id = form_json_id;
    current_label_id = form_label_id;
    current_version_id = form_version_id;
    current_editor_active_id = form_editor_active_id;
    editor.set(JSON.parse(document.getElementById(current_json_id).textContent));
    document.getElementById('id_editor_label').value = document.getElementById(current_label_id).value;
    document.getElementById('id_editor_version').value = document.getElementById(current_version_id).value;
    document.getElementById('id_editor_active').checked = document.getElementById(current_editor_active_id).checked;
}

function showModalMessage(msg) {
    var modal = $('#modal_run_tests');
    var ok = document.getElementById('ok_run_tests');
    var close = document.getElementById('close_run_tests');
    document.getElementById('text_run_tests').textContent = msg;

    ok.addEventListener('click', function() {  
        modal.modal("hide");   
    });

    close.addEventListener('click', function() {   
        modal.modal("hide");
    });

    modal.modal('show');
}

function runTests(repo_id, csrftoken) {
    try {
        fetch(window.location.protocol + '//' + window.location.host + '/runtests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                'repo_id': repo_id
            })
        }).then((response) => {
            if (response.ok) {
                showModalMessage('Test task launched successfully.');
            } else {
                throw new Error('Got unexpected response code: ' + response.status);
            }
        }).catch((error) => {
            showModalMessage('An error occured when processing the request. ' + error);
        });    
    } catch (error) {
        showModalMessage('An error occured when processing the request. ' + error);
    }
}

function beforeSubmit() {
    try {
        document.getElementById(current_json_id).textContent = getJsonData();
        document.getElementById(current_label_id).value = document.getElementById('id_editor_label').value; 
        document.getElementById(current_version_id).value = document.getElementById('id_editor_version').value; 
        document.getElementById(current_editor_active_id).checked = document.getElementById('id_editor_active').checked;
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

