// currentSkills is seeded from the template via window.INITIAL_SKILLS
const currentSkills = new Set(window.INITIAL_SKILLS || []);

function renderSkillTags() {
    const list = document.getElementById('skills-list');
    list.innerHTML = '';
    currentSkills.forEach(name => {
        const span = document.createElement('span');
        span.className = 'skill-tag';
        span.dataset.skill = name;
        span.innerHTML = `${name} <button onclick="removeSkillTag('${name}')" style="background:none;border:none;color:#ff6b6b;cursor:pointer;padding:0 4px;width:auto;">×</button>`;
        list.appendChild(span);
    });
}

function removeSkillTag(name) {
    currentSkills.delete(name);
    renderSkillTags();
}

function addSkillFromInput() {
    const input = document.getElementById('new-skill-input');
    const val = input.value.trim();
    if (val) { currentSkills.add(val); input.value = ''; renderSkillTags(); }
}

function addSkillFromSelect(sel) {
    if (sel.value) { currentSkills.add(sel.value); sel.value = ''; renderSkillTags(); }
}

async function saveSkills() {
    const res = await fetch('/api/update_skills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: Array.from(currentSkills) })
    });
    const data = await res.json();
    const el = document.getElementById('skills-status');
    el.textContent = data.message;
    el.style.color = res.ok ? '#4ecdc4' : '#ff6b6b';
}

async function addWorkExp() {
    const title = document.getElementById('exp-title').value.trim();
    const company = document.getElementById('exp-company').value.trim();
    if (!title || !company) { alert('Please enter both job title and company.'); return; }
    const res = await fetch('/api/work_experience', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_title: title, company_name: company })
    });
    const data = await res.json();
    const el = document.getElementById('work-exp-status');
    if (res.ok) {
        el.textContent = 'Added!';
        el.style.color = '#4ecdc4';
        document.getElementById('exp-title').value = '';
        document.getElementById('exp-company').value = '';
        const noMsg = document.getElementById('no-exp-msg');
        if (noMsg) noMsg.remove();
        const div = document.createElement('div');
        div.className = 'job';
        div.id = `we-${data.id}`;
        div.innerHTML = `<strong>${title}</strong> @ ${company}
            <button onclick="deleteWorkExp(${data.id})" style="float:right;background:#ff6b6b;color:#111;padding:4px 10px;width:auto;font-size:12px;border-radius:6px;border:none;cursor:pointer;">Remove</button>`;
        document.getElementById('work-exp-list').appendChild(div);
    } else {
        el.textContent = data.message;
        el.style.color = '#ff6b6b';
    }
}

async function deleteWorkExp(id) {
    const res = await fetch(`/api/work_experience/${id}`, { method: 'DELETE' });
    if (res.ok) {
        const el = document.getElementById(`we-${id}`);
        if (el) el.remove();
    }
}

async function upgradeMembership() {
    const res = await fetch('/api/upgrade_membership', { method: 'POST' });
    const data = await res.json();
    if (res.ok) { alert(data.message + ' Reload the page to see your new status.'); location.reload(); }
    else alert(data.message);
}

window.addEventListener('DOMContentLoaded', function () {
    document.getElementById('preferences-form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const payload = {
            education: document.getElementById('education').value.trim(),
            major: document.getElementById('major').value.trim(),
            contact_info: document.getElementById('contact_info').value.trim(),
            years_exp: parseInt(document.getElementById('years_exp').value) || null,
            preferred_mode: document.getElementById('preferred_mode').value,
            preferred_loc: document.getElementById('preferred_loc').value.trim(),
        };
        const res = await fetch('/api/update_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        const el = document.getElementById('preferences-status');
        el.textContent = data.message;
        el.style.color = res.ok ? '#4ecdc4' : '#ff6b6b';
    });

    document.getElementById('resume-upload-form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('resume', document.getElementById('resume-file').files[0]);
        const res = await fetch('/upload_resume', { method: 'POST', body: formData });
        const data = await res.json();
        const el = document.getElementById('upload-status');
        el.textContent = data.message;
        el.style.color = res.ok ? '#4ecdc4' : '#ff6b6b';
    });
});
