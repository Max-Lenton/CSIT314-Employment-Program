const reqSkills = new Set();

function renderReqSkillTags() {
    const list = document.getElementById('req-skills-list');
    list.innerHTML = '';
    reqSkills.forEach(name => {
        const span = document.createElement('span');
        span.className = 'skill-tag';
        span.innerHTML = `${name} <button type="button" onclick="removeReqSkill('${name}')" style="background:none;border:none;color:#ff6b6b;cursor:pointer;padding:0 4px;width:auto;">×</button>`;
        list.appendChild(span);
    });
}

function addReqSkill() {
    const input = document.getElementById('new-req-skill');
    const val = input.value.trim();
    if (val) { reqSkills.add(val); input.value = ''; renderReqSkillTags(); }
}

function addReqSkillFromSelect(sel) {
    if (sel.value) { reqSkills.add(sel.value); sel.value = ''; renderReqSkillTags(); }
}

function removeReqSkill(name) {
    reqSkills.delete(name);
    renderReqSkillTags();
}

async function deleteJob(id) {
    if (!confirm('Delete this job posting?')) return;
    const res = await fetch(`/api/jobs/${id}`, { method: 'DELETE' });
    if (res.ok) {
        const el = document.getElementById(`job-${id}`);
        if (el) el.remove();
    }
}

async function upgradeMembership() {
    const res = await fetch('/api/upgrade_membership', { method: 'POST' });
    const data = await res.json();
    if (res.ok) { alert(data.message + ' Reload to see your new status.'); location.reload(); }
    else alert(data.message);
}

window.addEventListener('DOMContentLoaded', function () {
    document.getElementById('create-job-form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const payload = {
            job_title: document.getElementById('job_title').value.trim(),
            job_description: document.getElementById('job_description').value.trim(),
            required_education: document.getElementById('required_education').value.trim(),
            required_exp: parseInt(document.getElementById('required_exp').value) || null,
            work_mode: document.getElementById('work_mode').value,
            job_location: document.getElementById('job_location').value.trim(),
            salary_range: document.getElementById('salary_range').value.trim(),
            required_skills: Array.from(reqSkills),
        };
        const res = await fetch('/api/jobs/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        const el = document.getElementById('create-job-status');
        el.textContent = data.message;
        el.style.color = res.ok ? '#4ecdc4' : '#ff6b6b';
        if (res.ok) {
            const noMsg = document.getElementById('no-jobs-msg');
            if (noMsg) noMsg.remove();
            const div = document.createElement('div');
            div.className = 'job';
            div.id = `job-${data.id}`;
            div.innerHTML = `<strong>${payload.job_title}</strong>
                <div>${payload.work_mode || ''} ${payload.job_location ? '&middot; ' + payload.job_location : ''}</div>
                ${payload.salary_range ? '<div style="font-size:13px;color:#aaa;">' + payload.salary_range + '</div>' : ''}
                <button onclick="deleteJob(${data.id})" style="float:right;background:#ff6b6b;color:#111;padding:4px 10px;width:auto;font-size:12px;border-radius:6px;border:none;cursor:pointer;margin-top:-40px;">Delete</button>`;
            document.getElementById('job-postings-list').appendChild(div);
            e.target.reset();
            reqSkills.clear();
            renderReqSkillTags();
        }
    });
});
