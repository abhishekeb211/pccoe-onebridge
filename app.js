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
        highContrastMode: false,
        largeFontMode: false
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
        <h2>Welcome back, ${GlobalState.user.name}</h2>
        <p>Here is your daily OneBridge snapshot for ${GlobalState.user.branch}.</p>
    </div>
    <div class="dashboard-grid">
        <!-- Snapshot 1: Active Tickets -->
        <div class="glass-card">
            <div class="card-title">
                <span class="card-icon">🎫</span>
                <h3>Active Tickets</h3>
            </div>
            <p>You have <strong>1</strong> active administrative request.</p>
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>WiFi Access Drop</span>
                    <span class="badge pending">Pending</span>
                </div>
                <small style="color: var(--text-secondary);">Routed to IT Department</small>
            </div>
            <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('support')">View All Tickets</button>
        </div>

        <!-- Snapshot 2: AI Matched Opportunities -->
        <div class="glass-card" style="border-top: 4px solid var(--secondary);">
            <div class="card-title">
                <span class="card-icon">✨</span>
                <h3>New Opportunities</h3>
            </div>
            <p>Gemini AI matched <strong>2</strong> scholarships to your profile.</p>
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>MahaDBT Maintenance</span>
                    <span class="badge approved">98% Match</span>
                </div>
                <small style="color: var(--text-secondary);">Deadline: Oct 15</small>
            </div>
            <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('opportunities')">Review Matches</button>
        </div>

        <!-- Snapshot 3: Facility Bookings -->
        <div class="glass-card" style="border-top: 4px solid var(--primary-light);">
            <div class="card-title">
                <span class="card-icon">🏢</span>
                <h3>Facility Access</h3>
            </div>
            <p>Your upcoming reservations.</p>
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Library Study Room 4</span>
                    <span class="badge ${GlobalState.user.needsEOC ? 'urgent' : 'approved'}">
                        ${GlobalState.user.needsEOC ? 'Priority Assigned' : 'Confirmed'}
                    </span>
                </div>
                <small style="color: var(--text-secondary);">Today, 2:00 PM - 4:00 PM</small>
            </div>
        </div>
        
        ${GlobalState.user.needsEOC ? `
        <!-- Priority EOC Alert -->
        <div class="glass-card" style="border-top: 4px solid var(--eoc-brand);">
            <div class="card-title">
                <span class="card-icon">♿</span>
                <h3>EOC Quick Actions</h3>
            </div>
            <p>The main library elevator is currently functioning.</p>
            <button class="btn-primary" style="margin-top: 1.5rem; width: 100%; background: linear-gradient(135deg, var(--eoc-brand), var(--eoc-brand-light));" onclick="renderView('eoc')">Open EOC Portal</button>
        </div>
        ` : ''}
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
            case 'eoc': 
                // RBAC Protection on front end
                if(GlobalState.user.roles.includes("eoc_admin") || GlobalState.user.needsEOC) {
                     content = generateEoc(); 
                } else {
                     content = `<h2>Access Denied</h2><p>You do not have EOC Portal permissions.</p>`;
                }
                break;
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
        
        // Active states & RBAC Nav Cleanup
        navItems.forEach(btn => {
            // Hide specific nav items based on explicit roles
            if (btn.dataset.route === 'eoc' && !GlobalState.user.roles.includes("eoc_admin") && !GlobalState.user.needsEOC) {
                btn.style.display = 'none';
            } else {
                btn.style.display = 'block';
            }

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

// --- Phase 8: Accessibility Handlers ---
const accFab = document.querySelector('.accessibility-fab');

// Sync global state to body CSS
GlobalState.subscribe((state) => {
    if (state.ui.highContrastMode) {
        document.body.classList.add('high-contrast');
    } else {
        document.body.classList.remove('high-contrast');
    }

    if (state.ui.largeFontMode) {
        document.body.classList.add('large-font');
    } else {
        document.body.classList.remove('large-font');
    }
});

// Toggle via FAB click
if (accFab) {
    accFab.addEventListener('click', () => {
        const isVip = !GlobalState.ui.highContrastMode;
        GlobalState.setState({ ui: { highContrastMode: isVip, largeFontMode: isVip } });
        // Announce change
        routeAnnouncer.textContent = `Accessibility mode ${isVip ? 'enabled' : 'disabled'}`;
    });
}

// Global Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + H for high contrast
    if (e.altKey && e.key.toLowerCase() === 'h') {
        const toggle = !GlobalState.ui.highContrastMode;
        GlobalState.setState({ ui: { highContrastMode: toggle } });
        routeAnnouncer.textContent = `High contrast mode ${toggle ? 'enabled' : 'disabled'}`;
    }
    // Alt + F for focal font sizing
    if (e.altKey && e.key.toLowerCase() === 'f') {
        const toggle = !GlobalState.ui.largeFontMode;
        GlobalState.setState({ ui: { largeFontMode: toggle } });
        routeAnnouncer.textContent = `Large font mode ${toggle ? 'enabled' : 'disabled'}`;
    }
});

// Formal App Initialization
document.addEventListener('DOMContentLoaded', () => {
    root.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
    renderView(GlobalState.ui.currentRoute);
});

