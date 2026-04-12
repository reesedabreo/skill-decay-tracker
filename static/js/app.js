// 2026 Trending Skills (Real job market data)
const TRENDING_SKILLS_2026 = [
    { name: 'Next.js 15', demand: 98, category: 'Frontend', why: 'AI-powered apps & SSR', icon: 'fab fa-react' },
    { name: 'LangChain 4', demand: 95, category: 'AI/ML', why: 'Agentic workflows', icon: 'fas fa-robot' },
    { name: 'Vercel AI SDK', demand: 92, category: 'Deployment', why: 'Edge AI deployment', icon: 'fas fa-cloud' },
    { name: 'React Server Components', demand: 89, category: 'React', why: 'Next-gen performance', icon: 'fab fa-react' },
    { name: 'GraphQL Federation', demand: 87, category: 'Backend', why: 'Microservices API', icon: 'fas fa-share-alt' }
];

let currentUser = null;
let userSkills = [];
let healthChart = null;

// Skill Decay Algorithm
function calculateDecay(skill) {
    const now = Date.now();
    const daysSince = (now - new Date(skill.lastPractice).getTime()) / 86400000;
    let health = 100 - (daysSince * 2.5);
    
    if (skill.frequency) {
        const freqPenalty = Math.max(0, (skill.targetFreq || 7) - skill.frequency) * 8;
        health -= freqPenalty;
    }
    
    health = Math.max(0, Math.min(100, health));
    const risk = health > 75 ? 'low' : health > 45 ? 'medium' : 'high';
    
    return { health: Math.round(health), risk };
}

// Load user data
function loadUserData() {
    const userData = localStorage.getItem('skillUser');
    const skillsData = localStorage.getItem('skillUserSkills') || '[]';
    
    if (userData) {
        currentUser = JSON.parse(userData);
        document.getElementById('userName').textContent = currentUser.name;
        userSkills = JSON.parse(skillsData).map(skill => ({ 
            ...skill, 
            ...calculateDecay(skill) 
        }));
        initDashboard();
    } else {
        window.location.href = 'login.html';
    }
}

// Save user data
function saveUserData() {
    if (currentUser) {
        localStorage.setItem('skillUser', JSON.stringify(currentUser));
        localStorage.setItem('skillUserSkills', JSON.stringify(
            userSkills.map(({ id, ...skill }) => skill)
        ));
    }
}

// Dashboard initialization
function initDashboard() {
    renderSkills();
    updateStats();
    initChart();
    renderRecommendations();
}

// Render skills grid
function renderSkills() {
    const container = document.getElementById('skillsList');
    if (!container) return;
    
    if (userSkills.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-plus-circle fa-5x text-muted mb-4"></i>
                <h3 class="text-muted mb-3">No skills yet</h3>
                <p class="text-muted mb-0">Click "Add Skill" to get started with tracking!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = userSkills.map(skill => `
        <div class="col-xl-3 col-lg-4 col-md-6">
            <div class="card skill-card h-100 shadow-xl border-0 rounded-4 risk-${skill.risk}">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start mb-4">
                        <h5 class="card-title fw-bold mb-0">${skill.name}</h5>
                        <button class="btn btn-sm btn-outline-light p-2" onclick="editSkill('${skill.id}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                    <div class="progress mb-4" style="height: 24px; border-radius: 12px;">
                        <div class="progress-bar rounded-3" style="width: ${skill.health}%"></div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="h4 fw-bold mb-0">${skill.health}%</span>
                        <span class="badge fs-6 px-3 py-2 fw-bold bg-${skill.risk === 'low' ? 'success' : skill.risk === 'medium' ? 'warning' : 'danger'}">
                            ${skill.risk.toUpperCase()} RISK
                        </span>
                    </div>
                    <div class="text-white-50 small">
                        <div>Last practiced: ${new Date(skill.lastPractice).toLocaleDateString()}</div>
                        <div>${skill.duration} mins • ${skill.frequency || 0} sessions</div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Update stats cards
function updateStats() {
    const healthy = userSkills.filter(s => s.risk === 'low').length;
    const total = userSkills.length;
    
    document.getElementById('totalSkills').textContent = total;
    document.getElementById('healthySkills').textContent = healthy;
    document.getElementById('atRiskSkills').textContent = total - healthy;
    document.getElementById('recommendations').textContent = TRENDING_SKILLS_2026.length;
}

// Initialize radar chart
function initChart() {
    const ctx = document.getElementById('healthChart');
    if (!ctx || userSkills.length === 0) return;
    
    if (healthChart) healthChart.destroy();
    
    healthChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: userSkills.slice(0, 6).map(s => s.name),
            datasets: [{
                label: 'Skill Health',
                data: userSkills.slice(0, 6).map(s => s.health),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderWidth: 3,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { stepSize: 20, color: 'rgba(255,255,255,0.6)' },
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    pointLabels: { color: '#fff', font: { size: 12 } }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}

// Render recommendations
function renderRecommendations() {
    const container = document.getElementById('trendingList');
    if (!container) return;
    
    container.innerHTML = TRENDING_SKILLS_2026.map(skill => `
        <div class="rec-card p-4 mb-4 rounded-4 shadow-lg border-0 hover-lift">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <i class="${skill.icon} text-primary fs-4"></i>
                        <div>
                            <h6 class="fw-bold mb-1">${skill.name}</h6>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge bg-success fs-6">${skill.demand}% Demand</span>
                                <small class="text-muted">${skill.category}</small>
                            </div>
                        </div>
                    </div>
                    <p class="small text-white-50 mb-0">${skill.why}</p>
                </div>
                <button class="btn btn-outline-primary btn-sm px-4 fw-bold" onclick="addTrendingSkill('${skill.name}')">
                    <i class="fas fa-plus me-1"></i>Add
                </button>
            </div>
        </div>
    `).join('');
}

// Auth handling (login.html)
document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.getElementById('authForm');
    const toggleAuth = document.getElementById('toggleAuth');
    const authTitle = document.getElementById('authTitle');
    const authBtnText = document.getElementById('authBtnText');
    
    if (authForm) {
        let isLogin = true;
        
        authForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            
            currentUser = { name: username, email };
            localStorage.setItem('skillUser', JSON.stringify(currentUser));
            localStorage.setItem('skillUserSkills', JSON.stringify([]));
            
            window.location.href = 'dashboard.html';
        });
        
        toggleAuth.addEventListener('click', function(e) {
            e.preventDefault();
            isLogin = !isLogin;
            authTitle.textContent = isLogin ? 'Welcome Back!' : 'Join 10K+ Professionals';
            authBtnText.textContent = isLogin ? 'Sign In' : 'Create Account Free';
            toggleAuth.textContent = isLogin ? 'Need an account? Sign Up' : 'Have account? Sign In';
            document.getElementById('username').style.display = isLogin ? 'none' : 'block';
        });
    }
    
    // Dashboard init
    if (window.location.pathname.includes('dashboard.html')) {
        loadUserData();
        
        // Skill form handler
        document.getElementById('skillForm').addEventListener('submit', handleSkillSubmit);
    }
});

// Skill form handler
function handleSkillSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('skillName').value;
    const duration = parseInt(document.getElementById('duration').value);
    const notes = document.getElementById('notes').value;
    const skillId = document.getElementById('editSkillId').value;
    
    const skillData = {
        name,
        duration,
        notes: notes || '',
        lastPractice: new Date().toISOString(),
        frequency: 1,
        targetFreq: 7
    };
    
    if (skillId) {
        // Update existing
        const index = userSkills.findIndex(s => s.id === skillId);
        if (index !== -1) {
            userSkills[index] = { id: skillId, ...skillData, ...calculateDecay(skillData) };
        }
    } else {
        // Add new
        skillData.id = Date.now().toString();
        userSkills.unshift({ ...skillData, ...calculateDecay(skillData) });
    }
    
    saveUserData();
    initDashboard();
    bootstrap.Modal.getInstance(document.getElementById('skillModal')).hide();
    document.getElementById('skillForm').reset();
    document.getElementById('editSkillId').value = '';
}

// Edit skill
function editSkill(id) {
    const skill = userSkills.find(s => s.id === id);
    if (skill) {
        document.getElementById('skillName').value = skill.name;
        document.getElementById('duration').value = skill.duration || 60;
        document.getElementById('notes').value = skill.notes || '';
        document.getElementById('editSkillId').value = id;
        new bootstrap.Modal(document.getElementById('skillModal')).show();
    }
}

// Add trending skill
function addTrendingSkill(name) {
    const existing = userSkills.find(s => s.name === name);
    if (existing) {
        editSkill(existing.id);
    } else {
        document.getElementById('skillName').value = name;
        document.getElementById('duration').value = 60;
        document.getElementById('editSkillId').value = '';
        new bootstrap.Modal(document.getElementById('skillModal')).show();
    }
}

// Logout
function logout() {
    localStorage.removeItem('skillUser');
    localStorage.removeItem('skillUserSkills');
    window.location.href = 'index.html';
}
