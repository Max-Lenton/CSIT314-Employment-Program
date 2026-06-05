let allItems = [];

async function loadInbox() {
    const res = await fetch('/api/inbox');
    if (!res.ok) { document.getElementById('inbox-container').innerHTML = '<p style="color:#ff6b6b;">Could not load inbox.</p>'; return; }
    allItems = await res.json();
    renderInbox(allItems);
}

function filterInbox(status) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active-filter'));
    document.getElementById('filter-' + status).classList.add('active-filter');
    const filtered = status === 'all' ? allItems : allItems.filter(i => i.status === status);
    renderInbox(filtered);
}

function renderInbox(items) {
    const container = document.getElementById('inbox-container');
    if (!items.length) {
        container.innerHTML = '<p style="color:#aaa;">Nothing here yet.</p>';
        return;
    }

    const isEmployer = window.ACCOUNT_TYPE === 'employer';
    container.innerHTML = items.map(item => {
        const statusClass = item.status === 'accepted' ? 'inbox-accepted' : item.status === 'rejected' ? 'inbox-rejected' : 'inbox-pending';
        const typeLabel = item.type === 'application' ? 'Application' : 'Job Offer';

        let titleHtml, subtitle;
        if (isEmployer) {
            titleHtml = `<a href="/candidate/${item.candidate_id}" style="color:inherit;text-decoration:none;border-bottom:1px solid #4ecdc4;">${item.candidate_name}</a>`;
            subtitle = `Applied for: <a href="/job/${item.job_id}" style="color:#aaa;text-decoration:none;border-bottom:1px dotted #555;">${item.job_title}</a>`;
        } else {
            titleHtml = `<a href="/job/${item.job_id}" style="color:inherit;text-decoration:none;border-bottom:1px solid #4ecdc4;">${item.job_title}</a>`;
            subtitle = item.type === 'application'
                ? `Your application to <strong>${item.company}</strong>`
                : `Job offer from <strong>${item.company}</strong>`;
        }

        const actions = item.status === 'pending' ? `
            <div style="display:flex;gap:8px;margin-top:10px;">
                ${canAccept(item, isEmployer) ? `<button onclick="event.stopPropagation();respond(${item.id}, 'accept')" style="width:auto;padding:6px 14px;">Accept</button>` : ''}
                ${canReject(item, isEmployer) ? `<button onclick="event.stopPropagation();respond(${item.id}, 'reject')" class="btn-danger" style="width:auto;padding:6px 14px;">Reject</button>` : ''}
            </div>` : '';

        return `<div class="inbox-item ${statusClass}">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;">
                <div>
                    <strong style="font-size:15px;">${titleHtml}</strong>
                    <div style="font-size:13px;color:#aaa;margin-top:2px;">${subtitle}</div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <span class="inbox-badge inbox-type-${item.type}">${typeLabel}</span>
                    <span class="inbox-badge ${statusClass}-badge">${item.status}</span>
                    <div style="font-size:11px;color:#555;margin-top:4px;">${item.created_at}</div>
                </div>
            </div>
            ${actions}
        </div>`;
    }).join('');
}

function canAccept(item, isEmployer) {
    // Employer accepts applications; candidate accepts offers
    if (isEmployer) return item.type === 'application';
    return item.type === 'offer';
}

function canReject(item, isEmployer) {
    if (isEmployer) return item.type === 'application';
    return item.type === 'offer';
}

async function respond(id, action) {
    const res = await fetch(`/api/inbox/${id}/${action}`, { method: 'POST' });
    if (res.ok) loadInbox();
}

window.addEventListener('DOMContentLoaded', loadInbox);
