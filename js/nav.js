(function () {
    const area = document.getElementById('nav-auth');
    if (!area) return;

    fetch('/api/me')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.username) {
                const span = document.createElement('span');
                span.className = 'nav-user';
                span.textContent = 'Hi, ' + data.username;

                const logout = document.createElement('a');
                logout.href = '#';
                logout.textContent = 'Logout';
                logout.addEventListener('click', function (e) {
                    e.preventDefault();
                    fetch('/api/logout', { method: 'POST' }).then(function () {
                        window.location.href = '/';
                    });
                });

                area.appendChild(span);
                area.appendChild(logout);
            } else {
                const path = window.location.pathname;

                const login = document.createElement('a');
                login.href = '/login';
                login.textContent = 'Login';
                if (path === '/login') login.classList.add('active');

                const signup = document.createElement('a');
                signup.href = '/signup';
                signup.textContent = 'Sign Up';
                if (path === '/signup') signup.classList.add('active');

                area.appendChild(login);
                area.appendChild(signup);
            }
        });
})();
