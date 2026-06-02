document.addEventListener('DOMContentLoaded', function () {
    const message = document.getElementById('home-message');
    if (message) {
        const now = new Date().toLocaleString();
        message.textContent = 'Homepage ready. Loaded at ' + now + '.';
    }
});
