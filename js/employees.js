let candidateData = [];

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
    candidateData = await res.json();
    renderCandidates(candidateData, 'Search Results');
}

async function loadRecommended() {
    const res = await fetch('/api/recommendations/candidates');
    if (!res.ok) { alert('Log in as an employer to see recommendations.'); return; }
    candidateData = await res.json();
    renderCandidates(candidateData, '&#9733; Recommended Candidates');
}

function renderCandidates(candidates, heading) {
    const container = document.getElementById('candidates-container');
    let html = heading ? `<h3 style="color:#7de8df;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">${heading}</h3>` : '';
    if (!candidates.length) { container.innerHTML = html + '<p style="color:#aaa;">No candidates found.</p>'; return; }
    html += candidates.map((c, i) => {
        const topSkills = c.skills.slice(0, 4).join(', ') + (c.skills.length > 4 ? ` +${c.skills.length - 4} more` : '');
        return `<div class="job" onclick="openCandidateModal(${i})">
            <strong>${c.name}</strong>
            <div style="font-size:13px;color:#aaa;">${c.education || ''} ${c.major ? '(' + c.major + ')' : ''} ${c.years_exp != null ? '&middot; ' + c.years_exp + ' yrs exp' : ''}</div>
            <div style="font-size:13px;color:#aaa;">${c.preferred_mode || ''} ${c.preferred_loc ? '&middot; ' + c.preferred_loc : ''}</div>
            ${topSkills ? `<div style="font-size:12px;color:#7de8df;margin-top:4px;">${topSkills}</div>` : ''}
        </div>`;
    }).join('');
    container.innerHTML = html;
}

function openCandidateModal(i) {
    const c = candidateData[i];
    document.getElementById('m-name').textContent = c.name;
    document.getElementById('m-edu').textContent = [c.education, c.major ? `(${c.major})` : ''].filter(Boolean).join(' ');
    document.getElementById('m-contact').innerHTML = c.contact_info ? `<strong>Contact:</strong> ${c.contact_info}` : '';
    const meta = [
        c.years_exp != null ? `${c.years_exp} yrs experience` : null,
        c.preferred_mode,
        c.preferred_loc
    ].filter(Boolean).join(' &middot; ');
    document.getElementById('m-meta').innerHTML = meta;
    const skillsEl = document.getElementById('m-skills');
    skillsEl.innerHTML = c.skills.length
        ? c.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')
        : '<span style="color:#888;font-size:13px;">None listed</span>';
    const expLines = c.work_experience.map(w => `${w.job_title} @ ${w.company_name}`).join('<br>');
    document.getElementById('m-exp').innerHTML = expLines ? `<strong>Experience:</strong><br>${expLines}` : '';
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

window.addEventListener('DOMContentLoaded', loadCandidates);
