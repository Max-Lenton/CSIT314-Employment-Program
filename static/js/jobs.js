document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('jobs-container');
    if (!container) {
        return;
    }

    const jobs = [
        { title: 'Research Analyst', team: 'Bioinformatics' },
        { title: 'Lab Operations Coordinator', team: 'Clinical' },
        { title: 'Data Engineer', team: 'Science Platform' }
    ];

    jobs.forEach(function (job) {
        const block = document.createElement('div');
        block.className = 'job';
        block.innerHTML = '<strong>' + job.title + '</strong><div>Team: ' + job.team + '</div>';
        container.appendChild(block);
    });
});
