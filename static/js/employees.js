document.addEventListener('DOMContentLoaded', function () {
    const list = document.getElementById('employee-list');
    if (!list) {
        return;
    }

    const employees = ['John Smith', 'John Constintine', 'John Garcia', 'Richard Johnson'];
    employees.forEach(function (name) {
        const item = document.createElement('li');
        item.textContent = name;
        list.appendChild(item);
    });
});
