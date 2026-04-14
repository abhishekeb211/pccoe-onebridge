/*
 * PCCOE OneBridge - API Service Module
 * Centralized fetch wrapper with auth, error handling, and base URL config.
 */

const IS_GITHUB_PAGES = window.location.hostname.includes('github.io') || window.location.protocol === 'file:';
const REPO_NAME = 'pccoe-onebridge'; // Repository name for subdirectory hosting

// Detect correct base path for static assets
const getBasePath = () => {
    if (IS_GITHUB_PAGES && window.location.hostname.includes('github.io')) {
        return `/${REPO_NAME}/`;
    }
    return './';
};

const BASE_PATH = getBasePath();
const API_BASE_URL = IS_GITHUB_PAGES ? '' : "http://localhost:8000";

const ApiService = {
    _token: null,

    setToken(token) {
        this._token = token;
    },

    getToken() {
        return this._token;
    },

    async fetchJSON(endpoint, options = {}) {
        if (IS_GITHUB_PAGES) {
            // In static mode, we intercept and throw a specific 'static' error 
            // that app.js can catch to provide mock fallbacks.
            const error = new Error('API unavailable in static mode');
            error.isStatic = true;
            throw error;
        }
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...options.headers,
        };

        if (this._token) {
            headers["Authorization"] = `Bearer ${this._token}`;
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const error = new Error(errorData.detail || `Request failed (${response.status})`);
                error.status = response.status;
                throw error;
            }

            return await response.json();
        } catch (err) {
            if (err.status || err.isStatic) throw err;
            throw new Error("Network error. Is the backend running?");
        }
    },

    // --- Auth ---
    async login(username, password) {
        if (IS_GITHUB_PAGES) {
            // Transparently handle login in static mode
            return { access_token: 'demo-token', token_type: 'bearer' };
        }
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Login failed");
        }

        const data = await response.json();
        this.setToken(data.access_token);
        return data;
    },

    // --- Tickets ---
    async submitTicket(description, studentPrn) {
        return this.fetchJSON("/api/v1/tickets", {
            method: "POST",
            body: JSON.stringify({ description, student_prn: studentPrn }),
        });
    },

    async getStudentTickets(studentPrn) {
        return this.fetchJSON(`/api/v1/tickets/${encodeURIComponent(studentPrn)}`);
    },

    // --- Opportunities ---
    async getOpportunities(studentPrn) {
        return this.fetchJSON(`/api/v1/opportunities/matches?student_prn=${encodeURIComponent(studentPrn)}`);
    },

    // --- Facilities ---
    async getFacilities() {
        return this.fetchJSON("/api/v1/facilities");
    },

    async bookFacility(studentPrn, facilityName, bookingTime, accessibilityOverride = false) {
        return this.fetchJSON("/api/v1/facilities/book", {
            method: "POST",
            body: JSON.stringify({
                student_prn: studentPrn,
                facility_name: facilityName,
                booking_time: bookingTime,
                accessibility_override: accessibilityOverride,
            }),
        });
    },

    // --- EOC ---
    async submitGrievance(description, studentPrn, category = "grievance") {
        return this.fetchJSON("/api/v1/eoc/secure-grievance", {
            method: "POST",
            body: JSON.stringify({
                description,
                student_prn: studentPrn,
                category,
            }),
        });
    },

    // --- Health ---
    async checkHealth() {
        return this.fetchJSON("/health");
    },

    // --- Profile ---
    async getMyProfile() {
        return this.fetchJSON("/auth/me");
    },

    // --- Dashboard ---
    async getDashboardSnapshot() {
        return this.fetchJSON("/api/v1/dashboard/snapshot");
    },

    // --- Notifications ---
    async getNotifications() {
        return this.fetchJSON("/api/v1/notifications");
    },

    async markNotificationRead(notificationId) {
        return this.fetchJSON(`/api/v1/notifications/${notificationId}/read`, {
            method: "POST",
        });
    },

    // --- AI Assist ---
    async aiAssist(query, context = "student_assist") {
        return this.fetchJSON("/api/v1/ai/assist", {
            method: "POST",
            body: JSON.stringify({ query, context }),
        });
    },

    async aiUsageStats() {
        return this.fetchJSON("/api/v1/ai/usage");
    },

    // --- Ticket Detail & Status ---
    async getTicketDetail(ticketId) {
        return this.fetchJSON(`/api/v1/tickets/detail/${ticketId}`);
    },

    async updateTicketStatus(ticketId, targetStatus, reason = "") {
        return this.fetchJSON(`/api/v1/tickets/${ticketId}/status`, {
            method: "PUT",
            body: JSON.stringify({ target_status: targetStatus, reason }),
        });
    },

    // --- File Upload ---
    async uploadTicketAttachment(ticketId, file) {
        const formData = new FormData();
        formData.append("file", file);

        const url = `${API_BASE_URL}/api/v1/tickets/${ticketId}/attachments`;
        const headers = {};
        if (this._token) {
            headers["Authorization"] = `Bearer ${this._token}`;
        }

        const response = await fetch(url, {
            method: "POST",
            headers,
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Upload failed");
        }

        return await response.json();
    },

    // --- Phase 21: Knowledge Base ---
    async searchKB(query) {
        return this.fetchJSON(`/api/v1/kb/search?q=${encodeURIComponent(query)}`);
    },

    async getKBCategories() {
        return this.fetchJSON("/api/v1/kb/categories");
    },

    async getKBArticle(articleId) {
        return this.fetchJSON(`/api/v1/kb/articles/${articleId}`);
    },

    async createKBArticle(title, content, category, tags = "") {
        return this.fetchJSON("/api/v1/kb/articles", {
            method: "POST",
            body: JSON.stringify({ title, content, category, tags }),
        });
    },

    // --- Phase 22: Chatbot ---
    async createChatSession() {
        return this.fetchJSON("/api/v1/chat/sessions", { method: "POST" });
    },

    async sendChatMessage(sessionId, message) {
        return this.fetchJSON(`/api/v1/chat/sessions/${sessionId}/messages`, {
            method: "POST",
            body: JSON.stringify({ message }),
        });
    },

    async getChatHistory(sessionId) {
        return this.fetchJSON(`/api/v1/chat/sessions/${sessionId}`);
    },

    // --- Phase 23: Escalation ---
    async triggerEscalation(conversationId = null, reason = "student_request") {
        return this.fetchJSON("/api/v1/escalations/trigger", {
            method: "POST",
            body: JSON.stringify({ conversation_id: conversationId, reason }),
        });
    },

    async getEscalationQueue() {
        return this.fetchJSON("/api/v1/escalations/queue");
    },

    async assignEscalation(escalationId) {
        return this.fetchJSON(`/api/v1/escalations/${escalationId}/assign`, { method: "PUT" });
    },

    async resolveEscalation(escalationId) {
        return this.fetchJSON(`/api/v1/escalations/${escalationId}/resolve`, { method: "PUT" });
    },

    async getEscalationContext(escalationId) {
        return this.fetchJSON(`/api/v1/escalations/${escalationId}/context`);
    },

    // --- Phase 24: Scholarships ---
    async getScholarshipSchemes() {
        return this.fetchJSON("/api/v1/scholarships/schemes");
    },

    async createScholarshipScheme(data) {
        return this.fetchJSON("/api/v1/scholarships/schemes", {
            method: "POST",
            body: JSON.stringify(data),
        });
    },

    async getEligibleScholarships() {
        return this.fetchJSON("/api/v1/scholarships/eligible");
    },

    async getEligibilityProfile() {
        return this.fetchJSON("/api/v1/scholarships/eligibility");
    },

    async updateEligibilityProfile(data) {
        return this.fetchJSON("/api/v1/scholarships/eligibility", {
            method: "POST",
            body: JSON.stringify(data),
        });
    },

    // --- Phase 25: AI Profile Matcher ---
    async getAIMatches() {
        return this.fetchJSON("/api/v1/opportunities/ai-matches");
    },

    async getMatchHistory() {
        return this.fetchJSON("/api/v1/matches/history");
    },

    // --- Phase 26: Application Tracker ---
    async createApplication(opportunityId, opportunityType, opportunityTitle, deadline = null) {
        return this.fetchJSON("/api/v1/applications", {
            method: "POST",
            body: JSON.stringify({
                opportunity_id: opportunityId,
                opportunity_type: opportunityType,
                opportunity_title: opportunityTitle,
                deadline,
            }),
        });
    },

    async getMyApplications() {
        return this.fetchJSON("/api/v1/applications/mine");
    },

    async updateApplicationStatus(applicationId, status) {
        return this.fetchJSON(`/api/v1/applications/${applicationId}/status`, {
            method: "PUT",
            body: JSON.stringify({ status }),
        });
    },

    async getApplicationDocuments(applicationId) {
        return this.fetchJSON(`/api/v1/applications/${applicationId}/documents`);
    },

    async uploadApplicationDocument(applicationId, file, docType = "general") {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("doc_type", docType);

        const url = `${API_BASE_URL}/api/v1/applications/${applicationId}/documents`;
        const headers = {};
        if (this._token) {
            headers["Authorization"] = `Bearer ${this._token}`;
        }

        const response = await fetch(url, {
            method: "POST",
            headers,
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Upload failed");
        }
        return await response.json();
    },

    // --- Phase 27: Career Inventory ---
    async getCareerInventory(branch = null, year = null, listingType = null) {
        const params = new URLSearchParams();
        if (branch) params.append("branch", branch);
        if (year) params.append("year", year);
        if (listingType) params.append("listing_type", listingType);
        const qs = params.toString();
        return this.fetchJSON(`/api/v1/careers/inventory${qs ? "?" + qs : ""}`);
    },

    async getRecommendedCareers() {
        return this.fetchJSON("/api/v1/careers/recommended");
    },

    // --- Phase 28: Readiness Scorer ---
    async scoreReadiness(documentText, documentType = "resume", opportunityTitle = null) {
        return this.fetchJSON("/api/v1/readiness/score", {
            method: "POST",
            body: JSON.stringify({
                document_text: documentText,
                document_type: documentType,
                opportunity_title: opportunityTitle,
            }),
        });
    },

    async getReadinessHistory() {
        return this.fetchJSON("/api/v1/readiness/history");
    },

    // --- Phase 29: Faculty Approval ---
    async requestEndorsement(applicationId, facultyPrn) {
        return this.fetchJSON("/api/v1/endorsements/request", {
            method: "POST",
            body: JSON.stringify({ application_id: applicationId, faculty_prn: facultyPrn }),
        });
    },

    async getPendingEndorsements() {
        return this.fetchJSON("/api/v1/endorsements/pending");
    },

    async actOnEndorsement(endorsementId, status, remarks = null) {
        return this.fetchJSON(`/api/v1/endorsements/${endorsementId}/act`, {
            method: "PUT",
            body: JSON.stringify({ status, remarks }),
        });
    },

    async getMyEndorsements() {
        return this.fetchJSON("/api/v1/endorsements/mine");
    },

    // --- Phase 30: Resource Inventory ---
    async getCampusResources(resourceType = null, building = null, accessibleOnly = false) {
        const params = new URLSearchParams();
        if (resourceType) params.append("resource_type", resourceType);
        if (building) params.append("building", building);
        if (accessibleOnly) params.append("accessible_only", "true");
        const qs = params.toString();
        return this.fetchJSON(`/api/v1/resources${qs ? "?" + qs : ""}`);
    },

    async getResourceDetail(resourceId) {
        return this.fetchJSON(`/api/v1/resources/${resourceId}`);
    },

    // --- Phase 31: Booking Engine ---
    async bookResource(resourceId, bookingDate, startTime, endTime, purpose = null) {
        return this.fetchJSON("/api/v1/resources/book", {
            method: "POST",
            body: JSON.stringify({
                resource_id: resourceId,
                booking_date: bookingDate,
                start_time: startTime,
                end_time: endTime,
                purpose,
            }),
        });
    },

    async getResourceBookings(resourceId, date = null) {
        const qs = date ? `?date=${date}` : "";
        return this.fetchJSON(`/api/v1/resources/${resourceId}/bookings${qs}`);
    },

    async cancelBooking(bookingId) {
        return this.fetchJSON(`/api/v1/bookings/${bookingId}`, { method: "DELETE" });
    },

    async getMyBookings() {
        return this.fetchJSON("/api/v1/bookings/mine");
    },

    // --- Phase 32: Confidential Mode ---
    async submitConfidentialGrievance(category, description, isAnonymous = false) {
        return this.fetchJSON("/api/v1/confidential/grievance", {
            method: "POST",
            body: JSON.stringify({ category, description, is_anonymous: isAnonymous }),
        });
    },

    async getConfidentialQueue() {
        return this.fetchJSON("/api/v1/confidential/queue");
    },

    async resolveConfidentialGrievance(grievanceId) {
        return this.fetchJSON(`/api/v1/confidential/${grievanceId}/resolve`, { method: "PUT" });
    },

    async getMyConfidentialGrievances() {
        return this.fetchJSON("/api/v1/confidential/mine");
    },

    // --- Phase 33: Disability Request Protocol ---
    async submitDisabilityRequest(requestType, description = null, location = null, urgency = "high") {
        return this.fetchJSON("/api/v1/disability/request", {
            method: "POST",
            body: JSON.stringify({ request_type: requestType, description, location, urgency }),
        });
    },

    async getDisabilityQueue() {
        return this.fetchJSON("/api/v1/disability/queue");
    },

    async updateDisabilityRequestStatus(requestId, status) {
        return this.fetchJSON(`/api/v1/disability/${requestId}/status?status=${status}`, { method: "PUT" });
    },

    async getMyDisabilityRequests() {
        return this.fetchJSON("/api/v1/disability/mine");
    },

    // --- Phase 34: Accessibility Overlays ---
    async createAccessibilityAlert(resourceId, alertType, description = null) {
        return this.fetchJSON("/api/v1/accessibility/alerts", {
            method: "POST",
            body: JSON.stringify({ resource_id: resourceId, alert_type: alertType, description }),
        });
    },

    async getAccessibilityAlerts(resourceId = null) {
        const qs = resourceId ? `?resource_id=${resourceId}` : "";
        return this.fetchJSON(`/api/v1/accessibility/alerts${qs}`);
    },

    async deactivateAccessibilityAlert(alertId) {
        return this.fetchJSON(`/api/v1/accessibility/alerts/${alertId}`, { method: "DELETE" });
    },

    async getResourceAccessibility(resourceId) {
        return this.fetchJSON(`/api/v1/resources/${resourceId}/accessibility`);
    },

    // --- Phase 35: Accessibility Audits ---
    async submitAuditResult(pageOrView, auditType, status, findings = null) {
        return this.fetchJSON("/api/v1/accessibility/audits", {
            method: "POST",
            body: JSON.stringify({ page_or_view: pageOrView, audit_type: auditType, status, findings }),
        });
    },

    async getAuditResults(page = null, auditType = null) {
        const params = new URLSearchParams();
        if (page) params.append("page", page);
        if (auditType) params.append("audit_type", auditType);
        const qs = params.toString();
        return this.fetchJSON(`/api/v1/accessibility/audits${qs ? "?" + qs : ""}`);
    },

    async getAuditOverview() {
        return this.fetchJSON("/api/v1/accessibility/audits/overview");
    },

    // --- Phase 36: Admin Portal ---
    async getAdminDashboard() {
        return this.fetchJSON("/api/v1/admin/dashboard");
    },

    async getAdminStudents(branch = null, year = null, hasDisability = null, limit = 100, offset = 0) {
        const params = new URLSearchParams();
        if (branch) params.append("branch", branch);
        if (year) params.append("year", year);
        if (hasDisability !== null) params.append("has_disability", hasDisability);
        params.append("limit", limit);
        params.append("offset", offset);
        return this.fetchJSON(`/api/v1/admin/students?${params.toString()}`);
    },

    async getAdminTickets(status = null, limit = 100, offset = 0) {
        const params = new URLSearchParams();
        if (status) params.append("status", status);
        params.append("limit", limit);
        params.append("offset", offset);
        return this.fetchJSON(`/api/v1/admin/tickets?${params.toString()}`);
    },

    async exportStudentsCSV() {
        return this.fetchJSON("/api/v1/admin/export/students");
    },

    // --- Phase 37: Inclusion Analytics ---
    async getGrievanceAnalytics() {
        return this.fetchJSON("/api/v1/analytics/inclusion/grievances");
    },

    async getScholarshipAnalytics() {
        return this.fetchJSON("/api/v1/analytics/inclusion/scholarships");
    },

    async getEngagementAnalytics() {
        return this.fetchJSON("/api/v1/analytics/inclusion/engagement");
    },

    async generateInclusionReport(reportType, periodStart, periodEnd) {
        const params = new URLSearchParams();
        params.append("report_type", reportType);
        params.append("period_start", periodStart);
        params.append("period_end", periodEnd);
        return this.fetchJSON(`/api/v1/analytics/inclusion/reports?${params.toString()}`, { method: "POST" });
    },

    async getInclusionReports(reportType = null) {
        const params = new URLSearchParams();
        if (reportType) params.append("report_type", reportType);
        const qs = params.toString();
        return this.fetchJSON(`/api/v1/analytics/inclusion/reports${qs ? "?" + qs : ""}`);
    },

    // --- Phase 38: Integration Testing ---
    async createTestRun(scenarioName, stepsTotal = 1) {
        const params = new URLSearchParams();
        params.append("scenario_name", scenarioName);
        params.append("steps_total", stepsTotal);
        return this.fetchJSON(`/api/v1/testing/integration/run?${params.toString()}`, { method: "POST" });
    },

    async completeTestRun(runId, status, stepsPassed = 0, errorDetails = null) {
        const params = new URLSearchParams();
        params.append("status", status);
        params.append("steps_passed", stepsPassed);
        if (errorDetails) params.append("error_details", errorDetails);
        return this.fetchJSON(`/api/v1/testing/integration/${runId}/complete?${params.toString()}`, { method: "PUT" });
    },

    async getTestResults(status = null, limit = 50) {
        const params = new URLSearchParams();
        if (status) params.append("status", status);
        params.append("limit", limit);
        return this.fetchJSON(`/api/v1/testing/integration/results?${params.toString()}`);
    },

    async getTestScenarios() {
        return this.fetchJSON("/api/v1/testing/integration/scenarios");
    },

    // --- Phase 39: Security Hardening ---
    async logSecurityEvent(eventType, severity = "medium", details = null) {
        const params = new URLSearchParams();
        params.append("event_type", eventType);
        params.append("severity", severity);
        if (details) params.append("details", details);
        return this.fetchJSON(`/api/v1/security/events?${params.toString()}`, { method: "POST" });
    },

    async getSecurityEvents(eventType = null, severity = null, limit = 100) {
        const params = new URLSearchParams();
        if (eventType) params.append("event_type", eventType);
        if (severity) params.append("severity", severity);
        params.append("limit", limit);
        return this.fetchJSON(`/api/v1/security/events?${params.toString()}`);
    },

    async getSecurityConfig() {
        return this.fetchJSON("/api/v1/security/config");
    },

    async getSecurityStats() {
        return this.fetchJSON("/api/v1/security/stats");
    },

    // --- Phase 40: Staging Launch ---
    async createDeployment(version, environment, releaseNotes = null) {
        const params = new URLSearchParams();
        params.append("version", version);
        params.append("environment", environment);
        if (releaseNotes) params.append("release_notes", releaseNotes);
        return this.fetchJSON(`/api/v1/deployments?${params.toString()}`, { method: "POST" });
    },

    async updateDeploymentStatus(deploymentId, status, healthStatus = "unknown") {
        const params = new URLSearchParams();
        params.append("status", status);
        params.append("health_status", healthStatus);
        return this.fetchJSON(`/api/v1/deployments/${deploymentId}/status?${params.toString()}`, { method: "PUT" });
    },

    async getDeployments(environment = null, limit = 20) {
        const params = new URLSearchParams();
        if (environment) params.append("environment", environment);
        params.append("limit", limit);
        return this.fetchJSON(`/api/v1/deployments?${params.toString()}`);
    },

    async getSystemHealth() {
        return this.fetchJSON("/api/v1/system/health");
    },

    async getSystemReadiness() {
        return this.fetchJSON("/api/v1/system/readiness");
    },

    // --- Scraped Real Data ---
    async getScrapedScholarships() {
        if (IS_GITHUB_PAGES) {
            // Load pre-scraped snapshot for static deployment
            const resp = await fetch(`${BASE_PATH}scraped_data/snapshot_scholarships.json`);
            if (!resp.ok) throw new Error('Snapshot not available');
            return resp.json();
        }
        return this.fetchJSON("/api/v1/scraped/scholarships");
    },

    async getScrapedInternships() {
        if (IS_GITHUB_PAGES) {
            const resp = await fetch(`${BASE_PATH}scraped_data/snapshot_internships.json`);
            if (!resp.ok) throw new Error('Snapshot not available');
            return resp.json();
        }
        return this.fetchJSON("/api/v1/scraped/internships");
    },

    async getScrapedStatus() {
        return this.fetchJSON("/api/v1/scraped/status");
    },
};
