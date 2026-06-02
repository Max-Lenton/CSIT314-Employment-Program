let jobData = [];

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
    jobData = await res.json();
    renderJobs(jobData, 'Search Results');
}

async function loadRecommended() {
    const res = await fetch('/api/recommendations/jobs');
    if (!res.ok) { alert('Log in as a candidate to see recommendations.'); return; }
    jobData = await res.json();
    renderJobs(jobData, '&#9733; Recommended Jobs');
}

function renderJobs(jobs, heading) {
    const container = document.getElementById('jobs-container');
    let html = heading ? `<h3 style="color:#7de8df;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">${heading}</h3>` : '';
    if (!jobs.length) { container.innerHTML = html + '<p style="color:#aaa;">No jobs found.</p>'; return; }
    html += jobs.map((j, i) => {
        const preview = j.description ? j.description.substring(0, 120) + (j.description.length > 120 ? '...' : '') : '';
        return `<div class="job" onclick="openJobModal(${i})">
            <strong>${j.title}</strong> &mdash; ${j.company}
            <div style="font-size:13px;color:#aaa;">${j.work_mode || ''} ${j.location ? '&middot; ' + j.location : ''} ${j.salary_range ? '&middot; ' + j.salary_range : ''}</div>
            ${preview ? `<div style="font-size:13px;color:#bbb;margin-top:4px;">${preview}</div>` : ''}
        </div>`;
    }).join('');
    container.innerHTML = html;
}

function openJobModal(i) {
    const j = jobData[i];
    document.getElementById('m-title').textContent = j.title;
    document.getElementById('m-company').textContent = j.company;
    const parts = [j.work_mode, j.location, j.salary_range].filter(Boolean);
    document.getElementById('m-meta').innerHTML = parts.length ? parts.join(' &middot; ') : '';
    document.getElementById('m-desc').innerHTML = j.description ? `<strong>Description:</strong> ${j.description}` : '';
    document.getElementById('m-edu').innerHTML = j.required_education ? `<strong>Education:</strong> ${j.required_education}` : '';
    document.getElementById('m-exp').innerHTML = j.required_exp != null ? `<strong>Experience:</strong> ${j.required_exp} yrs` : '';
    const skillsEl = document.getElementById('m-skills');
    skillsEl.innerHTML = j.required_skills.length
        ? j.required_skills.map(s => `<span class="skill-tag">${s}</span>`).join('')
        : '<span style="color:#888;font-size:13px;">None listed</span>';
    document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) {
    if (e.target === document.getElementById('modal-overlay')) {
        document.getElementById('modal-overlay').classList.remove('open');
    }
}

function closeModalDirect() {
    document.getElementById('modal-overlay').classList.remove('open');
}

window.addEventListener('DOMContentLoaded', loadJobs);
