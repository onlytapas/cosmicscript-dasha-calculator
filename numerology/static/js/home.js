// Move focus to the next date field once a field is complete.
(function () {
    const day = document.getElementById('day');
    const month = document.getElementById('month');
    const year = document.getElementById('year');
    day.addEventListener('input', () => { if (day.value.length >= 2) month.focus(); });
    month.addEventListener('input', () => { if (month.value.length >= 2) year.focus(); });
})();
