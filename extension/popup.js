// Configuration
const API_BASE = 'https://ssec-seo.vercel.app';

// ===== FREE TIER WITH 24-HOUR COOLDOWN =====
const STORAGE_KEY = 'ssec_seo_free_tier';

class FreeTierManager {
    constructor() {
        this.data = this.load();
    }
    
    load() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (!stored) {
            return {
                scansUsed: 0,
                maxScans: 5,
                firstScanDate: null,
                lastResetDate: new Date().toISOString(),
                fingerprint: this.generateFingerprint()
            };
        }
        const data = JSON.parse(stored);
        
        // Check if 24 hours have passed since last reset
        if (data.lastResetDate) {
            const lastReset = new Date(data.lastResetDate);
            const now = new Date();
            const hoursSinceReset = (now - lastReset) / (1000 * 60 * 60);
            
            if (hoursSinceReset >= 24) {
                data.scansUsed = 0;
                data.lastResetDate = now.toISOString();
            }
        }
        
        return data;
    }
    
    save() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
    }
    
    generateFingerprint() {
        const components = [
            navigator.userAgent,
            navigator.language,
            screen.colorDepth,
            screen.width + 'x' + screen.height,
            new Date().getTimezoneOffset()
        ];
        return this.hash(components.join('###'));
    }
    
    hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash.toString(36);
    }
    
    getStatus() {
        const now = new Date();
        const lastReset = new Date(this.data.lastResetDate);
        const nextReset = new Date(lastReset.getTime() + 24 * 60 * 60 * 1000);
        const hoursRemaining = Math.max(0, (nextReset - now) / (1000 * 60 * 60));
        
        return {
            scansRemaining: Math.max(0, this.data.maxScans - this.data.scansUsed),
            maxScans: this.data.maxScans,
            scansUsed: this.data.scansUsed,
            nextReset: nextReset.toISOString(),
            hoursRemaining: hoursRemaining,
            canScan: this.data.scansUsed < this.data.maxScans
        };
    }
    
    canScan() {
        return this.data.scansUsed < this.data.maxScans;
    }
    
    useScan() {
        if (this.data.scansUsed >= this.data.maxScans) {
            throw new Error('No scans remaining');
        }
        this.data.scansUsed++;
        if (!this.data.firstScanDate) {
            this.data.firstScanDate = new Date().toISOString();
        }
        this.save();
        return this.getStatus();
    }
    
    getTimeUntilReset() {
        const lastReset = new Date(this.data.lastResetDate);
        const nextReset = new Date(lastReset.getTime() + 24 * 60 * 60 * 1000);
        const now = new Date();
        const msRemaining = nextReset - now;
        
        if (msRemaining <= 0) {
            this.data.scansUsed = 0;
            this.data.lastResetDate = now.toISOString();
            this.save();
            return 0;
        }
        
        return msRemaining;
    }
    
    formatTimeRemaining(ms) {
        if (ms <= 0) return '0 minutes';
        const hours = Math.floor(ms / (1000 * 60 * 60));
        const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes} minutes`;
    }
}

const freeTier = new FreeTierManager();

// DOM Elements
const loadingEl = document.getElementById('loading');
const contentEl = document.getElementById('content');
const urlDisplayEl = document.getElementById('urlDisplay');
const scoreNumberEl = document.getElementById('scoreNumber');
const scoreCircleEl = document.getElementById('scoreCircle');
const riskBadgeEl = document.getElementById('riskBadge');
const pagesScannedEl = document.getElementById('pagesScanned');
const criticalIssuesEl = document.getElementById('criticalIssues');
const highIssuesEl = document.getElementById('highIssues');
const totalIssuesEl = document.getElementById('totalIssues');
const issuesListEl = document.getElementById('issuesList');
const fullReportLinkEl = document.getElementById('fullReportLink');
const rescanButtonEl = document.getElementById('rescanButton');

// Free tier UI elements (add these IDs to popup.html)
const scansRemainingEl = document.getElementById('scansRemaining');
const outOfScansPanel = document.getElementById('outOfScansPanel');
const scanResultsArea = document.getElementById('scanResultsArea');
const timeRemainingDisplay = document.getElementById('timeRemainingDisplay');

let currentUrl = '';
let timerInterval = null;

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    updateScansDisplay();
    checkAndShowScansStatus();
    scanCurrentTab();
});

rescanButtonEl.addEventListener('click', () => {
    if (!freeTier.canScan()) {
        showOutOfScans();
        return;
    }
    scanCurrentTab();
});

// ===== Free Tier UI Functions =====
function updateScansDisplay() {
    const status = freeTier.getStatus();
    if (scansRemainingEl) {
        scansRemainingEl.textContent = `${status.scansRemaining}/${status.maxScans}`;
    }
}

function checkAndShowScansStatus() {
    if (!freeTier.canScan()) {
        showOutOfScans();
    } else {
        hideOutOfScans();
    }
}

function showOutOfScans() {
    if (scanResultsArea) scanResultsArea.style.display = 'none';
    if (outOfScansPanel) outOfScansPanel.style.display = 'block';
    if (fullReportLinkEl) fullReportLinkEl.style.display = 'none';
    if (rescanButtonEl) rescanButtonEl.style.display = 'none';
    
    updateTimeRemaining();
    
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const ms = freeTier.getTimeUntilReset();
        if (ms <= 0) {
            clearInterval(timerInterval);
            hideOutOfScans();
            updateScansDisplay();
        } else {
            if (timeRemainingDisplay) {
                timeRemainingDisplay.textContent = freeTier.formatTimeRemaining(ms);
            }
        }
    }, 60000);
}

function hideOutOfScans() {
    if (scanResultsArea) scanResultsArea.style.display = 'block';
    if (outOfScansPanel) outOfScansPanel.style.display = 'none';
    if (fullReportLinkEl) fullReportLinkEl.style.display = 'block';
    if (rescanButtonEl) rescanButtonEl.style.display = 'block';
}

function updateTimeRemaining() {
    const ms = freeTier.getTimeUntilReset();
    if (timeRemainingDisplay) {
        timeRemainingDisplay.textContent = freeTier.formatTimeRemaining(ms);
    }
}

// ===== Modified Scan Function =====
async function scanCurrentTab() {
    // Check free tier first
    if (!freeTier.canScan()) {
        showOutOfScans();
        return;
    }
    
    try {
        showLoading();
        
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab || !tab.url) {
            showError('Cannot access current tab');
            return;
        }
        
        if (tab.url.startsWith('chrome://') || tab.url.startsWith('extension://')) {
            showError('Cannot scan browser internal pages');
            return;
        }
        
        currentUrl = tab.url;
        urlDisplayEl.textContent = currentUrl;
        fullReportLinkEl.href = `${API_BASE}/?url=${encodeURIComponent(currentUrl)}`;
        
        const data = await performScan(currentUrl);
        displayResults(data);
        
        // Use a scan from free tier
        freeTier.useScan();
        updateScansDisplay();
        
        hideLoading();
        
    } catch (error) {
        console.error('Scan error:', error);
        showError('Scan failed: ' + error.message);
    }
}

// ===== Existing Functions (Unchanged) =====
async function performScan(url) {
    const response = await fetch(`${API_BASE}/api/scan?url=${encodeURIComponent(url)}`);
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.error) {
        throw new Error(data.error);
    }
    
    return data;
}

function displayResults(data) {
    const score = data.score || 0;
    scoreNumberEl.textContent = score;
    scoreCircleEl.style.background = getScoreColor(score);
    
    const riskLevel = data.risk_level || 'Unknown';
    riskBadgeEl.textContent = riskLevel.toUpperCase();
    riskBadgeEl.className = `risk-badge risk-${riskLevel.toLowerCase()}`;
    
    pagesScannedEl.textContent = data.pages_scanned || 0;
    criticalIssuesEl.textContent = data.critical_issues || 0;
    highIssuesEl.textContent = data.high_issues || 0;
    totalIssuesEl.textContent = data.total_issues || 0;
    
    displayIssues(data);
}

function displayIssues(data) {
    const issues = [];
    
    if (data.critical_issues > 0) {
        issues.push({ severity: 'critical', message: `${data.critical_issues} critical issue(s) found` });
    }
    if (data.high_issues > 0) {
        issues.push({ severity: 'high', message: `${data.high_issues} high severity issue(s) found` });
    }
    if (data.medium_issues > 0) {
        issues.push({ severity: 'medium', message: `${data.medium_issues} medium severity issue(s) found` });
    }
    if (data.low_issues > 0) {
        issues.push({ severity: 'low', message: `${data.low_issues} low severity issue(s) found` });
    }
    
    if (issues.length === 0) {
        issuesListEl.innerHTML = '<div style="text-align: center; opacity: 0.7; padding: 8px;">✨ No issues found!</div>';
        return;
    }
    
    const icons = { critical: '🔴', high: '🟠', medium: '🟡', low: '🔵' };
    
    issuesListEl.innerHTML = issues.map(issue => `
        <div class="issue-item issue-${issue.severity}">
            <strong>${icons[issue.severity]} ${issue.severity.toUpperCase()}:</strong> ${issue.message}
        </div>
    `).join('');
}

function getScoreColor(score) {
    if (score >= 80) return '#28a745';
    if (score >= 60) return '#ffc107';
    if (score >= 40) return '#fd7e14';
    return '#dc3545';
}

function showLoading() {
    loadingEl.style.display = 'block';
    contentEl.style.display = 'none';
}

function hideLoading() {
    loadingEl.style.display = 'none';
    contentEl.style.display = 'block';
}

function showError(message) {
    hideLoading();
    urlDisplayEl.textContent = 'Error';
    scoreNumberEl.textContent = '!';
    riskBadgeEl.textContent = 'ERROR';
    issuesListEl.innerHTML = `<div class="issue-item issue-critical">❌ ${message}</div>`;
}