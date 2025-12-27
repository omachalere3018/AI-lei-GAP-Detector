// ==============================
// TAB SWITCHING
// ==============================
function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}
showTab('practice');

// ==============================
// SUBJECT CHANGE
// ==============================
function updateSubjectData() {
    const subject = document.getElementById('subjectSelect').value;
    updatePractice(subject);
    updateWeakness(subject);
    updateFeedback(subject);
}

// ==============================
// PRACTICE TABLE – REAL DATA
// ==============================
function updatePractice(subject) {
    fetch(`/practice-data/${subject}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector("#practiceTable tbody");
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4">No attempts yet</td></tr>`;
                return;
            }

            data.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.topic}</td>
                    <td>${row.avg_score}%</td>
                    <td>${row.attempts * 5}%</td>
                    <td>${row.timeTaken ?? 0} sec</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Practice table error:", err));
}

// ✅ Auto-update table when user comes back to this page
document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
        const subjectSelect = document.getElementById("subjectSelect");
        if (subjectSelect && typeof updatePractice === "function") {
            updatePractice(subjectSelect.value);
        }
    }
});

// ==============================
// WEAKNESS CHART – REAL DATA
// ==============================
let weaknessChart;

function updateWeakness(subject) {
    fetch(`/weakness-data/${subject}`)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("weaknessChart").getContext("2d");

            const labels = Object.keys(data);
            const values = Object.values(data);

            if (weaknessChart) weaknessChart.destroy();

            if (labels.length === 0) {
                return;
            }

            const colors = [
                '#e74c3c', '#3498db', '#f1c40f',
                '#2ecc71', '#9b59b6', '#e67e22'
            ];

            weaknessChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: labels.map((_, i) => colors[i % colors.length])
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: `${subject} Weakness Analysis`
                        }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        });
}

// ==============================
// AI FEEDBACK – REAL DATA
// ==============================
let feedbackChart;

function updateFeedback(subject) {
    fetch(`/feedback-data/${subject}`)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("feedbackChart").getContext("2d");

            if (feedbackChart) feedbackChart.destroy();

            if (data.labels.length === 0) return;

            feedbackChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Performance",
                        data: data.scores,
                        backgroundColor: "rgba(46, 204, 113, 0.2)",
                        borderColor: "#27ae60",
                        pointBackgroundColor: "#27ae60"
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        r: { beginAtZero: true, max: 100 }
                    }
                }
            });

            const tipsList = document.getElementById("tipsList");
            tipsList.innerHTML = "";
            data.tips.forEach(t => {
                const li = document.createElement("li");
                li.innerText = t;
                tipsList.appendChild(li);
            });
        });
}

// ==============================
// STUDY CLAIM
// ==============================
document.getElementById('studyForm').addEventListener('submit', function (e) {
    e.preventDefault();
    alert("Study claim submitted!");
    this.reset();
});

// ==============================
// INIT
// ==============================
updateSubjectData();

// Initial load when page is ready
document.addEventListener("DOMContentLoaded", () => {
    const subjectSelect = document.getElementById("subjectSelect");
    if (subjectSelect && typeof updatePractice === "function") {
        updatePractice(subjectSelect.value);
    }
});
