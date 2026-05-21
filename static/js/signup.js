document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('signup-form');
    const status = document.getElementById('signup-status');

    if (!form || !status) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const accountType = document.getElementById('account-type').value;
        const displayName = document.getElementById('display-name').value.trim();
        const username = document.getElementById('new-username').value.trim();
        const password = document.getElementById('new-password').value;

        status.style.color = "#4ecdc4";
        status.textContent = "Creating account...";

        fetch('/api/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                account_type: accountType,
                display_name: displayName,
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
            form.reset(); // Clear form on success
            
            // Optional: Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        })
        .catch(async (errorResponse) => {
            const errorData = await errorResponse.json().catch(() => ({}));
            status.style.color = "#ff6b6b"; // Red error color
            status.textContent = errorData.message || "An error occurred during signup.";
        });
    });
});