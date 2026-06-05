function navSearch() {
    const q = document.getElementById('nav-search').value.trim();
    if (q) window.location.href = '/jobs?q=' + encodeURIComponent(q);
}

document.addEventListener('DOMContentLoaded', function () {
    // Allow pressing Enter in search box
    const searchInput = document.getElementById('nav-search');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') navSearch();
        });
    }

    // Share trigger placeholder focus
    const shareTrigger = document.getElementById('share-trigger');
    if (shareTrigger) {
        shareTrigger.addEventListener('click', function () {
            alert('Post feature coming soon!');
        });
    }
});

