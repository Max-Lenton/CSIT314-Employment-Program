document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const status = document.getElementById('login-status');
    if (!form || !status) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        status.style.color = '#4ecdc4';
        status.textContent = 'Verifying...';

        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
            if (res.ok) {
                window.location.href = '/profile';
            } else {
                status.style.color = '#ff6b6b';
                status.textContent = res.data.message || 'Invalid username or password.';
            }
        });
    });
});
