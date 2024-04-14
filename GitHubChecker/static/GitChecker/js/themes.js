var toggleSwitch;
var currentTheme;

function initialize() {
    toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;
    document.cookie = 'theme=' + currentTheme + ';expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/;SameSite=Lax';

    toggleSwitch.addEventListener('change', switchTheme, false);
    
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);

        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    }
}

function switchTheme(e) {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        document.cookie = 'theme=dark;expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/;SameSite=Lax';
    }
    else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        document.cookie = 'theme=light;expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/;SameSite=Lax';
    }    
}

function reloadAfterToggle() {
    location.reload();
}

function initializeToggleListener() {
    toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    toggleSwitch.addEventListener('change', reloadAfterToggle, false);
}

