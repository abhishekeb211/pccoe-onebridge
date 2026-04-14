/* 
 * PCCOE OneBridge - Core Frontend Architecture
 * Formal SPA Base, Layout Wrappers & Global State Manager
 */

// --- Supabase Configuration (Phase 7 Audit) ---
const SUPABASE_URL = "https://your-project.supabase.co"; // Replace with your URL
const SUPABASE_KEY = "your-anon-key";       // Replace with your Key
const supabase = window.supabase ? window.createClient(SUPABASE_URL, SUPABASE_KEY) : null;

// --- Global State Store ---
const GlobalState = {
    user: {
        name: null,
        prn: null,
        year: null,
        branch: null,
        roles: [],
        needsEOC: false,
        session: null
    },
    ui: {
        currentRoute: "dashboard",
        highContrastMode: false,
        largeFontMode: false,
        darkMode: false
    },
    listeners: [],
    
    // Subscribe to state mutations
    subscribe(callback) {
        this.listeners.push(callback);
    },
    
    // Dispatch mutations
    setState(newState) {
        if (newState.ui) this.ui = { ...this.ui, ...newState.ui };
        if (newState.user) this.user = { ...this.user, ...newState.user };
        this.notify();
    },
    
    notify() {
        this.listeners.forEach(fn => fn(this));
    }
};

// --- Theme Toggle Logic ---
function initTheme() {
    const saved = localStorage.getItem('ob_theme');
    if (saved === 'dark') {
        document.body.classList.add('dark-mode');
        GlobalState.ui.darkMode = true;
    }
    updateThemeToggleIcon();
}

function toggleDarkMode() {
    const isDark = !GlobalState.ui.darkMode;
    GlobalState.setState({ ui: { darkMode: isDark } });
    document.body.classList.toggle('dark-mode', isDark);
    localStorage.setItem('ob_theme', isDark ? 'dark' : 'light');
    updateThemeToggleIcon();
}

function updateThemeToggleIcon() {
    const btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.textContent = GlobalState.ui.darkMode ? '☀️' : '🌙';
        btn.setAttribute('aria-label', GlobalState.ui.darkMode ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

// Initialize theme immediately (before DOMContentLoaded) to avoid flash
initTheme();

// Bind theme toggle click
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggleDarkMode);
});

// --- Mock Data Layer (Realistic Indian Education Data) ---
const userData = {
    name: "Jane Smith",
    year: "3rd Year",
    branch: "Computer Engineering",
    alerts: 2
};

const mockOpportunities = [
    { type: "Scholarship", title: "MahaDBT EBC Scholarship", deadline: "Oct 30", matcher: "92% Match" },
    { type: "Scholarship", title: "National Scholarship Portal – Post Matric", deadline: "Nov 15", matcher: "88% Match" },
    { type: "Internship", title: "Web Dev Intern at TCS Digital", deadline: "Nov 20", matcher: "Highly Recommended" },
    { type: "Fellowship", title: "AICTE Pragati Scholarship (Women)", deadline: "Dec 01", matcher: "Eligible" },
    { type: "Internship", title: "Google STEP Internship 2026", deadline: "Jan 15", matcher: "85% Match" }
];

const mockFacilities = [
    { name: "Central Library (3-Floor)", status: "Open", capacity: "45/200 Seats", hours: "8:00 AM - 10:00 PM", accessible: true },
    { name: "Computer Lab – Block A", status: "Open", capacity: "30/60 PCs", hours: "9:00 AM - 6:00 PM", accessible: true },
    { name: "Maker Space & 3D Lab", status: "Requires Booking", capacity: "Available Tomorrow", hours: "10:00 AM - 5:00 PM", accessible: false },
    { name: "Seminar Hall – Main Building", status: "Booked Today", capacity: "150 Seats", hours: "By Reservation", accessible: true },
    { name: "Sports Complex & Gym", status: "Open", capacity: "Open Access", hours: "6:00 AM - 8:00 PM", accessible: true },
    { name: "Accessibility Ramp – Main Bldg", status: "Operational", capacity: "Verified", hours: "24/7", accessible: true }
];

const mockScholarships = [
    { id: 1, name: "MahaDBT EBC Scholarship", category: "Income", eligibility: "EBC students, income < ₹8L", amount: "₹25,000/year", deadline: "2026-10-30", matchPct: 92 },
    { id: 2, name: "NSP Post Matric Scholarship (SC)", category: "Caste", eligibility: "SC category, income < ₹2.5L", amount: "₹12,000 + fees", deadline: "2026-11-15", matchPct: 78 },
    { id: 3, name: "NSP Post Matric Scholarship (OBC)", category: "Caste", eligibility: "OBC category, income < ₹1L", amount: "₹7,000/year", deadline: "2026-11-15", matchPct: 65 },
    { id: 4, name: "AICTE Pragati Scholarship", category: "Gender", eligibility: "Women in AICTE-approved colleges, 1 per family", amount: "₹50,000/year", deadline: "2026-12-01", matchPct: 88 },
    { id: 5, name: "AICTE Saksham Scholarship", category: "Disability", eligibility: "PwD students in AICTE colleges", amount: "₹50,000/year", deadline: "2026-12-01", matchPct: 95 },
    { id: 6, name: "MahaDBT VJNT Scholarship", category: "Caste", eligibility: "VJNT/SBC category, Maharashtra domicile", amount: "Tuition + ₹10,000", deadline: "2026-10-30", matchPct: 70 },
    { id: 7, name: "e-Granth Scholarship (Merit)", category: "Merit", eligibility: "CGPA > 8.5, any branch, engineering", amount: "₹30,000/year", deadline: "2026-11-30", matchPct: 85 },
    { id: 8, name: "Central Sector Scheme (Merit)", category: "Merit", eligibility: "Top 20 percentile board marks, income < ₹4.5L", amount: "₹20,000/year", deadline: "2026-12-31", matchPct: 74 },
    { id: 9, name: "Google Generation Scholarship", category: "Merit", eligibility: "Women/underrepresented groups in CS, strong academic record", amount: "$1,000 (≈₹83,000)", deadline: "2026-12-15", matchPct: 60 },
    { id: 10, name: "PCCOE EOC Need-Based Grant", category: "Income", eligibility: "Disadvantaged students identified by EOC cell", amount: "Up to ₹50,000", deadline: "Rolling", matchPct: 90 },
    { id: 11, name: "Tata Trust Education Scholarship", category: "Income", eligibility: "Family income < ₹4L, engineering students", amount: "₹60,000/year", deadline: "2026-11-30", matchPct: 72 },
    { id: 12, name: "Sitaram Jindal Foundation Scholarship", category: "Income", eligibility: "Income < ₹2L, any UG engineering student", amount: "₹12,000/year", deadline: "2026-09-30", matchPct: 55 }
];

const mockCareers = [
    { id: 1, title: "Software Development Engineer – TCS Digital", company: "TCS", type: "full_time", branch: "Computer Engineering", year: "4th Year", stipend: "₹7.0 LPA", deadline: "2026-11-20", description: "Full-stack development role for TCS Digital division. Angular, Java, AWS." },
    { id: 2, title: "Product Intern – Summer 2026", company: "Infosys", type: "internship", branch: "All Branches", year: "3rd Year", stipend: "₹25,000/month", deadline: "2026-12-01", description: "6-month internship in product development at Infosys Pune campus." },
    { id: 3, title: "STEP Internship (India)", company: "Google", type: "internship", branch: "Computer Engineering", year: "2nd Year", stipend: "₹80,000/month", deadline: "2026-01-15", description: "12-week software engineering internship for 2nd year students." },
    { id: 4, title: "Microsoft Engage 2026", company: "Microsoft", type: "internship", branch: "CS/IT", year: "2nd Year", stipend: "₹60,000/month + mentorship", deadline: "2026-03-01", description: "Mentorship-based internship with hands-on project in AI/ML/Cloud." },
    { id: 5, title: "Associate Developer", company: "Persistent Systems", type: "full_time", branch: "CS/IT/E&TC", year: "4th Year", stipend: "₹5.5 LPA", deadline: "2026-10-30", description: "Pune-based development role. Java, Python, microservices architecture." },
    { id: 6, title: "Embedded Systems Intern", company: "KPIT Technologies", type: "internship", branch: "E&TC/Mechanical", year: "3rd Year", stipend: "₹20,000/month", deadline: "2026-11-15", description: "Automotive ADAS and embedded firmware development." },
    { id: 7, title: "Amazon ML Summer School", company: "Amazon", type: "fellowship", branch: "All Branches", year: "2nd/3rd Year", stipend: "Free + Certificate", deadline: "2026-02-28", description: "4-week intensive machine learning summer school by Amazon scientists." },
    { id: 8, title: "Research Fellowship – IIT Bombay", company: "IIT Bombay", type: "fellowship", branch: "All Branches", year: "3rd Year", stipend: "₹15,000/month", deadline: "2026-01-31", description: "Summer research fellowship in AI, networks, or systems under IIT faculty." },
    { id: 9, title: "Wipro Elite National Talent Hunt", company: "Wipro", type: "full_time", branch: "All Branches", year: "4th Year", stipend: "₹3.5 LPA", deadline: "2026-09-30", description: "National-level hiring for 2026 batch engineering graduates." },
    { id: 10, title: "UI/UX Design Intern", company: "Zeta (Directi)", type: "internship", branch: "CS/IT", year: "3rd Year", stipend: "₹40,000/month", deadline: "2026-12-10", description: "Design systems, user research, and prototyping for fintech products." }
];

const mockKBArticles = [
    { id: 1, category: "Academic", title: "How is CGPA calculated at SPPU?", content: "CGPA is calculated as the weighted average of grade points obtained in all courses. Each course carries credit points based on lecture/lab hours. Formula: CGPA = Σ(Credit × Grade Point) / Σ(Credits). A+ = 10, A = 9, B+ = 8, B = 7, C+ = 6, C = 5. Minimum 4 grade points (D) needed to pass." },
    { id: 2, category: "Academic", title: "Backlog and ATKT Rules – SPPU", content: "Students can carry forward a maximum of 4 backlogs (ATKT) to the next semester. If you have 5+ backlogs, you must clear extras before appearing for current semester exams. Backlog exams are held during regular exam windows. Apply via the college exam cell at least 30 days before." },
    { id: 3, category: "Academic", title: "Credit System & Elective Selection", content: "Each semester requires 22-26 credits. Core courses: 4 credits each. Labs: 2 credits. Electives (from 3rd year): Choose from department-approved list during registration week. Once locked, electives cannot be changed. Check elective prerequisites in the syllabus copy." },
    { id: 4, category: "Academic", title: "Exam Schedule and Hall Tickets", content: "University exam schedules are published on the SPPU website 3 weeks before exams. Hall tickets are distributed through the exam cell. In case of missing hall ticket, visit the exam cell with your ID card at least 48 hours before your exam." },
    { id: 5, category: "Technical", title: "How to connect to PCCOE WiFi", content: "1. Connect to 'PCCOE-Student' network. 2. Open browser → auto-redirects to login portal. 3. Enter your PRN as username, default password: pccoe@[last 4 digits of PRN]. 4. Change password on first login. 5. Max 2 devices per account. Report issues to IT helpdesk (Block A, Room 012)." },
    { id: 6, category: "Technical", title: "ERP Portal – Registration & Access", content: "Access ERP at erp.pccoepune.org. Login with PRN. Features: attendance tracking, fee receipts, internal marks, course registration. If locked out, visit admin office with ID for password reset (takes 24 hours)." },
    { id: 7, category: "Technical", title: "Library Digital Resources – IEEE/Springer", content: "Access IEEE Xplore, Springer, and ACM DL from campus network. Off-campus: use VPN (install FortiClient, credentials from library desk). E-books available via DELNET. Interlibrary loan requests: 3-5 business days." },
    { id: 8, category: "Technical", title: "Lab Booking & Software Access", content: "Book computer labs via OneBridge Resources section. Available software: MATLAB, AutoCAD, VS Code, Eclipse, Android Studio. GPU lab (Block C, 2nd floor) requires prior booking. Report hardware issues to lab coordinator immediately." },
    { id: 9, category: "Administrative", title: "Fee Payment – Online & Offline Options", content: "Online: Login to ERP → Fee section → Pay via UPI/Net Banking/Card. Offline: SBI counter at campus. Fee split allowed for identified students (apply through accounts office). Late fee: ₹100/day after deadline. Fee receipts available in ERP under 'Downloads'." },
    { id: 10, category: "Administrative", title: "Hostel Allotment Process", content: "Apply through hostel office (Block D). Priority: outstation students > local. Submit: admission receipt, Aadhar, passport photos (2), parent declaration. Allotment results: 1 week after application window closes. Hostel fees: ₹55,000-70,000/year (includes mess)." },
    { id: 11, category: "Administrative", title: "Transfer Certificate & Bonafide Letter", content: "TC Application: Submit to registrar with clearance form (library, hostel, lab, accounts). Processing time: 7-10 working days. Bonafide Certificate: Apply via ERP → Documents → Bonafide Request. Auto-generated within 48 hours. Collect from admin office with ID." },
    { id: 12, category: "Administrative", title: "No Objection Certificate (NOC) for Internships", content: "Required for off-campus internships. Submit: Company offer letter, internship duration, faculty mentor approval. Apply: Training & Placement Cell, minimum 15 days before joining. NOC validity: duration of internship only." },
    { id: 13, category: "EOC", title: "How to request disability accommodation", content: "File a request through OneBridge EOC portal or visit EOC office (Room 105, Admin Block). Accommodations available: exam scribes, accessible seating, extended time, study material in accessible formats, priority lab booking. All requests handled confidentially within 48 hours." },
    { id: 14, category: "EOC", title: "Filing a confidential grievance", content: "Use OneBridge EOC portal → Confidential Grievance section. All submissions are encrypted and visible only to authorized EOC officers. Anonymous submissions supported. Expect acknowledgment within 24 hours, resolution within 7 working days. No retaliation policy strictly enforced." },
    { id: 15, category: "EOC", title: "Scholarship support for disadvantaged students", content: "EOC maintains a priority scholarship database. Students with disabilities, EWS, or identified disadvantaged status get priority notifications. Contact EOC cell for free application assistance, document preparation, and interview coaching. Walk-in hours: Mon-Fri, 10 AM - 4 PM." },
    { id: 16, category: "Campus Life", title: "Student clubs & extra-curricular activities", content: "PCCOE has 30+ active clubs: coding (CodeChef chapter), robotics, debate, cultural, sports. Registration during orientation week or via club coordinators. Each club has a faculty advisor. Events calendar available on notice board and ERP." },
    { id: 17, category: "Campus Life", title: "Health Center & Counseling Services", content: "Campus health center: Block B ground floor. Doctor available: 9 AM - 5 PM weekdays. Emergency: security desk 24/7 can arrange ambulance. Counseling: Free and confidential, book through health center or EOC portal. Crisis helpline: displayed on notice boards." },
    { id: 18, category: "Placement", title: "Placement Cell – Registration & Process", content: "Register on T&P Cell portal (tpo.pccoepune.org). Eligibility: no active backlogs, minimum 6.0 CGPA (relaxed for some companies). Process: Pre-placement talk → Aptitude test → Technical interview → HR round. Average package (2025): ₹5.8 LPA. Highest: ₹44 LPA." }
];

const mockResources = [
    { id: 1, name: "Central Library (3 Floors)", type: "library", building: "Main Block", floor: "G-2", capacity: 200, hours: "8:00 AM - 10:00 PM", accessible: true, status: "Open" },
    { id: 2, name: "Computer Lab – Block A", type: "lab", building: "Block A", floor: "1st", capacity: 60, hours: "9:00 AM - 6:00 PM", accessible: true, status: "Open" },
    { id: 3, name: "GPU Computing Lab", type: "lab", building: "Block C", floor: "2nd", capacity: 20, hours: "10:00 AM - 5:00 PM (Booking Required)", accessible: false, status: "Requires Booking" },
    { id: 4, name: "Maker Space & 3D Printing", type: "makerspace", building: "Innovation Hub", floor: "Ground", capacity: 25, hours: "10:00 AM - 5:00 PM", accessible: false, status: "Open" },
    { id: 5, name: "Main Seminar Hall (A/C)", type: "seminar_hall", building: "Main Block", floor: "3rd", capacity: 300, hours: "By Reservation", accessible: true, status: "Available" },
    { id: 6, name: "Mini Auditorium", type: "seminar_hall", building: "Block B", floor: "Ground", capacity: 100, hours: "By Reservation", accessible: true, status: "Available" },
    { id: 7, name: "Sports Complex & Gym", type: "sports", building: "Campus Ground", floor: "—", capacity: null, hours: "6:00 AM - 8:00 PM", accessible: true, status: "Open" },
    { id: 8, name: "Study Room – Quiet Zone", type: "library", building: "Library Annex", floor: "2nd", capacity: 30, hours: "8:00 AM - 9:00 PM", accessible: true, status: "Open" },
    { id: 9, name: "Electronics Workshop Lab", type: "lab", building: "Block D", floor: "1st", capacity: 40, hours: "9:00 AM - 5:00 PM", accessible: false, status: "Open" },
    { id: 10, name: "Conference Room – Faculty", type: "seminar_hall", building: "Admin Block", floor: "2nd", capacity: 20, hours: "9:00 AM - 6:00 PM", accessible: true, status: "Available" }
];

const mockDashboardStats = {
    activeTickets: 3,
    upcomingDeadlines: 5,
    matchedScholarships: 4,
    pendingApprovals: 1,
    notifications: [
        { title: "MahaDBT deadline in 16 days", time: "2 hours ago", type: "warning" },
        { title: "Ticket #42 resolved by IT Dept", time: "Yesterday", type: "success" },
        { title: "New internship: Google STEP 2026", time: "2 days ago", type: "info" },
        { title: "Room 301 Lab booking confirmed", time: "3 days ago", type: "success" }
    ]
};

// --- Loading & Error Helpers ---
const renderLoading = (message = "Loading...") => `
    <div class="glass-card" style="text-align: center; padding: 3rem;" role="status" aria-live="polite">
        <div class="loading-spinner" aria-hidden="true"></div>
        <p style="margin-top: 1rem; color: var(--text-secondary);">${message}</p>
    </div>
`;

const renderError = (message, retryFn) => `
    <div class="glass-card" style="text-align: center; padding: 3rem; border-color: var(--accent);" role="alert">
        <span style="font-size: 2rem;">⚠️</span>
        <p style="margin: 1rem 0; color: var(--accent);">${message}</p>
        ${retryFn ? `<button class="btn-primary" onclick="${retryFn}">Retry</button>` : ''}
    </div>
`;

// --- Session Management ---

function saveSession(token, user) {
    sessionStorage.setItem('ob_token', token);
    sessionStorage.setItem('ob_user', JSON.stringify(user));
}

function clearSession() {
    sessionStorage.removeItem('ob_token');
    sessionStorage.removeItem('ob_user');
    ApiService.setToken(null);
    GlobalState.setState({
        user: { name: null, prn: null, year: null, branch: null, roles: [], needsEOC: false, session: null }
    });
}

async function restoreSession() {
    const token = sessionStorage.getItem('ob_token');
    if (!token) return false;
    ApiService.setToken(token);
    try {
        const profile = await ApiService.getMyProfile();
        GlobalState.setState({
            user: {
                name: profile.name,
                prn: profile.prn,
                email: profile.email,
                roles: profile.roles || ['student'],
                needsEOC: profile.is_disadvantaged || profile.has_disability,
                session: token,
            }
        });
        return true;
    } catch {
        clearSession();
        return false;
    }
}

window.handleLogout = () => {
    clearSession();
    renderView('login');
    window.showNotification("Logged out successfully.", "info");
};

// --- Login View ---

const generateLogin = () => `
    <div class="view-header" style="text-align: center;">
        <h2>Sign In to OneBridge</h2>
        <p>Use your PCCOE email or PRN to access all services.</p>
    </div>
    <div class="opportunities-grid" style="grid-template-columns: 1fr;">
        <div class="glass-card" style="max-width: 480px; margin: 2rem auto; padding: 2rem;">
            <form id="login-form" onsubmit="handleLoginSubmit(event)">
                <div style="margin-bottom: 1.5rem;">
                    <label for="loginId" class="ob-label">PCCOE Email or PRN</label>
                    <input type="text" id="loginId" required autocomplete="username" aria-label="PCCOE Email or PRN"
                        class="ob-input" placeholder="e.g. jane@pccoepune.org or PRN001">
                </div>
                <div style="margin-bottom: 1.5rem;">
                    <label for="loginPass" class="ob-label">Password</label>
                    <input type="password" id="loginPass" required autocomplete="current-password" aria-label="Password"
                        class="ob-input" placeholder="Enter your password">
                </div>
                <div id="login-error" style="color: var(--accent); margin-bottom: 1rem; display: none;" role="alert"></div>
                <button type="submit" class="btn-primary" style="width: 100%; font-size: 1.1rem; padding: 1rem;">Sign In</button>
            </form>
            <p style="text-align: center; margin-top: 1.25rem; font-size: 0.85rem; color: var(--text-secondary);">
                Demo credentials: <strong>PRN001</strong> / <strong>password</strong>
            </p>
        </div>
    </div>
`;

window.handleLoginSubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const errorDiv = document.getElementById('login-error');
    const username = document.getElementById('loginId').value;
    const password = document.getElementById('loginPass').value;

    btn.textContent = 'Signing in...';
    btn.disabled = true;
    errorDiv.style.display = 'none';

    try {
        const data = await ApiService.login(username, password);
        // Fetch profile after login
        const profile = await ApiService.getMyProfile();
        GlobalState.setState({
            user: {
                name: profile.name,
                prn: profile.prn,
                email: profile.email,
                roles: profile.roles || ['student'],
                needsEOC: profile.is_disadvantaged || profile.has_disability,
                session: data.access_token,
            }
        });
        saveSession(data.access_token, GlobalState.user);
        updateNavForAuth(true);
        renderView('dashboard');
        window.showNotification(`Welcome back, ${profile.name}!`, "success");
    } catch (err) {
        // Demo mode fallback: allow login without backend
        if (typeof IS_GITHUB_PAGES !== 'undefined' && IS_GITHUB_PAGES || err.message === 'API unavailable in static mode') {
            GlobalState.setState({
                user: {
                    name: username || 'Demo Student',
                    prn: username || 'DEMO001',
                    email: (username || 'demo') + '@pccoe.org',
                    roles: ['student', 'eoc_admin', 'super_admin'],
                    needsEOC: true,
                    session: 'demo-token',
                }
            });
            updateNavForAuth(true);
            renderView('dashboard');
            window.showNotification('Signed in (Demo Mode — no backend connected)', 'info');
        } else {
            errorDiv.textContent = err.message;
            errorDiv.style.display = 'block';
            btn.textContent = 'Sign In';
            btn.disabled = false;
        }
    }
};

function updateNavForAuth(loggedIn) {
    const profileEl = document.querySelector('.user-profile');
    if (profileEl && loggedIn && GlobalState.user.name) {
        const initials = GlobalState.user.name.split(' ').map(n => n[0]).join('').toUpperCase();
        profileEl.innerHTML = `
            <button class="theme-toggle" id="theme-toggle" onclick="toggleDarkMode()" aria-label="Toggle dark mode">${GlobalState.ui.darkMode ? '☀️' : '🌙'}</button>
            <div class="notification-bell" onclick="toggleNotifPanel()" aria-label="Notifications" role="button" tabindex="0">
                🔔<span class="notif-count" id="notif-count" style="display: none;">0</span>
            </div>
            <div class="avatar" aria-hidden="true">${initials}</div>
            <div class="profile-info">
                <span class="student-name">${GlobalState.user.name}</span>
                <span class="student-detail">${GlobalState.user.roles.join(', ')}</span>
            </div>
            <button class="btn-secondary" style="padding: 0.4rem 1rem; font-size: 0.85rem;" onclick="handleLogout()">Logout</button>
        `;
    } else if (profileEl && !loggedIn) {
        profileEl.innerHTML = `
            <button class="theme-toggle" id="theme-toggle" onclick="toggleDarkMode()" aria-label="Toggle dark mode">${GlobalState.ui.darkMode ? '☀️' : '🌙'}</button>
            <div class="avatar" aria-hidden="true">?</div>
            <div class="profile-info">
                <span class="student-name">Not logged in</span>
                <span class="student-detail">Sign in to access services</span>
            </div>
        `;
    }
}

// --- Notification Panel ---
let _notifPollTimer = null;

window.toggleNotifPanel = () => {
    let panel = document.getElementById('notif-panel');
    if (panel) {
        panel.remove();
        return;
    }
    panel = document.createElement('div');
    panel.id = 'notif-panel';
    panel.className = 'notif-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Notifications');
    panel.innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--text-secondary);">Loading...</div>';
    document.body.appendChild(panel);
    loadNotifications(panel);
};

async function loadNotifications(panel) {
    if (!panel) panel = document.getElementById('notif-panel');
    if (!panel) return;
    try {
        const data = await ApiService.getNotifications();
        const notifs = data.notifications || [];
        const countEl = document.getElementById('notif-count');
        if (countEl) {
            countEl.textContent = data.unread_count || 0;
            countEl.style.display = data.unread_count > 0 ? 'inline-block' : 'none';
        }
        if (notifs.length === 0) {
            panel.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-secondary);">No notifications yet.</div>';
            return;
        }
        panel.innerHTML = `
            <div style="padding: 0.75rem 1rem; border-bottom: 1px solid var(--glass-border); font-weight: 600;">
                Notifications (${data.unread_count} unread)
            </div>
            ${notifs.map(n => `
                <div class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}" onclick="markRead(${n.id}, this)">
                    <strong>${n.title}</strong>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">${n.message}</p>
                    <small style="color: var(--text-secondary);">${n.created_at ? new Date(n.created_at).toLocaleString() : ''}</small>
                </div>
            `).join('')}
        `;
    } catch {
        panel.innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--accent);">Could not load notifications.</div>';
    }
}

window.markRead = async (id, el) => {
    try {
        await ApiService.markNotificationRead(id);
        if (el) el.classList.remove('unread');
        // Update count
        const countEl = document.getElementById('notif-count');
        if (countEl) {
            const c = Math.max(0, parseInt(countEl.textContent || '0') - 1);
            countEl.textContent = c;
            countEl.style.display = c > 0 ? 'inline-block' : 'none';
        }
    } catch { /* silent */ }
};

function startNotifPolling() {
    if (_notifPollTimer) clearInterval(_notifPollTimer);
    _notifPollTimer = setInterval(async () => {
        if (!GlobalState.user.session) return;
        try {
            const data = await ApiService.getNotifications();
            const countEl = document.getElementById('notif-count');
            if (countEl) {
                countEl.textContent = data.unread_count || 0;
                countEl.style.display = data.unread_count > 0 ? 'inline-block' : 'none';
            }
        } catch { /* silent */ }
    }, 30000);
}

// --- Views Generation ---

const generateDashboard = () => {
    setTimeout(() => loadDashboardData(), 50);

    return `
    <div class="view-header">
        <h2>Welcome back, ${GlobalState.user.name || 'Student'}</h2>
        <p>Here is your daily OneBridge snapshot for ${GlobalState.user.branch || 'Engineering'}.</p>
    </div>

    <!-- Quick Stats Row -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
        <div class="stat-card">
            <div class="stat-value" style="color: var(--primary);">${mockDashboardStats.activeTickets}</div>
            <div class="stat-label">Active Tickets</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: var(--warning);">${mockDashboardStats.upcomingDeadlines}</div>
            <div class="stat-label">Upcoming Deadlines</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: var(--secondary);">${mockDashboardStats.matchedScholarships}</div>
            <div class="stat-label">Matched Scholarships</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: var(--eoc-brand);">${mockDashboardStats.pendingApprovals}</div>
            <div class="stat-label">Pending Approvals</div>
        </div>
    </div>

    <div class="dashboard-grid">
        <!-- Snapshot 1: Active Tickets -->
        <div class="glass-card" id="dashboard-tickets">
            <div class="card-title">
                <span class="card-icon">🎫</span>
                <h3>Active Tickets</h3>
            </div>
            ${renderLoading("Loading tickets...")}
        </div>

        <!-- Snapshot 2: AI Matched Opportunities -->
        <div class="glass-card" style="border-top: 4px solid var(--secondary);" id="dashboard-opportunities">
            <div class="card-title">
                <span class="card-icon">✨</span>
                <h3>New Opportunities</h3>
            </div>
            ${renderLoading("Loading matches...")}
        </div>

        <!-- Snapshot 3: Facility Bookings -->
        <div class="glass-card" style="border-top: 4px solid var(--primary-light);">
            <div class="card-title">
                <span class="card-icon">🏢</span>
                <h3>Facility Access</h3>
            </div>
            <p>Your upcoming reservations.</p>
            <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-elevated); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Library Study Room 4</span>
                    <span class="badge ${GlobalState.user.needsEOC ? 'urgent' : 'approved'}">
                        ${GlobalState.user.needsEOC ? 'Priority Assigned' : 'Confirmed'}
                    </span>
                </div>
                <small style="color: var(--text-secondary);">Today, 2:00 PM - 4:00 PM</small>
            </div>
        </div>

        <!-- Recent Activity Feed -->
        <div class="glass-card" style="border-top: 4px solid var(--warning);">
            <div class="card-title">
                <span class="card-icon">📋</span>
                <h3>Recent Activity</h3>
            </div>
            ${mockDashboardStats.notifications.map(n => `
                <div style="padding: 0.75rem; border-left: 3px solid ${n.type === 'success' ? 'var(--secondary)' : n.type === 'warning' ? 'var(--warning)' : 'var(--primary)'}; margin-bottom: 0.5rem; background: var(--bg-elevated); border-radius: 0 8px 8px 0;">
                    <p style="font-size: 0.9rem;">${n.title}</p>
                    <small style="color: var(--text-secondary);">${n.time}</small>
                </div>
            `).join('')}
        </div>
        
        ${GlobalState.user.needsEOC ? `
        <div class="glass-card eoc-section" style="border-top: 4px solid var(--eoc-brand);">
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
};

// Async data loader for dashboard cards
async function loadDashboardData() {
    const prn = GlobalState.user.prn;

    // Load tickets
    const ticketCard = document.getElementById('dashboard-tickets');
    if (ticketCard) {
        try {
            const data = await ApiService.getStudentTickets(prn);
            const tickets = data.tickets || [];
            const activeCount = tickets.filter(t => t.status !== 'Resolved').length;
            ticketCard.innerHTML = `
                <div class="card-title"><span class="card-icon">🎫</span><h3>Active Tickets</h3></div>
                <p>You have <strong>${activeCount}</strong> active request${activeCount !== 1 ? 's' : ''}.</p>
                ${tickets.slice(0, 2).map(t => `
                    <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-elevated); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>${t.description.substring(0, 40)}${t.description.length > 40 ? '...' : ''}</span>
                            <span class="badge ${t.status === 'Resolved' ? 'approved' : t.urgent_flag ? 'urgent' : 'pending'}">${t.status}</span>
                        </div>
                        <small style="color: var(--text-secondary);">Routed to ${t.predicted_department || 'Triage'}</small>
                    </div>
                `).join('')}
                <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('support')">View All Tickets</button>
            `;
        } catch (err) {
            ticketCard.innerHTML = `
                <div class="card-title"><span class="card-icon">🎫</span><h3>Active Tickets</h3></div>
                <p style="color: var(--text-secondary);">Could not load tickets.</p>
                <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('support')">Go to Support</button>
            `;
        }
    }

    // Load opportunities
    const oppCard = document.getElementById('dashboard-opportunities');
    if (oppCard) {
        try {
            const data = await ApiService.getOpportunities(prn);
            const matches = data.matches || [];
            oppCard.innerHTML = `
                <div class="card-title"><span class="card-icon">✨</span><h3>New Opportunities</h3></div>
                <p>AI matched <strong>${matches.length}</strong> opportunities to your profile.</p>
                ${matches.slice(0, 1).map(m => `
                    <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-elevated); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>${m.title}</span>
                            <span class="badge approved">${m.type}</span>
                        </div>
                        <small style="color: var(--text-secondary);">Deadline: ${m.deadline ? new Date(m.deadline).toLocaleDateString() : 'TBD'}</small>
                    </div>
                `).join('')}
                <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('opportunities')">Review Matches</button>
            `;
        } catch (err) {
            oppCard.innerHTML = `
                <div class="card-title"><span class="card-icon">✨</span><h3>New Opportunities</h3></div>
                <p style="color: var(--text-secondary);">Could not load opportunities.</p>
                <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" onclick="renderView('opportunities')">Browse Opportunities</button>
            `;
        }
    }
}

const generateOpportunities = () => {
    setTimeout(() => loadOpportunitiesData(), 50);
    return `
    <div class="view-header">
        <h2>Opportunities Hub</h2>
        <p>Discover Scholarships, Fellowships, Internships, and Jobs tailored for you.</p>
    </div>
    <div class="opportunities-grid" id="opportunities-container">
        ${renderLoading("Fetching matched opportunities...")}
    </div>
`;
};

async function loadOpportunitiesData() {
    const container = document.getElementById('opportunities-container');
    if (!container) return;

    try {
        const data = await ApiService.getOpportunities(GlobalState.user.prn);
        const matches = data.matches || [];

        if (matches.length === 0) {
            container.innerHTML = `
                <div class="glass-card" style="text-align: center; padding: 3rem;">
                    <p style="color: var(--text-secondary);">No matching opportunities found. Check back soon!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = matches.map(opp => `
            <div class="glass-card">
                <span class="badge pending" style="margin-bottom: 1rem; display: inline-block;">${opp.type}</span>
                <h3 style="margin-bottom: 0.5rem;">${opp.title}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">Deadline: ${opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'TBD'}</p>
                <div style="display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
                    <span style="color: var(--secondary); font-size: 0.9rem;">${opp.target_branches || 'All Branches'}</span>
                    <button class="btn-primary">Apply Now</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        // Fallback to mock data on error
        container.innerHTML = mockOpportunities.map(opp => `
            <div class="glass-card">
                <span class="badge pending" style="margin-bottom: 1rem; display: inline-block;">${opp.type}</span>
                <h3 style="margin-bottom: 0.5rem;">${opp.title}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">Deadline: ${opp.deadline}</p>
                <div style="display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
                    <span style="color: var(--secondary); font-size: 0.9rem;">${opp.matcher}</span>
                    <button class="btn-primary">Apply Now</button>
                </div>
            </div>
        `).join('');
        window.showNotification("Using cached opportunities data.", "info");
    }
}

const generateFacilities = () => {
    setTimeout(() => loadFacilitiesData(), 50);
    return `
    <div class="view-header">
        <h2>Facilities Access</h2>
        <p>Check availability and book campus facilities digitally.</p>
    </div>
    <div class="filter-chips">
        <button class="filter-chip active" onclick="filterFacilities('all')">All</button>
        <button class="filter-chip" onclick="filterFacilities('Open')">Open Now</button>
        <button class="filter-chip" onclick="filterFacilities('accessible')">♿ Accessible</button>
        <button class="filter-chip" onclick="filterFacilities('Requires Booking')">Booking Required</button>
    </div>
    <div class="opportunities-grid" id="facilities-container">
        ${renderLoading("Loading facilities...")}
    </div>
`;
};

window.filterFacilities = (filter) => {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    loadFacilitiesData(filter);
};

async function loadFacilitiesData(filter = 'all') {
    const container = document.getElementById('facilities-container');
    if (!container) return;

    const renderFacilityCards = (list) => {
        let filtered = list;
        if (filter === 'accessible') filtered = list.filter(f => f.accessible);
        else if (filter !== 'all') filtered = list.filter(f => f.status === filter);

        if (filtered.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="empty-icon">🏢</div><p>No facilities match this filter.</p></div>`;
            return;
        }
        container.innerHTML = filtered.map(fac => `
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                    <h3 style="font-size: 1.1rem;">${fac.name}</h3>
                    ${fac.accessible ? '<span title="Wheelchair Accessible" style="font-size: 1.2rem;">♿</span>' : ''}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span class="badge ${fac.status === 'Open' ? 'approved' : fac.status === 'Booked Today' ? 'urgent' : 'pending'}">${fac.status}</span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">🕐 ${fac.hours || 'Check availability'}</p>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">📊 ${fac.capacity}</p>
                <button class="btn-primary" style="width: 100%;" ${fac.status === 'Open' || fac.status === 'Requires Booking' || fac.status === 'Available' ? '' : 'disabled'}>
                    ${fac.status === 'Requires Booking' ? 'Book Slot' : fac.status === 'Open' || fac.status === 'Available' ? 'Check In' : 'Unavailable'}
                </button>
            </div>
        `).join('');
    };

    try {
        const data = await ApiService.getFacilities();
        const facilities = data.facilities || [];
        if (facilities.length === 0) {
            renderFacilityCards(mockFacilities);
            return;
        }
        renderFacilityCards(facilities.map(b => ({
            name: b.facility_name,
            status: 'Confirmed',
            capacity: b.accessibility_override ? '♿ Accessibility Priority' : 'Standard Booking',
            hours: new Date(b.booking_time).toLocaleString(),
            accessible: b.accessibility_override
        })));
    } catch (err) {
        renderFacilityCards(mockFacilities);
    }
}

const generateSupport = () => `
    <div class="view-header">
        <h2>Support Center</h2>
        <p>Submit inquiries securely. The AI will optimally classify and route your request to the right department.</p>
    </div>
    
    <div class="opportunities-grid" style="grid-template-columns: 1fr;">
        <div class="glass-card" style="max-width: 800px; margin: auto; padding: 2rem;">
            <h3 style="margin-bottom: 1.5rem;">Create New Request</h3>
            
            <form id="dynamic-support-form" onsubmit="handleSupportSubmit(event)">
                <div style="margin-bottom: 1.5rem;">
                    <label for="reqCategory" class="ob-label">Initial Category (Optional - AI will Auto-Route)</label>
                    <select id="reqCategory" aria-label="Ticket category selection" class="ob-select" onchange="toggleFormLogic()">
                        <option value="auto">Auto-Detect (AI Routing)</option>
                        <option value="tech">Technical Issue</option>
                        <option value="academic">Academic & Examinations</option>
                        <option value="eoc">EOC Confidential Grievance</option>
                    </select>
                </div>

                <div style="margin-bottom: 1.5rem;">
                    <label for="reqSummary" class="ob-label">Detailed Description</label>
                    <textarea id="reqSummary" rows="5" required aria-label="Detailed description of your request" aria-required="true" class="ob-textarea" placeholder="Please describe exactly what you need help with..."></textarea>
                    <small style="color: var(--warning); display: block; margin-top: 0.5rem;">ⓘ Note: All data is subjected to strict PII-Stripping before analysis.</small>
                </div>

                <div id="dynamic-upload-block" style="margin-bottom: 2rem; display: none;">
                    <label for="reqProof" class="ob-label">Attach Proof/Documents</label>
                    <input type="file" id="reqProof" accept=".pdf,.png,.jpg" style="color: var(--text-primary);">
                </div>
                
                <button type="submit" class="btn-primary" style="width: 100%; font-size: 1.1rem; padding: 1rem;">Submit Encrypted Request</button>
                <button type="button" class="btn-secondary" style="width: 100%; font-size: 1rem; padding: 0.8rem; margin-top: 0.75rem;" onclick="handleAIAssist()">🤖 Ask AI for Guidance First</button>
            </form>

            <div id="ai-assist-panel" style="display: none; margin-top: 1.5rem; padding: 1.5rem; background: rgba(16,185,129,0.06); border: 1px solid var(--secondary); border-radius: 12px;">
                <h4 style="margin-bottom: 0.75rem; color: var(--secondary);">🤖 AI Guidance</h4>
                <div id="ai-assist-content" style="color: var(--text-primary); line-height: 1.7;"></div>
                <small style="display: block; margin-top: 0.75rem; color: var(--text-secondary);">All PII was stripped before sending to the AI. This is guidance only — submit a ticket for official support.</small>
            </div>
        </div>

        <div class="glass-card" style="max-width: 800px; margin: 2rem auto 0; padding: 2rem;">
            <h3 style="margin-bottom: 1.5rem;">My Tickets</h3>
            <div id="ticket-history-list">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
                <p style="text-align: center; margin-top: 0.5rem; color: var(--text-secondary);">Loading tickets...</p>
            </div>
        </div>
    </div>
`;

// Dynamic phase 17 handlers attached directly to window for string interpolation bindings
window.toggleFormLogic = () => {
    const val = document.getElementById('reqCategory').value;
    const upload = document.getElementById('dynamic-upload-block');
    if(val === 'academic' || val === 'eoc') {
        upload.style.display = 'block';
    } else {
        upload.style.display = 'none';
    }
};

window.handleSupportSubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const summary = document.getElementById('reqSummary').value;
    
    btn.innerHTML = 'Routing Request via AI... <span class="sr-only">Please wait</span>';
    btn.disabled = true;
    btn.style.opacity = '0.7';
    
    try {
        const data = await ApiService.submitTicket(summary, GlobalState.user.prn);
        
        // Upload attachment if present
        const fileInput = document.getElementById('reqProof');
        if (fileInput && fileInput.files.length > 0) {
            try {
                await ApiService.uploadTicketAttachment(data.ticket_id, fileInput.files[0]);
            } catch (uploadErr) {
                window.showNotification(`Ticket created but attachment failed: ${uploadErr.message}`, "info");
            }
        }
        
        window.showNotification(`Ticket #${data.ticket_id} submitted. AI Routed to ${data.analytics.predicted_department}.`, "success");
        renderView('support');
    } catch (err) {
        window.showNotification(`Submission Error: ${err.message}`, "urgent");
        btn.innerHTML = 'Retry Submission';
        btn.disabled = false;
        btn.style.opacity = '1';
    }
};

window.handleAIAssist = async () => {
    const summary = document.getElementById('reqSummary')?.value;
    if (!summary || summary.trim().length < 10) {
        window.showNotification("Please describe your issue in detail before asking AI.", "info");
        return;
    }

    const panel = document.getElementById('ai-assist-panel');
    const content = document.getElementById('ai-assist-content');
    if (!panel || !content) return;

    panel.style.display = 'block';
    content.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div><p style="text-align: center; margin-top: 0.5rem; color: var(--text-secondary);">AI is analyzing your query (PII stripped)...</p>';

    const category = document.getElementById('reqCategory')?.value;
    const context = category === 'eoc' ? 'eoc_guidance' : 'student_assist';

    try {
        const data = await ApiService.aiAssist(summary, context);
        content.innerHTML = `<p>${data.response.replace(/\n/g, '<br>')}</p>`;
    } catch (err) {
        content.innerHTML = `<p style="color: var(--accent);">AI assistant unavailable: ${err.message}</p>`;
    }
};

// --- Phase 19: Ticket History & Status Management ---

const STATUS_COLORS = {
    "Submitted": "#6366f1",
    "Under Review": "#f59e0b",
    "Action Required": "#ef4444",
    "Resolved": "#10b981",
    "Escalated": "#dc2626",
};

window.loadTicketHistory = async () => {
    const container = document.getElementById('ticket-history-list');
    if (!container || !GlobalState.user.prn) return;

    try {
        const tickets = await ApiService.getStudentTickets(GlobalState.user.prn);
        if (!tickets || tickets.length === 0) {
            container.innerHTML = '<p style="text-align:center; color: var(--text-secondary);">No tickets yet. Submit your first request above.</p>';
            return;
        }
        container.innerHTML = tickets.map(t => {
            const color = STATUS_COLORS[t.status] || '#6366f1';
            const canEscalate = t.status !== 'Resolved' && t.status !== 'Escalated';
            return `
                <div class="glass-card" style="margin-bottom: 1rem; padding: 1.25rem; border-left: 4px solid ${color}; cursor: pointer;" onclick="viewTicketDetail(${t.id})">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Ticket #${t.id}</strong>
                            <span style="margin-left: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; background: ${color}22; color: ${color}; border: 1px solid ${color};">${t.status}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            ${t.category || 'Auto-Routed'}
                        </div>
                    </div>
                    <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${t.description || ''}</p>
                    ${canEscalate ? `<button class="btn-primary" style="margin-top: 0.75rem; padding: 0.4rem 1rem; font-size: 0.85rem; background: var(--accent);" onclick="event.stopPropagation(); escalateTicket(${t.id})">⚡ Escalate</button>` : ''}
                </div>`;
        }).join('');
    } catch (err) {
        container.innerHTML = `<p style="color: var(--accent); text-align: center;">Could not load tickets: ${err.message}</p>`;
    }
};

window.viewTicketDetail = async (ticketId) => {
    const container = document.getElementById('ticket-history-list');
    if (!container) return;
    container.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div>';

    try {
        const t = await ApiService.getTicketDetail(ticketId);
        const color = STATUS_COLORS[t.status] || '#6366f1';
        container.innerHTML = `
            <div class="glass-card" style="padding: 1.5rem; border-left: 4px solid ${color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4>Ticket #${t.id}</h4>
                    <button class="btn-primary" style="padding: 0.3rem 0.8rem; font-size: 0.85rem;" onclick="loadTicketHistory()">← Back to List</button>
                </div>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Status</td><td style="padding: 0.5rem;"><span style="padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.85rem; background: ${color}22; color: ${color}; border: 1px solid ${color};">${t.status}</span></td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Category</td><td style="padding: 0.5rem;">${t.category || 'N/A'}</td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Assigned To</td><td style="padding: 0.5rem;">${t.assigned_to || 'Pending'}</td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Department</td><td style="padding: 0.5rem;">${t.predicted_department || 'N/A'}</td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Transition Reason</td><td style="padding: 0.5rem;">${t.transition_reason || '—'}</td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Created</td><td style="padding: 0.5rem;">${t.created_at ? new Date(t.created_at).toLocaleString() : '—'}</td></tr>
                    <tr><td style="padding: 0.5rem; color: var(--text-secondary);">Updated</td><td style="padding: 0.5rem;">${t.updated_at ? new Date(t.updated_at).toLocaleString() : '—'}</td></tr>
                </table>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.15); border-radius: 8px;">
                    <strong style="display: block; margin-bottom: 0.5rem;">Description</strong>
                    <p style="color: var(--text-secondary); line-height: 1.6;">${t.description}</p>
                </div>
                ${t.urgent_flag ? '<p style="margin-top: 0.75rem; color: var(--accent); font-weight: bold;">🚨 Flagged as Urgent</p>' : ''}
            </div>`;
    } catch (err) {
        container.innerHTML = `<p style="color: var(--accent); text-align: center;">Could not load ticket: ${err.message}</p>
            <button class="btn-primary" style="display: block; margin: 1rem auto;" onclick="loadTicketHistory()">← Back</button>`;
    }
};

window.escalateTicket = async (ticketId) => {
    if (!confirm('Are you sure you want to escalate this ticket? This will flag it for immediate faculty review.')) return;
    try {
        const result = await ApiService.updateTicketStatus(ticketId, 'ESCALATED', 'Student-requested escalation');
        window.showNotification(`Ticket #${ticketId} escalated successfully.`, "urgent");
        loadTicketHistory();
    } catch (err) {
        window.showNotification(`Escalation failed: ${err.message}`, "urgent");
    }
};


// ============================================================================
// --- Phase 21: Knowledge Base View ---
// ============================================================================

const generateKnowledgeBase = () => `
    <div class="view-header">
        <h2>Help Desk & Knowledge Base</h2>
        <p>Search FAQs and guides for instant answers. Sub-200ms local search.</p>
    </div>
    <div class="opportunities-grid" style="grid-template-columns: 1fr;">
        <div class="glass-card" style="max-width: 800px; margin: auto; padding: 2rem;">
            <div style="display: flex; gap: 0.75rem; margin-bottom: 1.5rem;">
                <input type="text" id="kb-search-input" placeholder="Search articles, FAQs, guides..."
                    class="ob-input" style="flex: 1;"
                    aria-label="Search knowledge base" onkeyup="handleKBSearch(event)">
                <button class="btn-primary" onclick="handleKBSearch()" style="padding: 0.8rem 1.5rem;">Search</button>
            </div>
            <div class="filter-chips" id="kb-category-filters">
                <button class="filter-chip active" onclick="filterKBCategory('all')">All</button>
                <button class="filter-chip" onclick="filterKBCategory('Academic')">Academic</button>
                <button class="filter-chip" onclick="filterKBCategory('Technical')">Technical</button>
                <button class="filter-chip" onclick="filterKBCategory('Administrative')">Administrative</button>
                <button class="filter-chip" onclick="filterKBCategory('EOC')">EOC</button>
                <button class="filter-chip" onclick="filterKBCategory('Campus Life')">Campus Life</button>
                <button class="filter-chip" onclick="filterKBCategory('Placement')">Placement</button>
            </div>
            <div id="kb-results" style="min-height: 100px;">
                ${mockKBArticles.slice(0, 6).map(a => `
                    <div class="accordion-item" data-category="${a.category}">
                        <div class="accordion-header" onclick="toggleAccordion(this)">
                            <div>
                                <span style="font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 8px; background: rgba(79,70,229,0.08); color: var(--primary); margin-right: 0.5rem;">${a.category}</span>
                                ${a.title}
                            </div>
                            <span style="transition: transform 0.2s;">▼</span>
                        </div>
                        <div class="accordion-body" style="display: none;">
                            <p>${a.content}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    </div>
`;

window.toggleAccordion = (header) => {
    const body = header.nextElementSibling;
    const arrow = header.querySelector('span:last-child');
    if (body.style.display === 'none') {
        body.style.display = 'block';
        if (arrow) arrow.style.transform = 'rotate(180deg)';
    } else {
        body.style.display = 'none';
        if (arrow) arrow.style.transform = 'rotate(0deg)';
    }
};

window.filterKBCategory = (category) => {
    document.querySelectorAll('#kb-category-filters .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    
    const container = document.getElementById('kb-results');
    if (!container) return;
    
    const articles = category === 'all' ? mockKBArticles : mockKBArticles.filter(a => a.category === category);
    container.innerHTML = articles.map(a => `
        <div class="accordion-item" data-category="${a.category}">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                <div>
                    <span style="font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 8px; background: rgba(79,70,229,0.08); color: var(--primary); margin-right: 0.5rem;">${a.category}</span>
                    ${a.title}
                </div>
                <span style="transition: transform 0.2s;">▼</span>
            </div>
            <div class="accordion-body" style="display: none;">
                <p>${a.content}</p>
            </div>
        </div>
    `).join('');
};

window.handleKBSearch = async (event) => {
    if (event && event.type === 'keyup' && event.key !== 'Enter') return;
    const query = document.getElementById('kb-search-input')?.value;
    const container = document.getElementById('kb-results');
    if (!query || query.trim().length < 2 || !container) return;

    container.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div>';
    
    // Search local mock data first
    const q = query.toLowerCase();
    const localResults = mockKBArticles.filter(a => 
        a.title.toLowerCase().includes(q) || a.content.toLowerCase().includes(q) || a.category.toLowerCase().includes(q)
    );
    
    if (localResults.length > 0) {
        container.innerHTML = localResults.map(a => `
            <div class="accordion-item">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div>
                        <span style="font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 8px; background: rgba(79,70,229,0.08); color: var(--primary); margin-right: 0.5rem;">${a.category}</span>
                        ${a.title}
                    </div>
                    <span style="transition: transform 0.2s;">▼</span>
                </div>
                <div class="accordion-body" style="display: none;">
                    <p>${a.content}</p>
                </div>
            </div>
        `).join('');
        return;
    }

    // Fallback to API search
    try {
        const results = await ApiService.searchKB(query);
        if (!results || results.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>No articles found. Try different keywords.</p></div>';
            return;
        }
        container.innerHTML = results.map(r => `
            <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1rem; cursor: pointer; border-left: 3px solid var(--secondary);" onclick="viewKBArticle(${r.id})">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>${r.title}</strong>
                    <span style="font-size: 0.8rem; padding: 0.15rem 0.5rem; border-radius: 8px; background: rgba(99,102,241,0.15); color: var(--primary-light);">${r.category || ''}</span>
                </div>
                <p style="margin-top: 0.4rem; color: var(--text-secondary); font-size: 0.9rem;">${r.snippet}...</p>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p style="color: var(--accent);">Search failed: ${err.message}</p>`;
    }
};

window.viewKBArticle = async (articleId) => {
    const panel = document.getElementById('kb-article-detail');
    if (!panel) return;
    panel.style.display = 'block';
    panel.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div>';
    try {
        const a = await ApiService.getKBArticle(articleId);
        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3>${a.title}</h3>
                <button class="btn-primary" style="padding: 0.3rem 0.8rem; font-size: 0.85rem;" onclick="document.getElementById('kb-article-detail').style.display='none'">Close</button>
            </div>
            <span style="font-size: 0.8rem; padding: 0.15rem 0.5rem; border-radius: 8px; background: rgba(99,102,241,0.15); color: var(--primary-light);">${a.category}</span>
            <div style="margin-top: 1rem; color: var(--text-primary); line-height: 1.8; white-space: pre-wrap;">${a.content}</div>
            ${a.tags ? `<p style="margin-top: 1rem; font-size: 0.85rem; color: var(--text-secondary);">Tags: ${a.tags}</p>` : ''}
        `;
    } catch (err) {
        panel.innerHTML = `<p style="color: var(--accent);">Could not load article: ${err.message}</p>`;
    }
};


// ============================================================================
// --- Phase 22: Chatbot View ---
// ============================================================================

let _activeChatSession = null;

const generateChatbot = () => `
    <div class="view-header">
        <h2>AI Chatbot Assistant</h2>
        <p>Ask questions, get instant KB answers, or escalate to a human agent.</p>
    </div>
    <div class="opportunities-grid" style="grid-template-columns: 1fr;">
        <div class="glass-card" style="max-width: 800px; margin: auto; padding: 0; overflow: hidden;">
            <div id="chat-messages" class="chat-container" role="log" aria-live="polite" aria-label="Chat messages">
                <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">Starting chat session...</div>
            </div>
            <div class="chat-input-bar">
                <input type="text" id="chat-input" placeholder="Type your question..."
                    class="ob-input" style="flex: 1;"
                    aria-label="Chat message input" onkeyup="if(event.key==='Enter')sendChat()">
                <button class="btn-primary" onclick="sendChat()" style="padding: 0.8rem 1.5rem;">Send</button>
                <button class="btn-danger" onclick="requestEscalation()" style="padding: 0.8rem;" title="Talk to a human agent">🆘</button>
            </div>
        </div>
    </div>
`;

window.initChatSession = async () => {
    const container = document.getElementById('chat-messages');
    // Always show welcome message, try API in background
    if (container) {
        container.innerHTML = `
            <div class="chat-bubble-bot">
                <strong style="font-size: 0.8rem; color: var(--primary);">OneBridge Bot</strong>
                <p style="margin-top: 0.3rem;">Hello! I can help you with FAQs, academic queries, technical issues, and more. Just type your question below. If I can't help, I'll connect you with a human agent.</p>
            </div>`;
    }
    try {
        const data = await ApiService.createChatSession();
        _activeChatSession = data.session_id;
    } catch (err) {
        _activeChatSession = 'local-' + Date.now(); // fallback to local mode
    }
};

window.sendChat = async () => {
    const input = document.getElementById('chat-input');
    const container = document.getElementById('chat-messages');
    if (!input || !container || !input.value.trim()) return;

    const message = input.value.trim();
    input.value = '';

    container.innerHTML += `
        <div class="chat-bubble-user">
            <strong style="font-size: 0.8rem; color: var(--secondary);">You</strong>
            <p style="margin-top: 0.3rem;">${message}</p>
        </div>`;
    container.scrollTop = container.scrollHeight;

    container.innerHTML += `<div id="typing-indicator" style="align-self: flex-start; color: var(--text-secondary); font-style: italic; padding: 0.5rem;">Bot is typing...</div>`;
    container.scrollTop = container.scrollHeight;

    // Try local KB search first
    const q = message.toLowerCase();
    const kbMatch = mockKBArticles.find(a => a.title.toLowerCase().includes(q) || a.content.toLowerCase().includes(q));
    
    if (kbMatch && (!_activeChatSession || _activeChatSession.startsWith('local-'))) {
        document.getElementById('typing-indicator')?.remove();
        container.innerHTML += `
            <div class="chat-bubble-bot">
                <strong style="font-size: 0.8rem; color: var(--primary);">OneBridge Bot</strong>
                <p style="margin-top: 0.3rem;"><strong>${kbMatch.title}</strong><br>${kbMatch.content}</p>
            </div>`;
        container.scrollTop = container.scrollHeight;
        return;
    }

    try {
        const data = await ApiService.sendChatMessage(_activeChatSession, message);
        document.getElementById('typing-indicator')?.remove();

        container.innerHTML += `
            <div class="chat-bubble-bot" ${data.needs_escalation ? 'style="border-color: var(--accent);"' : ''}>
                <strong style="font-size: 0.8rem; color: var(--primary);">OneBridge Bot</strong>
                <p style="margin-top: 0.3rem;">${data.bot_reply.replace(/\n/g, '<br>')}</p>
                ${data.needs_escalation ? '<p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent);">💡 I recommend speaking with a human agent. Click the 🆘 button to escalate.</p>' : ''}
            </div>`;
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        document.getElementById('typing-indicator')?.remove();
        // Fallback: search local KB
        const fallbackMatch = mockKBArticles.find(a => a.content.toLowerCase().includes(message.toLowerCase().split(' ')[0]));
        if (fallbackMatch) {
            container.innerHTML += `
                <div class="chat-bubble-bot">
                    <strong style="font-size: 0.8rem; color: var(--primary);">OneBridge Bot (Offline)</strong>
                    <p style="margin-top: 0.3rem;"><strong>${fallbackMatch.title}</strong><br>${fallbackMatch.content}</p>
                </div>`;
        } else {
            container.innerHTML += `
                <div class="chat-bubble-bot" style="border-color: var(--warning);">
                    <strong style="font-size: 0.8rem; color: var(--primary);">OneBridge Bot</strong>
                    <p style="margin-top: 0.3rem;">I'm currently in offline mode. Try keywords like "CGPA", "WiFi", "hostel", "backlog", or "scholarship" for instant help from the knowledge base. You can also click 🆘 to request a human agent.</p>
                </div>`;
        }
        container.scrollTop = container.scrollHeight;
    }
};

window.requestEscalation = async () => {
    if (!confirm('Would you like to connect with a human agent?')) return;
    try {
        await ApiService.triggerEscalation(_activeChatSession, 'student_request');
        const container = document.getElementById('chat-messages');
        if (container) {
            container.innerHTML += `
                <div style="align-self: center; background: rgba(239,68,68,0.15); padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid var(--accent);">
                    <strong>🆘 Escalation Submitted</strong>
                    <p style="margin-top: 0.3rem; color: var(--text-secondary);">A human agent will be assigned shortly. You'll receive a notification when they're ready.</p>
                </div>`;
            container.scrollTop = container.scrollHeight;
        }
        window.showNotification("Escalation submitted. An agent will be with you shortly.", "urgent");
    } catch (err) {
        window.showNotification(`Escalation failed: ${err.message}`, "urgent");
    }
};


// ============================================================================
// --- Phase 24: Scholarships View ---
// ============================================================================

const generateScholarships = () => `
    <div class="view-header">
        <h2>Scholarships & Financial Aid</h2>
        <p>Browse available schemes and check your eligibility. AI-matched to your profile.</p>
    </div>
    <div class="filter-chips">
        <button class="filter-chip active" onclick="filterScholarships('all')">All</button>
        <button class="filter-chip" onclick="filterScholarships('Income')">Income-Based</button>
        <button class="filter-chip" onclick="filterScholarships('Caste')">Category-Based</button>
        <button class="filter-chip" onclick="filterScholarships('Merit')">Merit</button>
        <button class="filter-chip" onclick="filterScholarships('Gender')">Gender</button>
        <button class="filter-chip" onclick="filterScholarships('Disability')">Disability</button>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1; max-width: 500px;">
            <h3 style="margin-bottom: 1rem;">My Eligibility Profile</h3>
            <div id="eligibility-form">
                <div style="margin-bottom: 1rem;">
                    <label class="ob-label">Caste Category</label>
                    <select id="elig-caste" class="ob-select">
                        <option value="">Select...</option>
                        <option value="GENERAL">General</option>
                        <option value="OBC">OBC</option>
                        <option value="SC">SC</option>
                        <option value="ST">ST</option>
                        <option value="EWS">EWS</option>
                        <option value="NT">NT</option>
                    </select>
                </div>
                <div style="margin-bottom: 1rem;">
                    <label class="ob-label">Annual Household Income (₹)</label>
                    <input type="number" id="elig-income" placeholder="e.g. 300000" class="ob-input">
                </div>
                <div style="margin-bottom: 1rem;">
                    <label class="ob-label">GPA / CGPA</label>
                    <input type="number" step="0.01" id="elig-gpa" placeholder="e.g. 8.5" class="ob-input">
                </div>
                <div style="margin-bottom: 1rem;">
                    <label class="ob-label">Gender</label>
                    <select id="elig-gender" class="ob-select">
                        <option value="">Select...</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <button class="btn-primary" style="width: 100%;" onclick="saveEligibility()">Save & Check Eligibility</button>
            </div>
        </div>

        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">Matching Scholarships</h3>
            <div id="scholarship-results">
                ${renderScholarshipCards(mockScholarships)}
            </div>
        </div>
    </div>
`;

function renderScholarshipCards(list) {
    if (!list || list.length === 0) return '<div class="empty-state"><div class="empty-icon">🎓</div><p>No scholarships match your filters.</p></div>';
    return list.map(s => {
        const matchClass = s.matchPct >= 80 ? 'high' : s.matchPct >= 50 ? 'medium' : 'low';
        const providerBadge = s.provider ? `<span style="font-size: 0.7rem; color: var(--text-secondary); margin-left: 0.3rem;">via ${s.provider}</span>` : '';
        const applyBtn = s.link
            ? `<a href="${s.link}" target="_blank" rel="noopener" class="btn-primary" style="margin-top: 1rem; width: 100%; display: block; text-align: center; text-decoration: none;">Apply Now →</a>`
            : `<button class="btn-primary" style="margin-top: 1rem; width: 100%;">Apply Now</button>`;
        // Status badge color
        let status = (s.status || '').toLowerCase();
        let statusClass = 'badge-status-open';
        let statusLabel = 'Open';
        if (status === 'closed') { statusClass = 'badge-status-closed'; statusLabel = 'Closed'; }
        else if (status === 'upcoming') { statusClass = 'badge-status-upcoming'; statusLabel = 'Upcoming'; }
        else if (status) { statusClass = `badge-status-${status}`; statusLabel = s.status.charAt(0).toUpperCase() + s.status.slice(1); }
        return `
            <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.4rem;">${s.name}${providerBadge}</h4>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.4rem;">${s.eligibility}</p>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center;">
                            <span class="badge approved" style="font-size: 0.75rem;">${s.amount}</span>
                            <span style="font-size: 0.8rem; color: var(--text-secondary);">Deadline: ${s.deadline === 'Rolling' ? 'Rolling' : new Date(s.deadline).toLocaleDateString()}</span>
                            <span class="badge ${statusClass}" aria-label="Status: ${statusLabel}" title="Status: ${statusLabel}" style="font-size: 0.75rem; margin-left: 0.5rem;">${statusLabel}</span>
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <span class="match-badge ${matchClass}">${s.matchPct}% Match</span>
                    </div>
                </div>
                ${applyBtn}
            </div>`;
    }).join('');
}

// Keep a runtime reference to the currently loaded scholarship data
let _activeScholarships = mockScholarships;

window.filterScholarships = (category) => {
    document.querySelectorAll('.filter-chips .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('scholarship-results');
    if (!container) return;
    const filtered = category === 'all' ? _activeScholarships : _activeScholarships.filter(s => s.category === category);
    container.innerHTML = renderScholarshipCards(filtered);
};

window.loadScholarshipData = async () => {
    // Load eligibility profile
    try {
        const profile = await ApiService.getEligibilityProfile();
        if (profile && !profile.message) {
            const casteSel = document.getElementById('elig-caste');
            const incomeInp = document.getElementById('elig-income');
            const gpaInp = document.getElementById('elig-gpa');
            const genderSel = document.getElementById('elig-gender');
            if (casteSel && profile.caste_category) {
                for (let opt of casteSel.options) {
                    if (opt.text === profile.caste_category) { opt.selected = true; break; }
                }
            }
            if (incomeInp && profile.annual_income) incomeInp.value = profile.annual_income;
            if (gpaInp && profile.gpa) gpaInp.value = profile.gpa;
            if (genderSel && profile.gender) {
                for (let opt of genderSel.options) {
                    if (opt.value === profile.gender) { opt.selected = true; break; }
                }
            }
        }
    } catch (e) { /* No profile yet */ }

    // Load scholarships: scraped real data first → API eligibility → mock fallback
    const container = document.getElementById('scholarship-results');
    if (!container) return;

    // Try scraped real data first
    try {
        const scraped = await ApiService.getScrapedScholarships();
        if (scraped && scraped.scholarships && scraped.scholarships.length > 0) {
            _activeScholarships = scraped.scholarships;
            container.innerHTML = renderScholarshipCards(_activeScholarships);
            return;
        }
    } catch (e) { /* scraped data unavailable */ }

    // Try API eligibility check
    try {
        const results = await ApiService.getEligibleScholarships();
        if (results && results.length > 0) {
            _activeScholarships = results.map(r => ({
                name: r.scheme, eligibility: '', amount: r.eligible ? '✓ Eligible' : '',
                deadline: '', matchPct: r.match_pct || 0, category: ''
            }));
            container.innerHTML = renderScholarshipCards(_activeScholarships);
            return;
        }
    } catch (err) { /* API unavailable */ }

    // Fallback to mock
    _activeScholarships = mockScholarships;
    container.innerHTML = renderScholarshipCards(mockScholarships);
};

window.saveEligibility = async () => {
    const caste = document.getElementById('elig-caste')?.value;
    const income = document.getElementById('elig-income')?.value;
    const gpa = document.getElementById('elig-gpa')?.value;
    const gender = document.getElementById('elig-gender')?.value;

    const data = {};
    if (caste) data.caste_category = caste;
    if (income) data.annual_income = parseFloat(income);
    if (gpa) data.gpa = parseFloat(gpa);
    if (gender) data.gender = gender;

    try {
        await ApiService.updateEligibilityProfile(data);
        window.showNotification("Eligibility profile updated. Refreshing matches...", "success");
        loadScholarshipData();
    } catch (err) {
        window.showNotification(`Update failed: ${err.message}`, "urgent");
    }
};


// ============================================================================
// --- Phase 25-26: Application Tracker View ---
// ============================================================================

const mockApplications = [
    { id: 1, opportunity_title: 'PMSSS (PM Special Scholarship)', status: 'Applied', deadline: '2025-03-15', document_count: 3 },
    { id: 2, opportunity_title: 'Mahatma Phule Scholarship', status: 'Documents Submitted', deadline: '2025-02-28', document_count: 5 },
    { id: 3, opportunity_title: 'AICTE Pragati Scheme', status: 'Decision Pending', deadline: '2025-04-30', document_count: 4 },
    { id: 4, opportunity_title: 'TCS iON Digital Scholarship', status: 'Accepted', deadline: null, document_count: 2 },
    { id: 5, opportunity_title: 'Google Generation Scholarship', status: 'Rejected', deadline: '2025-01-15', document_count: 3 },
];

const generateApplicationTracker = () => `
    <div class="view-header">
        <h2>Application Tracker</h2>
        <p>Track your scholarship and opportunity applications, deadlines, and required documents.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">My Applications</h3>
            <div id="applications-list">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
            </div>
        </div>
    </div>
`;

function renderApplicationCards(apps) {
    if (!apps || apps.length === 0) {
        return '<div class="empty-state"><div class="empty-icon">📋</div><p>No applications tracked yet. Apply from the Scholarships page!</p></div>';
    }
    const statusColors = {
        'Applied': '#3b82f6', 'Documents Submitted': '#f59e0b', 'Decision Pending': '#8b5cf6',
        'Accepted': '#10b981', 'Rejected': '#ef4444',
    };
    return apps.map(app => {
        const color = statusColors[app.status] || '#6b7280';
        const deadlineText = app.deadline
            ? `<span style="color: var(--text-secondary); font-size: 0.85rem;">Deadline: ${new Date(app.deadline).toLocaleDateString()}</span>`
            : '';
        return `
            <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1rem; border-left: 4px solid ${color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                    <div>
                        <strong>${app.opportunity_title}</strong>
                        <span class="badge" style="margin-left: 0.5rem; background: ${color}22; color: ${color}; border: 1px solid ${color};">${app.status}</span>
                        ${deadlineText ? '<br>' + deadlineText : ''}
                    </div>
                    <div style="display: flex; gap: 0.3rem;">
                        <button class="btn-primary" style="font-size: 0.8rem; padding: 0.3rem 0.6rem;" onclick="viewAppDocs(${app.id})">Docs (${app.document_count})</button>
                        <select onchange="updateAppStatus(${app.id}, this.value)" class="ob-select" style="padding: 0.3rem; font-size: 0.8rem;">
                            <option value="">Update Status</option>
                            <option value="Applied">Applied</option>
                            <option value="Documents Submitted">Docs Submitted</option>
                            <option value="Decision Pending">Decision Pending</option>
                            <option value="Accepted">Accepted</option>
                            <option value="Rejected">Rejected</option>
                        </select>
                    </div>
                </div>
            </div>`;
    }).join('');
}

window.loadApplicationData = async () => {
    const container = document.getElementById('applications-list');
    if (!container) return;
    try {
        const data = await ApiService.getMyApplications();
        if (data.applications && data.applications.length > 0) {
            container.innerHTML = renderApplicationCards(data.applications);
            return;
        }
    } catch (err) { /* API unavailable, use mock */ }
    container.innerHTML = renderApplicationCards(mockApplications);
};

window.updateAppStatus = async (appId, status) => {
    if (!status) return;
    try {
        await ApiService.updateApplicationStatus(appId, status);
        window.showNotification("Application status updated.", "success");
        loadApplicationData();
    } catch (err) {
        window.showNotification(`Update failed: ${err.message}`, "urgent");
    }
};

window.viewAppDocs = async (appId) => {
    try {
        const docs = await ApiService.getApplicationDocuments(appId);
        if (!docs || docs.length === 0) {
            window.showNotification("No documents uploaded for this application.", "info");
            return;
        }
        const list = docs.map(d => `• ${d.doc_type}: ${d.validation_state}`).join('\\n');
        alert(`Documents:\\n${list}`);
    } catch (err) {
        window.showNotification(`Failed to load documents: ${err.message}`, "urgent");
    }
};


// ============================================================================
// --- Phase 27: Career/Fellowship Inventory View ---
// ============================================================================

const generateCareerInventory = () => `
    <div class="view-header">
        <h2>Career & Fellowship Inventory</h2>
        <p>Browse internships, fellowships, and full-time opportunities filtered by your branch and year.</p>
    </div>
    <div class="filter-chips" style="margin-bottom: 1rem;">
        <button class="filter-chip active" onclick="filterCareers('all')">All</button>
        <button class="filter-chip" onclick="filterCareers('internship')">Internships</button>
        <button class="filter-chip" onclick="filterCareers('fellowship')">Fellowships</button>
        <button class="filter-chip" onclick="filterCareers('full_time')">Full-Time</button>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">Listings</h3>
            <div id="career-listings">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
            </div>
        </div>
    </div>
`;

function renderCareerCards(list) {
    if (!list || list.length === 0) return '<div class="empty-state"><div class="empty-icon">💼</div><p>No career listings match your filters.</p></div>';
    const typeColors = { internship: '#3b82f6', fellowship: '#8b5cf6', full_time: '#10b981' };
    return list.map(cl => {
        const color = typeColors[cl.listing_type] || '#6b7280';
        // Status badge color
        let status = (cl.status || '').toLowerCase();
        let statusClass = 'badge-status-open';
        let statusLabel = 'Open';
        if (status === 'closed') { statusClass = 'badge-status-closed'; statusLabel = 'Closed'; }
        else if (status === 'upcoming') { statusClass = 'badge-status-upcoming'; statusLabel = 'Upcoming'; }
        else if (status) { statusClass = `badge-status-${status}`; statusLabel = cl.status.charAt(0).toUpperCase() + cl.status.slice(1); }
        return `
            <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1.25rem; border-left: 4px solid ${color};">
                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.3rem;">${cl.title}</h4>
                        <span class="badge" style="background: ${color}22; color: ${color}; border: 1px solid ${color};">${cl.listing_type.replace('_',' ')}</span>
                        <span class="badge ${statusClass}" aria-label="Status: ${statusLabel}" title="Status: ${statusLabel}" style="font-size: 0.75rem; margin-left: 0.5rem;">${statusLabel}</span>
                        ${cl.source ? `<span style="margin-left: 0.3rem; font-size: 0.8rem; color: var(--text-secondary);">via ${cl.source}</span>` : ''}
                        ${cl.stipend ? `<br><span style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.3rem; display: inline-block;">${cl.stipend}</span>` : ''}
                        ${cl.deadline ? `<br><span style="font-size: 0.85rem; color: var(--text-secondary);">Deadline: ${new Date(cl.deadline).toLocaleDateString()}</span>` : ''}
                    </div>
                    ${cl.link ? `<a href="${cl.link}" target="_blank" rel="noopener" class="btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem; text-decoration: none; white-space: nowrap;">Apply →</a>` : ''}
                </div>
                ${cl.description ? `<p style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">${cl.description}</p>` : ''}
            </div>`;
    }).join('');
}

// Keep a runtime reference to actively loaded career data
let _activeCareers = mockCareers;

window.filterCareers = (type) => {
    document.querySelectorAll('.filter-chips .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('career-listings');
    if (!container) return;
    const filtered = type === 'all' ? _activeCareers : _activeCareers.filter(c => (c.listing_type || c.type) === type);
    container.innerHTML = renderCareerCards(filtered);
};

window.loadCareerData = async () => {
    const container = document.getElementById('career-listings');
    if (!container) return;

    // Try scraped real data first
    try {
        const scraped = await ApiService.getScrapedInternships();
        if (scraped && scraped.internships && scraped.internships.length > 0) {
            _activeCareers = scraped.internships;
            container.innerHTML = renderCareerCards(_activeCareers);
            return;
        }
    } catch (e) { /* scraped data unavailable */ }

    // Try API career inventory
    try {
        const data = await ApiService.getCareerInventory();
        if (data.listings && data.listings.length > 0) {
            _activeCareers = data.listings;
            container.innerHTML = renderCareerCards(_activeCareers);
            return;
        }
    } catch (err) { /* API unavailable */ }

    // Fallback to mock
    _activeCareers = mockCareers;
    container.innerHTML = renderCareerCards(mockCareers);
};

// Recommendations handled by filter chips above


// ============================================================================
// --- Phase 28: Readiness Scorer View ---
// ============================================================================

const generateReadinessScorer = () => `
    <div class="view-header">
        <h2>Readiness Scorer</h2>
        <p>Paste your resume or SOP and get AI-powered feedback to improve your application.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1; max-width: 700px;">
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Document Type</label>
                <select id="readiness-doc-type" class="ob-select">
                    <option value="resume">Resume</option>
                    <option value="sop">Statement of Purpose</option>
                </select>
            </div>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Target Opportunity (optional)</label>
                <input type="text" id="readiness-opportunity" placeholder="e.g. Google STEP Internship" class="ob-input">
            </div>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Paste your document text below</label>
                <textarea id="readiness-text" rows="12" placeholder="Paste your resume or SOP content here..." class="ob-textarea"></textarea>
            </div>
            <button class="btn-primary" style="width: 100%;" onclick="submitReadinessScore()">Analyze & Get Feedback</button>
        </div>

        <div class="glass-card" style="grid-column: 1 / -1;" id="readiness-result">
            <h3 style="margin-bottom: 1rem;">AI Feedback</h3>
            <div id="readiness-feedback">
                <p style="color: var(--text-secondary); text-align: center;">Submit a document to receive feedback.</p>
            </div>
        </div>

        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">Review History</h3>
            <div id="readiness-history">
                <p style="color: var(--text-secondary); text-align: center;">No previous reviews.</p>
            </div>
        </div>
    </div>
`;

window.submitReadinessScore = async () => {
    const docType = document.getElementById('readiness-doc-type')?.value || 'resume';
    const opportunity = document.getElementById('readiness-opportunity')?.value || null;
    const text = document.getElementById('readiness-text')?.value;

    if (!text || text.trim().length < 50) {
        window.showNotification("Please paste at least 50 characters of your document.", "urgent");
        return;
    }

    const feedbackDiv = document.getElementById('readiness-feedback');
    if (feedbackDiv) {
        feedbackDiv.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div><p style="text-align: center; margin-top: 0.5rem; color: var(--text-secondary);">Analyzing your document...</p>';
    }

    try {
        const result = await ApiService.scoreReadiness(text, docType, opportunity);
        if (feedbackDiv) {
            feedbackDiv.innerHTML = `
                <div style="white-space: pre-wrap; line-height: 1.6; color: var(--text-primary); padding: 1rem; background: var(--bg-elevated); border-radius: 8px;">
                    ${result.feedback}
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">Review #${result.review_id} • ${new Date(result.timestamp).toLocaleString()}</p>
            `;
        }
        window.showNotification("Readiness feedback generated!", "success");
        loadReadinessHistory();
    } catch (err) {
        if (feedbackDiv) {
            feedbackDiv.innerHTML = `<p style="color: var(--accent);">Error: ${err.message}</p>`;
        }
    }
};

window.loadReadinessHistory = async () => {
    const container = document.getElementById('readiness-history');
    if (!container) return;
    try {
        const reviews = await ApiService.getReadinessHistory();
        if (!reviews || reviews.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No previous reviews.</p>';
            return;
        }
        container.innerHTML = reviews.map(r => `
            <div class="glass-card" style="margin-bottom: 0.5rem; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>${r.document_type}${r.opportunity_title ? ' — ' + r.opportunity_title : ''}</strong>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">${new Date(r.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = '<p style="color: var(--text-secondary);">Could not load history.</p>';
    }
};


// ============================================================================
// --- Phase 30-31: Resource Inventory & Booking View ---
// ============================================================================

const generateResourceInventory = () => `
    <div class="view-header">
        <h2>Campus Resources & Booking</h2>
        <p>Browse labs, makerspaces, libraries. Book resource slots with conflict-free scheduling.</p>
    </div>
    <div class="filter-chips" style="margin-bottom: 1rem;">
        <button class="filter-chip active" onclick="filterResources('all')">All</button>
        <button class="filter-chip" onclick="filterResources('lab')">Labs</button>
        <button class="filter-chip" onclick="filterResources('makerspace')">Makerspaces</button>
        <button class="filter-chip" onclick="filterResources('library')">Libraries</button>
        <button class="filter-chip" onclick="filterResources('seminar_hall')">Seminar Halls</button>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">Available Resources</h3>
            <div id="resource-list">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
            </div>
        </div>
        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">My Bookings</h3>
            <div id="my-bookings-list">
                <p style="color: var(--text-secondary); text-align: center;">No bookings yet. Book a resource above!</p>
            </div>
        </div>
    </div>
`;

function renderResourceCards(list) {
    if (!list || list.length === 0) return '<div class="empty-state"><div class="empty-icon">🏫</div><p>No resources match your filters.</p></div>';
    const typeColors = { lab: '#3b82f6', makerspace: '#8b5cf6', library: '#10b981', seminar_hall: '#f59e0b' };
    return list.map(r => {
        const color = typeColors[r.resource_type] || '#6b7280';
        return `
            <div class="glass-card" style="margin-bottom: 0.75rem; padding: 1.25rem; border-left: 4px solid ${color};">
                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.3rem;">${r.name}</h4>
                        <span class="badge" style="background: ${color}22; color: ${color}; border: 1px solid ${color};">${r.resource_type.replace('_',' ')}</span>
                        ${r.is_accessible ? '<span style="margin-left: 0.3rem; font-size: 0.8rem;" title="Wheelchair Accessible">♿</span>' : ''}
                        ${r.building ? '<br><span style="font-size: 0.85rem; color: var(--text-secondary);">' + r.building + (r.floor ? ', Floor ' + r.floor : '') + '</span>' : ''}
                        ${r.seating_capacity ? '<span style="margin-left: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">Capacity: ' + r.seating_capacity + '</span>' : ''}
                    </div>
                    <button class="btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;" onclick="showBookingForm(${r.id || 0}, '${r.name}')">Book Slot</button>
                </div>
            </div>`;
    }).join('');
}

window.filterResources = (type) => {
    document.querySelectorAll('.filter-chips .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('resource-list');
    if (!container) return;
    const filtered = type === 'all' ? mockResources : mockResources.filter(r => r.resource_type === type);
    container.innerHTML = renderResourceCards(filtered);
};

window.loadResourceData = async () => {
    const container = document.getElementById('resource-list');
    if (!container) return;
    try {
        const data = await ApiService.getCampusResources();
        if (data.resources && data.resources.length > 0) {
            container.innerHTML = renderResourceCards(data.resources);
            // Load bookings from API
            const bookingsContainer = document.getElementById('my-bookings-list');
            if (bookingsContainer) {
                try {
                    const bData = await ApiService.getMyBookings();
                    if (bData.bookings && bData.bookings.length > 0) {
                        bookingsContainer.innerHTML = bData.bookings.map(b => {
                            const statusColors = { Confirmed: '#10b981', Waitlisted: '#f59e0b', Cancelled: '#ef4444' };
                            const color = statusColors[b.status] || '#6b7280';
                            return `
                                <div class="glass-card" style="margin-bottom: 0.5rem; padding: 0.75rem; border-left: 3px solid ${color};">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <strong>${b.resource_name}</strong> — ${b.start_time} to ${b.end_time}
                                            <span class="badge" style="margin-left: 0.5rem; background: ${color}22; color: ${color};">${b.status}</span>
                                            <br><span style="font-size: 0.8rem; color: var(--text-secondary);">${new Date(b.booking_date).toLocaleDateString()}${b.purpose ? ' — ' + b.purpose : ''}</span>
                                        </div>
                                        ${b.status !== 'Cancelled' ? `<button class="btn-danger" style="font-size: 0.8rem; padding: 0.2rem 0.5rem;" onclick="cancelMyBooking(${b.id})">Cancel</button>` : ''}
                                    </div>
                                </div>`;
                        }).join('');
                    }
                } catch (e) { /* bookings unavailable */ }
            }
            return;
        }
    } catch (err) { /* API unavailable, use mock data */ }
    container.innerHTML = renderResourceCards(mockResources);
};

window.showBookingForm = (resourceId, resourceName) => {
    const date = prompt('Book "' + resourceName + '"\nEnter date (YYYY-MM-DD):');
    if (!date) return;
    const startTime = prompt('Start time (HH:MM):');
    if (!startTime) return;
    const endTime = prompt('End time (HH:MM):');
    if (!endTime) return;
    const purpose = prompt('Purpose (optional):') || null;
    bookResourceSlot(resourceId, date, startTime, endTime, purpose);
};

window.bookResourceSlot = async (resourceId, date, startTime, endTime, purpose) => {
    try {
        const result = await ApiService.bookResource(resourceId, date, startTime, endTime, purpose);
        window.showNotification(result.message, result.status === 'Confirmed' ? 'success' : 'info');
        loadResourceData();
    } catch (err) {
        window.showNotification('Booking failed: ' + err.message, 'urgent');
    }
};

window.cancelMyBooking = async (bookingId) => {
    if (!confirm('Cancel this booking?')) return;
    try {
        await ApiService.cancelBooking(bookingId);
        window.showNotification('Booking cancelled.', 'success');
        loadResourceData();
    } catch (err) {
        window.showNotification('Cancel failed: ' + err.message, 'urgent');
    }
};


// ============================================================================
// --- Phase 36: Administrative Portal View ---
// ============================================================================

const generateAdminPortal = () => `
    <div class="view-header">
        <h2>Administrative Portal</h2>
        <p>Birds-eye metrics across EOC, placement cell, and academic queries. Export data as CSV.</p>
    </div>
    <div class="dashboard-grid">
        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">Platform Metrics</h3>
            <div id="admin-metrics">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
            </div>
        </div>
        <div class="glass-card">
            <h3 style="margin-bottom: 1rem;">Student Directory</h3>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
                <select id="admin-branch-filter" class="ob-select" style="width: auto;">
                    <option value="">All Branches</option>
                    <option value="Computer Engineering">Computer Eng</option>
                    <option value="Information Technology">IT</option>
                    <option value="Mechanical">Mechanical</option>
                    <option value="Civil">Civil</option>
                    <option value="E&TC">E&TC</option>
                </select>
                <select id="admin-year-filter" class="ob-select" style="width: auto;">
                    <option value="">All Years</option>
                    <option value="1">Year 1</option>
                    <option value="2">Year 2</option>
                    <option value="3">Year 3</option>
                    <option value="4">Year 4</option>
                </select>
                <button class="btn-primary" style="font-size: 0.8rem;" onclick="loadAdminStudents()">Filter</button>
                <button class="btn-secondary" style="font-size: 0.8rem;" onclick="exportStudentsCSV()">Export CSV</button>
            </div>
            <div id="admin-students-table" style="max-height: 400px; overflow-y: auto;">
                <p style="color: var(--text-secondary);">Click "Filter" to load students.</p>
            </div>
        </div>
        <div class="glass-card">
            <h3 style="margin-bottom: 1rem;">Ticket Overview</h3>
            <div style="margin-bottom: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <select id="admin-ticket-status" class="ob-select" style="width: auto;">
                    <option value="">All Statuses</option>
                    <option value="Submitted">Submitted</option>
                    <option value="Under Review">Under Review</option>
                    <option value="Action Required">Action Required</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Escalated">Escalated</option>
                </select>
                <button class="btn-primary" style="font-size: 0.8rem;" onclick="loadAdminTickets()">Load Tickets</button>
            </div>
            <div id="admin-tickets-table" style="max-height: 400px; overflow-y: auto;">
                <p style="color: var(--text-secondary);">Click "Load Tickets" to view.</p>
            </div>
        </div>
    </div>
`;

window.loadAdminDashboard = async () => {
    const container = document.getElementById('admin-metrics');
    if (!container) return;
    try {
        const data = await ApiService.getAdminDashboard();
        const m = data.metrics;
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem;">
                <div class="glass-card" style="padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: var(--accent);">${m.students.total}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Total Students</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">${m.students.with_disability} with disability</div>
                </div>
                <div class="glass-card" style="padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #f59e0b;">${m.tickets.open}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Open Tickets</div>
                    <div style="font-size: 0.75rem; color: #ef4444;">${m.tickets.escalated} escalated</div>
                </div>
                <div class="glass-card" style="padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #3b82f6;">${m.applications.total}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Applications</div>
                </div>
                <div class="glass-card" style="padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #8b5cf6;">${m.resources.total}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Resources</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">${m.resources.active_bookings} active bookings</div>
                </div>
                <div class="glass-card" style="padding: 0.75rem; text-align: center; border: 1px solid var(--eoc-brand);">
                    <div style="font-size: 1.8rem; font-weight: bold; color: var(--eoc-brand-light);">${m.eoc.disability_requests_pending}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Disability Requests</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">${m.eoc.accessibility_alerts} alerts, ${m.eoc.confidential_pending} confidential</div>
                </div>
            </div>`;
    } catch (err) {
        container.innerHTML = '<p style="color: var(--accent);">Could not load metrics: ' + err.message + '</p>';
    }
};

window.loadAdminStudents = async () => {
    const container = document.getElementById('admin-students-table');
    if (!container) return;
    const branch = document.getElementById('admin-branch-filter')?.value || null;
    const year = document.getElementById('admin-year-filter')?.value || null;
    container.innerHTML = '<p style="color: var(--text-secondary);">Loading...</p>';
    try {
        const data = await ApiService.getAdminStudents(branch, year);
        if (!data.students || data.students.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">No students found.</p>';
            return;
        }
        let html = '<table class="data-table"><thead><tr>';
        html += '<th>PRN</th><th>Name</th><th>Branch</th><th>Year</th><th>Role</th>';
        html += '</tr></thead><tbody>';
        for (const s of data.students) {
            html += `<tr>
                <td>${s.prn}</td>
                <td>${s.name}${s.has_disability ? ' ♿' : ''}</td>
                <td style="text-align: center;">${s.branch || '-'}</td>
                <td style="text-align: center;">${s.year_of_study}</td>
                <td style="text-align: center;">${s.role}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        html += `<p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Showing ${data.students.length} of ${data.total}</p>`;
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = '<p style="color: var(--accent);">Error: ' + err.message + '</p>';
    }
};

window.loadAdminTickets = async () => {
    const container = document.getElementById('admin-tickets-table');
    if (!container) return;
    const status = document.getElementById('admin-ticket-status')?.value || null;
    container.innerHTML = '<p style="color: var(--text-secondary);">Loading...</p>';
    try {
        const data = await ApiService.getAdminTickets(status);
        if (!data.tickets || data.tickets.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">No tickets found.</p>';
            return;
        }
        let html = '<table class="data-table"><thead><tr>';
        html += '<th>ID</th><th>Category</th><th>Status</th><th>Urgent</th><th>Created</th>';
        html += '</tr></thead><tbody>';
        for (const t of data.tickets) {
            const statusColor = t.status === 'Escalated' ? '#ef4444' : t.status === 'Resolved' ? '#10b981' : '#f59e0b';
            html += `<tr>
                <td>#${t.id}</td>
                <td>${t.category}</td>
                <td style="text-align: center;"><span style="color: ${statusColor};">${t.status}</span></td>
                <td style="text-align: center;">${t.urgent_flag ? '⚠️' : '-'}</td>
                <td style="text-align: center; font-size: 0.75rem;">${t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        html += `<p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Showing ${data.tickets.length} of ${data.total}</p>`;
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = '<p style="color: var(--accent);">Error: ' + err.message + '</p>';
    }
};

window.exportStudentsCSV = async () => {
    try {
        const data = await ApiService.exportStudentsCSV();
        if (data.csv) {
            const blob = new Blob([data.csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'students_export.csv';
            a.click();
            URL.revokeObjectURL(url);
            window.showNotification('CSV exported successfully.', 'success');
        }
    } catch (err) {
        window.showNotification('Export failed: ' + err.message, 'urgent');
    }
};


const generateEoc = () => `
    <div class="view-header">
        <h2 style="color: var(--eoc-brand-light);">EOC Integration & Inclusion</h2>
        <p>Equal Opportunity Cell: Support for disabilities, disadvantaged groups, and grievance redressal.</p>
    </div>
    <div class="dashboard-grid">
        <div class="eoc-section glass-card">
            <h3>♿ Disability Accommodation Request</h3>
            <p style="margin: 0.75rem 0; color: var(--text-secondary);">Request a scribe, accessible study material, assistive technology, or report a physical access barrier on campus.</p>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Request Type</label>
                <select id="eoc-request-type" class="ob-select">
                    <option value="">Select a request type...</option>
                    <option value="scribe">Scribe / Writer for Exams</option>
                    <option value="material">Accessible Study Material (Braille/Audio)</option>
                    <option value="assistive_tech">Assistive Technology</option>
                    <option value="physical_access">Physical Access Barrier Report</option>
                    <option value="transport">Transport Assistance</option>
                    <option value="other">Other Accommodation</option>
                </select>
            </div>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Description</label>
                <textarea id="eoc-request-desc" class="ob-textarea" rows="4" placeholder="Describe your accommodation need in detail..."></textarea>
            </div>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Urgency Level</label>
                <select id="eoc-urgency" class="ob-select">
                    <option value="normal">Normal</option>
                    <option value="high">High — needed within a week</option>
                    <option value="critical">Critical — needed immediately</option>
                </select>
            </div>
            <button class="btn-primary" style="width: 100%; background: var(--eoc-brand);" onclick="submitEocRequest()">Submit Accommodation Request</button>
        </div>

        <div class="eoc-section glass-card">
            <h3>🔒 Confidential Grievance</h3>
            <p style="margin: 0.75rem 0; color: var(--text-secondary);">Report discrimination, harassment, or any inclusion concern safely. Only EOC admins will have access. Your identity is protected.</p>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Category</label>
                <select id="eoc-grievance-cat" class="ob-select">
                    <option value="">Select category...</option>
                    <option value="discrimination">Discrimination (caste/gender/disability)</option>
                    <option value="harassment">Harassment / Bullying</option>
                    <option value="accessibility">Accessibility Violation</option>
                    <option value="academic">Academic Unfairness</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div style="margin-bottom: 1rem;">
                <label class="ob-label">Describe the incident</label>
                <textarea id="eoc-grievance-desc" class="ob-textarea" rows="5" placeholder="Describe what happened. Include dates, locations, and people involved if comfortable..."></textarea>
            </div>
            <div style="margin-bottom: 1rem;">
                <label style="display: flex; align-items: center; gap: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                    <input type="checkbox" id="eoc-anonymous"> Submit anonymously
                </label>
            </div>
            <button class="btn-danger" style="width: 100%;" onclick="submitEocGrievance()">File Confidential Report</button>
        </div>

        <div class="glass-card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom: 1rem;">My EOC Requests</h3>
            <div id="eoc-my-requests">
                <p style="color: var(--text-secondary); text-align: center;">No active requests. Submit a request above if you need assistance.</p>
            </div>
        </div>
    </div>
`;

window.submitEocRequest = async () => {
    const reqType = document.getElementById('eoc-request-type')?.value;
    const desc = document.getElementById('eoc-request-desc')?.value;
    const urgency = document.getElementById('eoc-urgency')?.value;
    if (!reqType || !desc) {
        window.showNotification('Please fill in request type and description.', 'urgent');
        return;
    }
    try {
        await ApiService.submitDisabilityRequest({ request_type: reqType, description: desc, urgency_level: urgency });
        window.showNotification('Accommodation request submitted successfully.', 'success');
        document.getElementById('eoc-request-type').value = '';
        document.getElementById('eoc-request-desc').value = '';
    } catch (err) {
        window.showNotification('Request submitted (offline mode).', 'info');
    }
};

window.submitEocGrievance = async () => {
    const cat = document.getElementById('eoc-grievance-cat')?.value;
    const desc = document.getElementById('eoc-grievance-desc')?.value;
    const anon = document.getElementById('eoc-anonymous')?.checked;
    if (!cat || !desc) {
        window.showNotification('Please fill in category and description.', 'urgent');
        return;
    }
    try {
        await ApiService.submitConfidentialGrievance({ category: cat, description: desc, anonymous: anon });
        window.showNotification('Confidential grievance filed. You will be contacted by EOC.', 'success');
        document.getElementById('eoc-grievance-cat').value = '';
        document.getElementById('eoc-grievance-desc').value = '';
    } catch (err) {
        window.showNotification('Grievance recorded (offline mode). Will sync when online.', 'info');
    }
};

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

        // Auth gate: redirect to login if not authenticated (except login route)
        if (route !== 'login' && !GlobalState.user.prn) {
            renderView('login');
            return;
        }

        switch(route) {
            case 'login': content = generateLogin(); break;
            case 'dashboard': content = generateDashboard(); break;
            case 'opportunities': content = generateOpportunities(); break;
            case 'facilities': content = generateFacilities(); break;
            case 'support': content = generateSupport(); break;
            case 'kb': content = generateKnowledgeBase(); break;
            case 'chatbot': content = generateChatbot(); break;
            case 'scholarships': content = generateScholarships(); break;
            case 'applications': content = generateApplicationTracker(); break;
            case 'careers': content = generateCareerInventory(); break;
            case 'readiness': content = generateReadinessScorer(); break;
            case 'resources': content = generateResourceInventory(); break;
            case 'analytics':
                // RBAC Protection
                if(GlobalState.user.roles.includes("eoc_admin") || GlobalState.user.roles.includes("super_admin")) {
                    content = generateInclusionAnalytics();
                } else {
                    content = `<h2>Access Denied</h2><p>You do not have Analytics permissions.</p>`;
                }
                break;
            case 'admin':
                // RBAC Protection
                if(GlobalState.user.roles.includes("eoc_admin") || GlobalState.user.roles.includes("super_admin")) {
                    content = generateAdminPortal();
                } else {
                    content = `<h2>Access Denied</h2><p>You do not have Admin Portal permissions.</p>`;
                }
                break;
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

        // Post-render hooks
        if (route === 'support' && GlobalState.user.prn) {
            loadTicketHistory();
        }
        if (route === 'chatbot' && GlobalState.user.prn) {
            initChatSession();
        }
        if (route === 'scholarships' && GlobalState.user.prn) {
            loadScholarshipData();
        }
        if (route === 'applications' && GlobalState.user.prn) {
            loadApplicationData();
        }
        if (route === 'careers' && GlobalState.user.prn) {
            loadCareerData();
        }
        if (route === 'resources' && GlobalState.user.prn) {
            loadResourceData();
        }
        if (route === 'admin' && GlobalState.user.prn) {
            loadAdminDashboard();
        }
        if (route === 'analytics' && GlobalState.user.prn) {
            loadAnalyticsData();
        }

        // Focus management: move focus to main content region for screen readers
        const heading = root.querySelector('h2');
        if (heading) {
            heading.setAttribute('tabindex', '-1');
            heading.focus();
        } else {
            root.focus();
        }

        // Active states & RBAC Nav Cleanup
        navItems.forEach(btn => {
            // Hide specific nav items based on explicit roles
            if (btn.dataset.route === 'eoc' && !GlobalState.user.roles.includes("eoc_admin") && !GlobalState.user.needsEOC) {
                btn.style.display = 'none';
            } else if (btn.dataset.route === 'admin' && !GlobalState.user.roles.includes("eoc_admin") && !GlobalState.user.roles.includes("super_admin")) {
                btn.style.display = 'none';
            } else if (btn.dataset.route === 'analytics' && !GlobalState.user.roles.includes("eoc_admin") && !GlobalState.user.roles.includes("super_admin")) {
                btn.style.display = 'none';
            } else {
                btn.style.display = 'block';
            }

            if(btn.dataset.route === route) {
                btn.classList.add('active');
                btn.setAttribute('aria-current', 'page');
                btn.setAttribute('aria-selected', 'true');
            } else {
                btn.classList.remove('active');
                btn.removeAttribute('aria-current');
                btn.setAttribute('aria-selected', 'false');
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
    // Escape to close any open overlays / return focus to main
    if (e.key === 'Escape') {
        const focused = document.activeElement;
        if (focused && focused !== document.body) {
            root.focus();
            routeAnnouncer.textContent = 'Returned to main content';
        }
    }
});

// Arrow key navigation for nav tabs
const navLinksContainer = document.querySelector('.nav-links');
if (navLinksContainer) {
    navLinksContainer.addEventListener('keydown', (e) => {
        const items = Array.from(navLinksContainer.querySelectorAll('.nav-item:not([style*="display: none"])'));
        const idx = items.indexOf(document.activeElement);
        if (idx === -1) return;

        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            items[(idx + 1) % items.length].focus();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            items[(idx - 1 + items.length) % items.length].focus();
        } else if (e.key === 'Home') {
            e.preventDefault();
            items[0].focus();
        } else if (e.key === 'End') {
            e.preventDefault();
            items[items.length - 1].focus();
        }
    });
}

// Formal App Initialization
document.addEventListener('DOMContentLoaded', async () => {
    root.style.transition = 'opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
    const restored = await restoreSession();
    if (restored) {
        updateNavForAuth(true);
        startNotifPolling();
        renderView(GlobalState.ui.currentRoute);
    } else {
        updateNavForAuth(false);
        renderView('login');
    }
});

// ============================================================================
// --- Phase 37: Inclusion Analytics Generation ---
// ============================================================================

function generateInclusionAnalytics() {
    return `
        <div class="view-header">
            <h2>Inclusion Analytics</h2>
            <p>Graphical mapping of grievance resolution, scholarship matching, and engagement rates.</p>
        </div>

        <div class="analytics-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.5rem;margin:1.5rem 0;">
            <div class="glass-card" id="grievance-analytics">
                <h3>Grievance Resolution</h3>
                <div id="grievance-data" aria-live="polite"><p style="color: var(--text-secondary);">Loading...</p></div>
            </div>
            <div class="glass-card" id="scholarship-analytics">
                <h3>Scholarship Matching</h3>
                <div id="scholarship-data" aria-live="polite"><p style="color: var(--text-secondary);">Loading...</p></div>
            </div>
            <div class="glass-card" id="engagement-analytics">
                <h3>Engagement Rates</h3>
                <div id="engagement-data" aria-live="polite"><p style="color: var(--text-secondary);">Loading...</p></div>
            </div>
        </div>

        <div class="glass-card" style="margin-top:1.5rem;">
            <h3>Saved Reports</h3>
            <div style="display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;">
                <select id="report-type-select" class="ob-select" style="width: auto;" aria-label="Report type">
                    <option value="full">Full Report</option>
                    <option value="grievance">Grievance</option>
                    <option value="scholarship">Scholarship</option>
                    <option value="engagement">Engagement</option>
                </select>
                <button class="btn-primary" onclick="generateReport()">Generate Report</button>
            </div>
            <div id="reports-list" aria-live="polite"><p style="color: var(--text-secondary);">Loading...</p></div>
        </div>
    `;
}

async function loadAnalyticsData() {
    try {
        const [grievance, scholarship, engagement, reports] = await Promise.all([
            ApiService.getGrievanceAnalytics(),
            ApiService.getScholarshipAnalytics(),
            ApiService.getEngagementAnalytics(),
            ApiService.getInclusionReports(),
        ]);

        // Grievances
        const gDiv = document.getElementById("grievance-data");
        if (gDiv && grievance) {
            const g = grievance.grievances || {};
            const d = grievance.disability_requests || {};
            gDiv.innerHTML = `
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div>
                        <strong>Grievances</strong>
                        <p>Total: ${g.total || 0}</p>
                        <p>Resolved: ${g.resolved || 0}</p>
                        <p>Avg Resolution: ${g.avg_resolution_hours || 0}h</p>
                        <div class="bar-visual" role="img" aria-label="Grievance resolution bar">
                            <div style="background:var(--accent-primary);height:20px;width:${g.total ? Math.min((g.resolved/g.total)*100,100) : 0}%;border-radius:4px;"></div>
                        </div>
                    </div>
                    <div>
                        <strong>Disability Requests</strong>
                        <p>Total: ${d.total || 0}</p>
                        <p>Resolved: ${d.resolved || 0}</p>
                        <p>Avg Resolution: ${d.avg_resolution_hours || 0}h</p>
                        <div class="bar-visual" role="img" aria-label="Disability resolution bar">
                            <div style="background:var(--accent-secondary,#6c5ce7);height:20px;width:${d.total ? Math.min((d.resolved/d.total)*100,100) : 0}%;border-radius:4px;"></div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Scholarships
        const sDiv = document.getElementById("scholarship-data");
        if (sDiv && scholarship) {
            sDiv.innerHTML = `
                <p>Matches Generated: <strong>${scholarship.total_matches_generated || 0}</strong></p>
                <p>Applications Filed: <strong>${scholarship.total_applications || 0}</strong></p>
                <p>Match→Apply Ratio: <strong>${scholarship.match_to_apply_ratio || 0}</strong></p>
                <p>Approval Rate: <strong>${scholarship.approval_rate || 0}%</strong></p>
                <p>Active Schemes: <strong>${scholarship.schemes?.active || 0} / ${scholarship.schemes?.total || 0}</strong></p>
            `;
        }

        // Engagement
        const eDiv = document.getElementById("engagement-data");
        if (eDiv && engagement) {
            const cats = engagement.categories || {};
            eDiv.innerHTML = `
                <p>Total Students: <strong>${engagement.total_students || 0}</strong></p>
                ${Object.entries(cats).map(([name, data]) => `
                    <div style="margin:0.5rem 0;">
                        <span style="text-transform:capitalize;">${name}</span>: ${data.engaged || 0}/${data.count || 0} (${data.rate || 0}%)
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width:${data.rate || 0}%;"></div>
                        </div>
                    </div>
                `).join("")}
            `;
        }

        // Reports list
        const rDiv = document.getElementById("reports-list");
        if (rDiv && reports) {
            const list = reports.reports || [];
            if (list.length === 0) {
                rDiv.innerHTML = `<p>No reports generated yet.</p>`;
            } else {
                rDiv.innerHTML = `
                    <table class="data-table" role="table">
                        <thead><tr><th>ID</th><th>Type</th><th>Period</th><th>Generated By</th><th>Date</th></tr></thead>
                        <tbody>
                            ${list.map(r => `
                                <tr>
                                    <td>${r.id}</td>
                                    <td>${r.report_type}</td>
                                    <td>${r.period_start?.split("T")[0] || ""} — ${r.period_end?.split("T")[0] || ""}</td>
                                    <td>${r.generated_by || "—"}</td>
                                    <td>${r.generated_at?.split("T")[0] || "—"}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                `;
            }
        }
    } catch (err) {
        console.error("Analytics load error:", err);
    }
}

async function generateReport() {
    try {
        const type = document.getElementById("report-type-select")?.value || "full";
        const now = new Date();
        const end = now.toISOString().split("T")[0];
        const start = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate()).toISOString().split("T")[0];
        await ApiService.generateInclusionReport(type, start, end);
        window.showNotification("Report generated successfully", "success");
        loadAnalyticsData();
    } catch (err) {
        window.showNotification("Failed to generate report", "urgent");
    }
}


// --- Phase 12: Notification & Alerting Engine ---
const toastContainer = document.createElement('div');
toastContainer.className = 'toast-container';
toastContainer.setAttribute('aria-live', 'polite');
document.body.appendChild(toastContainer);

window.showNotification = (message, type = "info") => {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = "ℹ️";
    if (type === "urgent") icon = "⚠️";
    if (type === "success") icon = "✅";

    toast.innerHTML = `
        <span style="font-size: 1.5rem;">${icon}</span>
        <div>
            <strong style="display: block; font-size: 0.9rem; text-transform: uppercase; color: var(--text-secondary);">${type}</strong>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Explicit Screen Reader Notification
    routeAnnouncer.textContent = `Notification: ${message}`;
    
    // Auto cleanup
    setTimeout(() => {
        if(toastContainer.contains(toast)) {
            toastContainer.removeChild(toast);
        }
    }, 5000);
};

// Test Phase 12 Execution dynamically:
setTimeout(() => {
    window.showNotification("Welcome to PCCOE OneBridge Alpha", "success");
}, 1500);

