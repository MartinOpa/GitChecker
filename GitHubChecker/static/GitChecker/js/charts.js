var toggleSwitch

function initializeToggle() {
    toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    toggleSwitch.addEventListener('change', updateChartsTheme, false);
}

function toggleMenu() {
    button = document.getElementById('hide');
    frame = document.getElementById('outer-frame');
    frame.classList.toggle('hidden-field');
    header = document.getElementById('preferences');
    header.classList.toggle('hidden-field');

    if (button.innerText == 'Hide menu') {
        button.innerText = 'Show menu';
    } else {
        button.innerText = 'Hide menu';
    }
}

function toggleCompare() {
    document.getElementById('set-2').classList.toggle('hidden-field');
    document.getElementById('set-label-1').classList.toggle('hidden-field');
    document.getElementById('set-label-2').classList.toggle('hidden-field');
    compare = document.getElementById('compare-on');
    button = document.getElementById('compare');

    if (button.innerText == 'Compare on') {
        compare.value = false;
        button.innerText = 'Compare off';
    } else {
        compare.value = true;
        button.innerText = 'Compare on';
    }
}

function updateChartsTheme() {
    document.getElementById('update-button').click();
}

