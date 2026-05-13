document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const status = document.getElementById('login-status');

    if (!form || !status) {
        return;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const username = document.getElementById('username').value.trim();
        status.textContent = username ? 'Welcome, ' + username + '. Login flow can be connected next.' : 'Please enter a username.';
    });
});
