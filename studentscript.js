// Sample subject-wise data
const subjectData = {
    DSA: {
        practice: [
            { test: 'Array Test', score: 75, growth: 5 },
            { test: 'Linked List Test', score: 65, growth: 3 }
        ],
        weakness: { Arrays: 5, LinkedList: 8, Trees: 4 },
        feedback: { 
            scores: [75, 65, 60], 
            labels: ['Arrays','LinkedList','Trees'], 
            tips: ['Revise Linked Lists', 'Practice Tree traversal'] 
        }
    },
    DBMS: {
        practice: [
            { test: 'ER Diagram Test', score: 80, growth: 4 },
            { test: 'SQL Query Test', score: 55, growth: -2 }
        ],
        weakness: { 'ER Diagrams': 2, 'SQL Queries': 6, 'Normalization': 4 },
        feedback: { 
            scores: [80,55,60], 
            labels: ['ER Diagrams','SQL Queries','Normalization'], 
            tips: ['Focus on SQL Queries', 'Practice Normalization'] 
        }
    },
    OS: {
        practice: [
            { test: 'Process Management', score: 70, growth: 2 },
            { test: 'Memory Management', score: 75, growth: 1 }
        ],
        weakness: { 'Process': 4, 'Memory': 5, 'File System': 3 },
        feedback: { 
            scores: [70,75,65], 
            labels: ['Process','Memory','File System'], 
            tips: ['Revise Process scheduling', 'Practice Memory management problems'] 
        }
    },
    CN: {
        practice: [
            { test: 'TCP/IP Test', score: 65, growth: 3 },
            { test: 'Routing Test', score: 60, growth: 2 }
        ],
        weakness: { 'TCP/IP': 5, Routing: 6, 'Network Security': 4 },
        feedback: { 
            scores: [65,60,70], 
            labels: ['TCP/IP','Routing','Network Security'], 
            tips: ['Revise Routing algorithms', 'Practice TCP/IP concepts'] 
        }
    }
};

// Switch tabs
function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}
showTab('practice');

// Update all subject-dependent data
function updateSubjectData() {
    const subject = document.getElementById('subjectSelect').value;
    updatePractice(subject);
    updateWeakness(subject);
    updateFeedback(subject);
}

// Practice/Test Table
function updatePractice(subject) {
    const tbody = document.querySelector('#practiceTable tbody');
    tbody.innerHTML = '';
    subjectData[subject].practice.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.test}</td><td>${item.score}</td><td>${item.growth}%</td>`;
        tbody.appendChild(tr);
    });
}

// Weakness Analysis Chart
let weaknessChart;
function updateWeakness(subject) {
    const ctx = document.getElementById('weaknessChart').getContext('2d');
    const data = subjectData[subject].weakness;
    const labels = Object.keys(data);
    const values = Object.values(data);

    if (weaknessChart) weaknessChart.destroy();

    weaknessChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mistakes per Topic',
                data: values,
                backgroundColor: ['#e74c3c','#f1c40f','#3498db','#2ecc71']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false }, title: { display: true, text: `${subject} Weakness Analysis` } }
        }
    });
}

// AI Feedback Chart
let feedbackChart;
function updateFeedback(subject) {
    const ctx = document.getElementById('feedbackChart').getContext('2d');
    const feedback = subjectData[subject].feedback;

    if (feedbackChart) feedbackChart.destroy();

    feedbackChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: feedback.labels,
            datasets: [{
                label: 'Scores',
                data: feedback.scores,
                fill: true,
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderColor: '#27ae60',
                pointBackgroundColor: '#27ae60'
            }]
        },
        options: { responsive: true, scales: { r: { beginAtZero: true } } }
    });

    // Update tips
    const tipsList = document.getElementById('tipsList');
    tipsList.innerHTML = '';
    feedback.tips.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        tipsList.appendChild(li);
    });
}

// Study Claim Form
document.getElementById('studyForm').addEventListener('submit', function(e){
    e.preventDefault();
    alert("Study claim submitted!");
    this.reset();
});

// Initialize default subject
updateSubjectData();
