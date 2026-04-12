document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('healthChart');

    if (!ctx) return;

    const skillNames = window.skillNames || [];
    const healthScores = window.healthScores || [];

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: skillNames,
            datasets: [{
                label: 'Skill Health',
                data: healthScores,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
});