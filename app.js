// Sentry Frontend Error Monitoring (replace DSN with your Sentry project DSN)
if (window.Sentry === undefined) {
    const script = document.createElement('script');
    script.src = 'https://browser.sentry-cdn.com/10.49.0/bundle.tracing.replay.min.js';
    script.crossOrigin = 'anonymous';
    script.onload = () => {
        Sentry.init({
            dsn: 'https://your-frontend-dsn@sentry.io/project-id', // TODO: Replace with real DSN
            integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
            tracesSampleRate: 0.1,
            replaysSessionSampleRate: 0.05,
            replaysOnErrorSampleRate: 1.0,
        });
    };
    document.head.appendChild(script);
}
document.addEventListener("DOMContentLoaded", () => {
    // State
    let curatedData = {};
    let liveScholarships = [];
    let liveInternships = [];
    let notifications = [];
    let activeTab = "beyond-limits";
    let searchQuery = "";
    let achieverFilter = "all";

    // DOM Elements
    const mainTabs = document.querySelectorAll(".main-tab");
    const tabContents = document.querySelectorAll(".tab-content");
    const globalSearch = document.getElementById("global-search");
    const hofFilters = document.getElementById("hof-filters");
    const searchInfoBar = document.getElementById("search-info-bar");
    const searchInfoText = document.getElementById("search-info-text");
    const btnSwitchTab = document.getElementById("btn-switch-tab");
    const tabGlider = document.getElementById("tab-glider");

    // Grids
    const achieverGrid = document.getElementById("achiever-grid");
    const legendsGrid = document.getElementById("legends-grid");
    const staticScholarshipsGrid = document.getElementById("static-scholarships-grid");
    const sFeed = document.getElementById("scholarships-feed");
    const iFeed = document.getElementById("internships-feed");
    const skillsGrid = document.getElementById("skills-grid");
    const platformsGrid = document.getElementById("platforms-grid");
    const roadmapContainer = document.getElementById("roadmap-timeline");

    // Project Roadmap Data
    const roadmapData = [
        {
            part: "Part 1",
            title: "Architecture Design",
            phases: "Requirement Crystallization & AI Strategy Selection",
        },
        { part: "Part 3", title: "User Identity", phases: "Unified Student Profile & RBAC System" },
        {
            part: "Part 4",
            title: "AI Subsystem",
            phases: "Local Agent Initialization & Gemini API Integration",
        },
        {
            part: "Part 7",
            title: "Scholarships Module",
            phases: "AI Profile Matcher & Application Tracker",
        },
        {
            part: "Part 8",
            title: "Professional Hub",
            phases: "Career Inventory & Readiness Scorer",
        },
        {
            part: "Part 10",
            title: "Accessibility Layer",
            phases: "Confidential Subsystems & Disability Protocol",
        },
        { part: "Part 12", title: "Go-Live", phases: "Hardening, Testing & Staging Launch" },
    ];

    // Fetch Data with Year Support
    const getCurrentYear = () => {
        const d = new Date();
        return d.getFullYear();
    };

    // Set to true to use mock/test data
    const USE_TEST_DATA = false; // Change to true for development/testing

    const fetchData = async () => {
        renderSkeletons();
        const year = getCurrentYear();
        let scholarshipsPath = `data/${year}/scholarships.json`;
        let studentsPath = `data/${year}/students.json`;
        let testScholarshipsPath = "data/test/scholarships.json";
        let testStudentsPath = "data/test/students.json";
        // Fallback to root if not found
        const fetchWithFallback = async (path, fallback) => {
            try {
                const res = await fetch(path);
                if (res.ok) return res.json();
                throw new Error("Not found");
            } catch {
                return fetch(fallback)
                    .then((r) => r.json())
                    .catch(() => []);
            }
        };
        try {
            let curatedRes, sRes, iRes, nRes;
            if (USE_TEST_DATA) {
                [curatedRes, sRes, iRes, nRes] = await Promise.all([
                    fetch("data/curated_content.json").then((r) => r.json()),
                    fetch(testScholarshipsPath)
                        .then((r) => r.json())
                        .catch(() => []),
                    fetch("data/internships.json")
                        .then((r) => r.json())
                        .catch(() => []),
                    fetch("data/notifications.json")
                        .then((r) => r.json())
                        .catch(() => []),
                ]);
            } else {
                [curatedRes, sRes, iRes, nRes] = await Promise.all([
                    fetch("data/curated_content.json").then((r) => r.json()),
                    fetchWithFallback(scholarshipsPath, "data/scholarships.json"),
                    fetch("data/internships.json")
                        .then((r) => r.json())
                        .catch(() => []),
                    fetch("data/notifications.json")
                        .then((r) => r.json())
                        .catch(() => []),
                ]);
            }

            curatedData = curatedRes;
            liveScholarships = sRes;
            liveInternships = iRes;
            notifications = nRes;

            setTimeout(() => {
                init();
                updateTabGlider();
            }, 1200);
        } catch (error) {
            showToast({
                title: "Data Load Error",
                message: "There was a problem loading data. Please try again or contact support.",
            });
        }
    };

    const init = () => {
        renderAllGrids();
        setupFilters();
        renderRoadmap();
        renderDailyInsight();
        initPulseSystem();
        initGliderResizeHandler();
    };

    // UI Polish: Skeletons
    const renderSkeletons = () => {
        const skeletonHtml = Array(4).fill('<div class="skeleton-card skeleton"></div>').join("");
        achieverGrid.innerHTML = skeletonHtml;
        staticScholarshipsGrid.innerHTML = skeletonHtml;
        platformsGrid.innerHTML = skeletonHtml;
        sFeed.innerHTML = "";
        iFeed.innerHTML = "";
    };

    // UI Polish: Tab Glider
    const updateTabGlider = () => {
        const activeTabEl = document.querySelector(".main-tab.active");
        if (!activeTabEl || !tabGlider) return;

        tabGlider.style.width = `${activeTabEl.offsetWidth}px`;
        tabGlider.style.left = `${activeTabEl.offsetLeft}px`;
    };

    const initGliderResizeHandler = () => {
        window.addEventListener("resize", updateTabGlider);
    };

    // Intelligence Layer: Daily Insight
    const renderDailyInsight = () => {
        const insights = curatedData.motivational_insights || [];
        if (insights.length === 0) return;
        const randomInsight = insights[Math.floor(Math.random() * insights.length)];
        const target = document.getElementById("daily-insight-text");
        if (target) {
            target.innerHTML = `"${randomInsight.text}" — <strong>${randomInsight.author}</strong>`;
        }
    };

    // Global Render Handler
    const renderAllGrids = () => {
        const counts = {
            "beyond-limits": renderHallOfFame(),
            "learn-grow": renderScholarships(),
            "hire-me": renderHireMe(),
        };
        handleSearchFeedback(counts);
    };

    const handleSearchFeedback = (counts) => {
        const q = searchQuery.trim();
        if (!q) {
            searchInfoBar.classList.remove("active");
            return;
        }
        const currentCount = counts[activeTab];
        if (currentCount > 0) {
            searchInfoBar.classList.remove("active");
        } else {
            const otherTabs = Object.keys(counts).filter((t) => t !== activeTab && counts[t] > 0);
            if (otherTabs.length > 0) {
                const targetTab = otherTabs[0];
                const targetLabel = document
                    .querySelector(`[data-tab="${targetTab}"]`)
                    .textContent.trim();
                searchInfoText.textContent = `No matches in this section. Found results in "${targetLabel}".`;
                searchInfoBar.classList.add("active");
                btnSwitchTab.onclick = () => switchTab(targetTab);
            } else {
                searchInfoText.textContent = `No matches found anywhere for "${q}".`;
                searchInfoBar.classList.add("active");
            }
        }
    };

    const switchTab = (tabId) => {
        const tabEl = document.querySelector(`[data-tab="${tabId}"]`);
        if (tabEl) {
            tabEl.click();
            window.scrollTo({ top: searchInfoBar.offsetTop - 20, behavior: "smooth" });
        }
    };

    const renderHallOfFame = () => {
        const q = searchQuery.toLowerCase();
        const year = getCurrentYear();
        const nextYear = year + 1;
        // Show achievers for current and next year
        const filteredAchievers = curatedData.achievers.filter((a) => {
            const matchesSearch =
                a.name.toLowerCase().includes(q) || a.achievement.toLowerCase().includes(q);
            const matchesCategory = achieverFilter === "all" || a.category === achieverFilter;
            const matchesYear =
                a.year == year ||
                a.year == nextYear ||
                a.year == String(year) ||
                a.year == String(nextYear);
            return matchesSearch && matchesCategory && matchesYear;
        });

        achieverGrid.innerHTML = filteredAchievers
            .map(
                (a) => `
            <div class="achiever-card animate">
                <div class="achiever-header">
                    <i class="fa-solid ${a.icon} fa-2x" style="color: var(--accent-primary);"></i>
                    <div>
                        <div class="achiever-name">${a.name}</div>
                        <div class="disability-badge">${a.disability}</div>
                    </div>
                </div>
                <p class="achiever-desc">${a.achievement}</p>
                <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">
                    ${a.category} • Batch ${a.year}
                </div>
            </div>
        `,
            )
            .join("");

        // Legends: always show all, or filter by year if needed
        const filteredLegends = curatedData.legends.filter(
            (l) => l.name.toLowerCase().includes(q) || l.achievement.toLowerCase().includes(q),
        );
        legendsGrid.innerHTML = filteredLegends
            .map(
                (l) => `
            <div class="achiever-card glass animate">
                <div class="achiever-header">
                    <i class="fa-solid ${l.icon} fa-2x" style="color: var(--accent-tertiary);"></i>
                    <div>
                        <div class="achiever-name" style="color: var(--accent-secondary);">${l.name}</div>
                        <div class="disability-badge">${l.disability}</div>
                    </div>
                </div>
                <p class="achiever-desc">${l.achievement}</p>
            </div>
        `,
            )
            .join("");

        return filteredAchievers.length + filteredLegends.length;
    };

    const renderScholarships = () => {
        const q = searchQuery.toLowerCase();
        const filteredStatic = curatedData.featured_scholarships.filter(
            (s) => s.name.toLowerCase().includes(q) || s.provider.toLowerCase().includes(q),
        );
        staticScholarshipsGrid.innerHTML = filteredStatic
            .map(
                (s) => `
            <div class="resource-card animate">
                <div class="opp-type">${s.category}</div>
                <div class="resource-title">${s.name}</div>
                <p class="resource-info">${s.eligibility}</p>
                <div style="font-weight: 600; color: var(--accent-secondary); margin-bottom: 0.5rem;">${s.benefit}</div>
                <span class="resource-tag">${s.provider}</span>
            </div>
        `,
            )
            .join("");

        const filteredLive = liveScholarships.filter(
            (s) => s.name.toLowerCase().includes(q) || s.provider.toLowerCase().includes(q),
        );
        sFeed.innerHTML = filteredLive
            .slice(0, 8)
            .map((s) => renderLiveCard(s, "scholarship"))
            .join("");

        skillsGrid.innerHTML = curatedData.skill_pathways
            .map((skill) => {
                const randomProgress = Math.floor(Math.random() * 60) + 20; // 20-80%
                return `
                <div class="resource-card glass animate">
                    <div class="opp-type">${skill.tag}</div>
                    <div class="resource-title">${skill.category}</div>
                    <p class="resource-info">${skill.details}</p>
                    <div class="skill-progress-container">
                        <div class="progress-label">
                            <span>Profile Match</span>
                            <span>${randomProgress}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${randomProgress}%"></div>
                        </div>
                    </div>
                    <span class="resource-tag" style="margin-top: 1rem; display: inline-block;">${skill.platform}</span>
                </div>
            `;
            })
            .join("");

        return filteredStatic.length + filteredLive.length;
    };

    const renderHireMe = () => {
        const q = searchQuery.toLowerCase();
        const filteredPlatforms = curatedData.platforms.filter(
            (p) => p.name.toLowerCase().includes(q) || p.details.toLowerCase().includes(q),
        );
        platformsGrid.innerHTML = filteredPlatforms
            .map(
                (p) => `
            <div class="resource-card animate">
                <div class="opp-type">${p.tag}</div>
                <div class="resource-title">${p.name}</div>
                <p class="resource-info">${p.details}</p>
            </div>
        `,
            )
            .join("");

        const filteredInterns = liveInternships.filter(
            (i) => i.title.toLowerCase().includes(q) || i.company.toLowerCase().includes(q),
        );
        iFeed.innerHTML = filteredInterns
            .slice(0, 8)
            .map((i) => {
                const randomScore = Math.floor(Math.random() * 15) + 85;
                return `
                <div class="opp-card animate">
                    <div class="compat-badge">
                        <i class="fa-solid fa-bolt"></i> AI Score: ${randomScore}%
                    </div>
                    <div class="opp-type">${i.branch || "General"}</div>
                    <h3 class="opp-title">${i.title || "Dynamic Opportunity"}</h3>
                    <div class="opp-company">
                        <i class="fa-solid fa-building"></i> ${i.company || "Corporate Partner"}
                    </div>
                    <div class="opp-footer">
                        <a href="${i.link || "#"}" target="_blank" class="btn-link" onclick="celebrateClick(event)">Apply Now <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
                    </div>
                </div>
            `;
            })
            .join("");

        return filteredPlatforms.length + filteredInterns.length;
    };

    const renderLiveCard = (item, type) => {
        const isSchol = type === "scholarship";
        return `
            <div class="opp-card animate">
                <div class="opp-type">${isSchol ? item.category || "General" : item.branch || "General"}</div>
                <h3 class="opp-title">${isSchol ? item.name || "Scholarship Opportunity" : item.title || "Live Role"}</h3>
                <div class="opp-company">
                    <i class="fa-solid ${isSchol ? "fa-building-columns" : "fa-building"}"></i>
                    ${isSchol ? item.provider || "State/Central Agency" : item.company || "Industry Partner"}
                </div>
                <div class="opp-footer">
                    <a href="${item.link || "#"}" target="_blank" class="btn-link" onclick="celebrateClick(event)">Details <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
                </div>
            </div>
        `;
    };

    window.celebrateClick = (e) => {
        console.log("Insight: Student taking action toward goal.");
        // We could add confetti here if a library was present
    };

    const renderRoadmap = () => {
        roadmapContainer.innerHTML = roadmapData
            .map(
                (item, idx) => `
            <div class="timeline-item animate" style="animation-delay: ${idx * 0.1}s">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-part">${item.part}</div>
                    <h4 style="margin-bottom: 0.5rem;">${item.title}</h4>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">${item.phases}</p>
                </div>
            </div>
        `,
            )
            .join("");
    };

    const setupFilters = () => {
        const categories = [...new Set(curatedData.achievers.map((a) => a.category))];
        hofFilters.innerHTML =
            '<div class="chip active" data-filter="all">All Achievers</div>' +
            categories
                .map(
                    (cat) =>
                        `<div class="chip" data-filter="${cat}">${cat.charAt(0).toUpperCase() + cat.slice(1)}</div>`,
                )
                .join("");
        hofFilters.querySelectorAll(".chip").forEach((chip) => {
            chip.addEventListener("click", () => {
                hofFilters.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
                chip.classList.add("active");
                achieverFilter = chip.dataset.filter;
                renderHallOfFame();
            });
        });
    };

    globalSearch.addEventListener("input", (e) => {
        searchQuery = e.target.value;
        renderAllGrids();
    });

    mainTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.getAttribute("data-tab");
            mainTabs.forEach((t) => {
                t.classList.remove("active");
                t.setAttribute("aria-selected", "false");
            });
            tab.classList.add("active");
            tab.setAttribute("aria-selected", "true");
            tabContents.forEach((content) => {
                content.classList.remove("active");
                if (content.id === target) content.classList.add("active");
            });
            activeTab = target;
            updateTabGlider();
            renderAllGrids();
            tab.focus();
        });
        tab.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                tab.click();
            }
            // Arrow key navigation
            if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
                e.preventDefault();
                const tabsArr = Array.from(mainTabs);
                const idx = tabsArr.indexOf(tab);
                let nextIdx = e.key === "ArrowRight" ? idx + 1 : idx - 1;
                if (nextIdx < 0) nextIdx = tabsArr.length - 1;
                if (nextIdx >= tabsArr.length) nextIdx = 0;
                tabsArr[nextIdx].focus();
            }
        });
    });

    // Pulse Notifications
    const initPulseSystem = () => {
        const toast = document.getElementById("notification-toast");
        const closeBtn = document.getElementById("close-toast");
        const pulseBadge = document.querySelector(".pulse-badge");
        if (pulseBadge) pulseBadge.textContent = notifications.length;
        setTimeout(() => {
            if (notifications.length > 0) {
                const notif = notifications[Math.floor(Math.random() * notifications.length)];
                showToast(notif);
            }
        }, 5000);
        if (closeBtn) closeBtn.onclick = () => toast.classList.remove("active");
    };

    const showToast = (notif) => {
        const toast = document.getElementById("notification-toast");
        const title = document.getElementById("toast-title");
        const msg = document.getElementById("toast-message");
        if (!toast || !title || !msg) return;
        title.textContent = notif.title || 'Notification';
        msg.textContent = notif.message || '';
        toast.classList.add("active");
        setTimeout(() => toast.classList.remove("active"), 10000);
    };

    const a11yToggle = document.getElementById("a11y-toggle");
    a11yToggle.addEventListener("click", () => {
        document.body.classList.toggle("high-contrast");
        a11yToggle.focus();
    });
    a11yToggle.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            a11yToggle.click();
        }
    });

    const supportToggle = document.getElementById("support-toggle");
    const supportModal = document.getElementById("support-modal");
    const closeModal = document.querySelector(".close-modal");
    if (supportToggle) {
        supportToggle.addEventListener("click", () => {
            supportModal.classList.add("active");
            supportModal.querySelector("input, textarea, button").focus();
        });
        supportToggle.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                supportToggle.click();
            }
        });
    }
    if (closeModal)
        closeModal.addEventListener("click", () => supportModal.classList.remove("active"));

    // Accessibility Feedback Modal Logic
    const a11yFeedbackToggle = document.getElementById("a11y-feedback-toggle");
    const a11yFeedbackModal = document.getElementById("a11y-feedback-modal");
    const closeA11yFeedback = document.getElementById("close-a11y-feedback");
    const a11yFeedbackForm = document.getElementById("a11y-feedback-form");
    const a11yFeedbackStatus = document.getElementById("a11y-feedback-status");

    if (a11yFeedbackToggle && a11yFeedbackModal) {
        a11yFeedbackToggle.addEventListener("click", () => {
            a11yFeedbackModal.classList.add("active");
            a11yFeedbackModal.querySelector("textarea,button").focus();
        });
        a11yFeedbackToggle.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                a11yFeedbackToggle.click();
            }
        });
    }
    if (closeA11yFeedback)
        closeA11yFeedback.addEventListener("click", () =>
            a11yFeedbackModal.classList.remove("active"),
        );

    if (a11yFeedbackForm) {
        a11yFeedbackForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const desc = document.getElementById("a11y-feedback-desc").value.trim();
            if (desc.length < 5) return;
            // Save feedback to localStorage (could be sent to backend in production)
            let feedbacks = JSON.parse(localStorage.getItem("a11y_feedbacks") || "[]");
            feedbacks.push({ desc, date: new Date().toISOString() });
            localStorage.setItem("a11y_feedbacks", JSON.stringify(feedbacks));
            a11yFeedbackForm.style.display = "none";
            a11yFeedbackStatus.style.display = "block";
            setTimeout(() => {
                a11yFeedbackModal.classList.remove("active");
                a11yFeedbackForm.style.display = "";
                a11yFeedbackStatus.style.display = "none";
                a11yFeedbackForm.reset();
            }, 2500);
        });
    }

    fetchData();

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) entry.target.classList.add("animate");
            });
        },
        { threshold: 0.1 },
    );

    setTimeout(() => {
        document.querySelectorAll(".animate").forEach((el) => observer.observe(el));
    }, 2000);
});
