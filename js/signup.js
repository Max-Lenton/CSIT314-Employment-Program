document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('signup-form');
    const status = document.getElementById('signup-status');
    if (!form || !status) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const accountType = document.getElementById('account-type').value;
        const displayName = document.getElementById('display-name').value.trim();
        const username = document.getElementById('new-username').value.trim();
        const password = document.getElementById('new-password').value;

        status.style.color = '#4ecdc4';
        status.textContent = 'Creating account...';

        fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                account_type: accountType,
                display_name: displayName,
                username: username,
                password: password
            })
        })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
            if (res.ok) {
                status.textContent = res.data.message;
                form.reset();
                setTimeout(function () { window.location.href = '/login'; }, 2000);
            } else {
                status.style.color = '#ff6b6b';
                status.textContent = res.data.message || 'An error occurred during sign up.';
            }
        });
    });
});
