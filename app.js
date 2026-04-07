/* 
 * PCCOE OneBridge - Core Frontend Architecture
 * Formal SPA Base, Layout Wrappers & Global State Manager
 */

// --- Global State Store ---
const GlobalState = {
    user: {
        name: "Jane Smith",
        year: "3rd Year",
        branch: "Computer Engineering",
        roles: ["student"],
        needsEOC: true
    },
    ui: {
        currentRoute: "dashboard",
        highContrastMode: false
    },
    listeners: [],
    
    // Subscribe to state mutations
    subscribe(callback) {
        this.listeners.push(callback);
    },
    
    // Dispatch mutations
    setState(newState) {
        this.ui = { ...this.ui, ...newState.ui };
        this.user = { ...this.user, ...newState.user };
        this.notify();
    },
    
    notify() {
        this.listeners.forEach(fn => fn(this));
    }
};

// --- Mock Data Layer ---
const userData = {
    name: "Jane Smith",
    year: "3rd Year",
    branch: "Computer Engineering",
    alerts: 2
};

const mockOpportunities = [
    { type: "Scholarship", title: "MahaDBT State Scholarship", deadline: "Oct 30", matcher: "90% Match" },
    { type: "Internship", title: "Web Dev Intern at TechCorp", deadline: "Nov 15", matcher: "Highly Recommended" },
    { type: "Fellowship", title: "Innovation Research Fellowship", deadline: "Dec 01", matcher: "Eligible" }
];

const mockFacilities = [
    { name: "Central Library", status: "Open", capacity: "45/100 Seats" },
    { name: "Maker Space", status: "Requires Booking", capacity: "Available Tomorrow" },
    { name: "Accessibility Ramp - Main Bldg", status: "Operational", capacity: "Verified" }
];

// --- Views Generation ---

const generateDashboard = () => `
    <div class="view-header">
        <h2>Welcome back, ${userData.name}!</h2>
        <p>Here is your daily snapshot and pending items.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card">
            <div class="card-title">
                <span class="card-icon">📝</span>
                <h3>My Requests</h3>
            </div>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 1rem;">
                <li style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Bonafide Certificate</span>
                    <span class="badge approved">Approved</span>
                </li>
                <li style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Library Overdue Issue</span>
                    <span class="badge pending">Under Review</span>
                </li>
            </ul>
            <br>
            <button class="btn-primary" style="width: 100%;">Raise New Request</button>
        </div>
        
        <div class="glass-card" style="border-color: rgba(139, 92, 246, 0.4);">
            <div class="card-title" style="color: var(--eoc-brand-light);">
                <span class="card-icon" style="background: rgba(139, 92, 246, 0.2);">🤝</span>
                <h3>EOC Reminders</h3>
            </div>
            <p style="margin-bottom: 1rem;">Disabled Student Scholarship renewal is due next week. Have you prepared your documents?</p>
            <button class="btn-primary" style="background: var(--eoc-brand); width: 100%;">View Guidelines</button>
        </div>

        <div class="glass-card">
            <div class="card-title">
                <span class="card-icon">✨</span>
                <h3>AI Career Matches</h3>
            </div>
            <p style="margin-bottom: 1rem; color: var(--text-secondary);">Based on your profile (3rd Yr Comp):</p>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.5rem;">
                ${mockOpportunities.slice(0, 2).map(opp => `
                    <li style="padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <strong>${opp.title}</strong><br>
                        <small style="color: var(--secondary);">${opp.matcher}</small>
                    </li>
                `).join('')}
            </ul>
        </div>
    </div>
`;

const generateOpportunities = () => `
    <div class="view-header">
        <h2>Opportunities Hub</h2>
        <p>Discover Scholarships, Fellowships, Internships, and Jobs tailored for you.</p>
    </div>
    <div class="opportunities-grid">
        ${mockOpportunities.map(opp => `
            <div class="glass-card">
                <span class="badge pending" style="margin-bottom: 1rem; display: inline-block;">${opp.type}</span>
                <h3 style="margin-bottom: 0.5rem;">${opp.title}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">Deadline: ${opp.deadline}</p>
                <div style="display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
                    <span style="color: var(--secondary); font-size: 0.9rem;">${opp.matcher}</span>
                    <button class="btn-primary">Apply Now</button>
                </div>
            </div>
        `).join('')}
    </div>
`;

const generateFacilities = () => `
    <div class="view-header">
        <h2>Facilities Access</h2>
        <p>Check availability and book campus facilities digitally.</p>
    </div>
    <div class="opportunities-grid">
        ${mockFacilities.map(fac => `
            <div class="glass-card">
                <h3 style="margin-bottom: 0.5rem;">${fac.name}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">Status: <strong style="color: white;">${fac.status}</strong></p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.9rem;">${fac.capacity}</span>
                    <button class="btn-primary" ${fac.status.includes('Booking') ? '' : 'disabled style="opacity: 0.5; cursor: not-allowed;"'}>Book Slot</button>
                </div>
            </div>
        `).join('')}
    </div>
`;

const generateSupport = () => `
    <div class="view-header">
        <h2>Support Center</h2>
        <p>Need help? Reach out to our 3-tier support system.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card">
            <h3>💻 Technical Support</h3>
            <p style="margin: 1rem 0; color: var(--text-secondary);">LMS issues, Login problems, Wi-Fi connectivity.</p>
            <button class="btn-primary">Raise IT Ticket</button>
        </div>
        <div class="glass-card">
            <h3>📚 Academic Support</h3>
            <p style="margin: 1rem 0; color: var(--text-secondary);">Subject guidance, Mentorship, Exam queries.</p>
            <button class="btn-primary">Contact Mentor</button>
        </div>
        <div class="glass-card">
            <h3>🌿 Wellbeing & Counseling</h3>
            <p style="margin: 1rem 0; color: var(--text-secondary);">Mental health, Stress relief, Confidential counseling.</p>
            <button class="btn-primary" style="background: var(--secondary);">Book Session</button>
        </div>
    </div>
`;

const generateEoc = () => `
    <div class="view-header">
        <h2 style="color: var(--eoc-brand-light);">EOC Integration & Inclusion</h2>
        <p>Equal Opportunity Cell: Support for disabilities, disadvantaged groups, and grievance redressal.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="border: 1px solid var(--eoc-brand);">
            <h3>Accessibility Request</h3>
            <p style="margin: 1rem 0; color: var(--text-secondary);">Request a scribe, accessible study material, or report a physical access barrier on campus.</p>
            <button class="btn-primary" style="background: var(--eoc-brand); width: 100%;">Submit Request</button>
        </div>
        <div class="glass-card" style="border: 1px solid var(--eoc-brand);">
            <h3>Confidential Grievance</h3>
            <p style="margin: 1rem 0; color: var(--text-secondary);">Report discrimination safely and privately. Only EOC admins will have access.</p>
            <button class="btn-primary" style="background: transparent; border: 1px solid var(--accent); color: var(--accent); width: 100%;">File Report</button>
        </div>
    </div>
`;

// --- Layout Wrapper & SPA Core Engine ---

const root = document.getElementById('app-root');
const navItems = document.querySelectorAll('.nav-item');

// Live region for screen readers notifying route changes
const routeAnnouncer = document.createElement('div');
routeAnnouncer.setAttribute('aria-live', 'assertive');
routeAnnouncer.className = 'sr-only';
document.body.appendChild(routeAnnouncer);

const renderView = (route) => {
    // Standard Layout Wrapper Fade Out Focus
    root.style.opacity = 0;
    root.setAttribute('aria-busy', 'true');
    
    setTimeout(() => {
        let content = '';
        switch(route) {
            case 'dashboard': content = generateDashboard(); break;
            case 'opportunities': content = generateOpportunities(); break;
            case 'facilities': content = generateFacilities(); break;
            case 'support': content = generateSupport(); break;
            case 'eoc': content = generateEoc(); break;
            default: content = generateDashboard();
        }
        
        // Inject layout with a standard screen shell template
        root.innerHTML = `
            <section class="module-wrapper" role="region" aria-label="${route} view">
                ${content}
            </section>
        `;
        
        // SPA UI Updates
        GlobalState.setState({ ui: { currentRoute: route } });
        
        // Notify screen readers
        routeAnnouncer.textContent = `Navigated to ${route.replace('-', ' ')} view`;
        
        root.style.opacity = 1;
        root.setAttribute('aria-busy', 'false');
        
        // Active states
        navItems.forEach(btn => {
            if(btn.dataset.route === route) {
                btn.classList.add('active');
                btn.setAttribute('aria-current', 'page');
            } else {
                btn.classList.remove('active');
                btn.removeAttribute('aria-current');
            }
        });
    }, 200); 
};

// Listen to Global State events if needed globally
GlobalState.subscribe((state) => {
    console.log(`[SPA Core] Router State Mutated: ${state.ui.currentRoute}`);
});

// Event Binding
navItems.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const route = e.target.dataset.route;
        renderView(route);
    });
});

// Formal App Initialization
document.addEventListener('DOMContentLoaded', () => {
    root.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
    renderView(GlobalState.ui.currentRoute);
});

