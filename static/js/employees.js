async function loadCandidates() {
    const kw = document.getElementById('kw').value.trim();
    const skill = document.getElementById('skill').value.trim();
    const edu = document.getElementById('edu').value.trim();
    const minexp = document.getElementById('minexp').value.trim();
    const mode = document.getElementById('mode').value;
    const params = new URLSearchParams();
    if (kw) params.append('keyword', kw);
    if (skill) params.append('skill', skill);
    if (edu) params.append('education', edu);
    if (minexp) params.append('min_exp', minexp);
    if (mode) params.append('work_mode', mode);
    const res = await fetch('/api/candidates?' + params.toString());
    const candidates = await res.json();
    renderCandidates(candidates, 'Search Results');
}

async function loadRecommended() {
    const res = await fetch('/api/recommendations/candidates');
    if (!res.ok) { alert('Log in as an employer to see recommendations.'); return; }
    const candidates = await res.json();
    renderCandidates(candidates, '&#9733; Recommended Candidates');
}

function renderCandidates(candidates, heading) {
    const container = document.getElementById('candidates-container');
    let html = heading ? `<h3 style="color:#7de8df;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">${heading}</h3>` : '';
    if (!candidates.length) { container.innerHTML = html + '<p style="color:#aaa;">No candidates found.</p>'; return; }
    html += candidates.map(c => {
        const skills = c.skills.length ? c.skills.join(', ') : 'None listed';
        const exp = c.work_experience.map(w => `${w.job_title} @ ${w.company_name}`).join('; ') || 'None listed';
        return `<div class="job">
            <strong>${c.name}</strong>
            <div style="font-size:13px;color:#aaa;">${c.education || ''} ${c.major ? '(' + c.major + ')' : ''} &middot; ${c.years_exp != null ? c.years_exp + ' yrs exp' : 'Exp not listed'}</div>
            <div style="font-size:13px;color:#aaa;">${c.preferred_mode || ''} ${c.preferred_loc ? '&middot; ' + c.preferred_loc : ''}</div>
            <div style="font-size:12px;color:#7de8df;margin-top:4px;">Skills: ${skills}</div>
            <div style="font-size:12px;color:#bbb;margin-top:2px;">Experience: ${exp}</div>
        </div>`;
    }).join('');
    container.innerHTML = html;
}

window.addEventListener('DOMContentLoaded', loadCandidates);
