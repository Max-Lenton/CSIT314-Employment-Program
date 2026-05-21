document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const status = document.getElementById('login-status');

    if (!form || !status) {
        return;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        status.style.color = "#4ecdc4";
        status.textContent = "Verifying...";

        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) throw response;
            return response.json();
        })
        .then(data => {
            status.textContent = data.message;
            window.location.href = '/profile';
        })
        .catch(async (errorResponse) => {
            const errorData = await errorResponse.json().catch(() => ({}));
            status.style.color = "#ff6b6b";
            status.textContent = errorData.message || "Invalid username or password.";
        })
    });
});
