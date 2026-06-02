async function loadJobs() {
    const kw = document.getElementById('kw').value.trim();
    const mode = document.getElementById('mode').value;
    const loc = document.getElementById('loc').value.trim();
    const maxexp = document.getElementById('maxexp').value.trim();
    const params = new URLSearchParams();
    if (kw) params.append('keyword', kw);
    if (mode) params.append('work_mode', mode);
    if (loc) params.append('location', loc);
    if (maxexp) params.append('max_exp', maxexp);
    const res = await fetch('/api/jobs?' + params.toString());
    const jobs = await res.json();
    renderJobs(jobs, 'Search Results');
}

async function loadRecommended() {
    const res = await fetch('/api/recommendations/jobs');
    if (!res.ok) { alert('Log in as a candidate to see recommendations.'); return; }
    const jobs = await res.json();
    renderJobs(jobs, '&#9733; Recommended Jobs');
}

function renderJobs(jobs, heading) {
    const container = document.getElementById('jobs-container');
    let html = heading ? `<h3 style="color:#7de8df;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">${heading}</h3>` : '';
    if (!jobs.length) { container.innerHTML = html + '<p style="color:#aaa;">No jobs found.</p>'; return; }
    html += jobs.map(j => {
        const skills = j.required_skills.length ? j.required_skills.join(', ') : 'None listed';
        return `<div class="job">
            <strong>${j.title}</strong> &mdash; ${j.company}
            <div style="font-size:13px;color:#aaa;">${j.work_mode || ''} ${j.location ? '&middot; ' + j.location : ''} ${j.salary_range ? '&middot; ' + j.salary_range : ''}</div>
            <div style="font-size:13px;color:#bbb;margin-top:4px;">${j.description ? j.description.substring(0, 160) + (j.description.length > 160 ? '...' : '') : ''}</div>
            <div style="font-size:12px;color:#7de8df;margin-top:4px;">Skills: ${skills} &middot; Exp: ${j.required_exp != null ? j.required_exp + ' yrs' : 'Any'}</div>
        </div>`;
    }).join('');
    container.innerHTML = html;
}

window.addEventListener('DOMContentLoaded', loadJobs);
