// Configuration
const API_BASE = 'https://ssec-seo.vercel.app';

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

let currentUrl = '';

// Initialize
document.addEventListener('DOMContentLoaded', scanCurrentTab);
rescanButtonEl.addEventListener('click', scanCurrentTab);

async function scanCurrentTab() {
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
        hideLoading();
        
    } catch (error) {
        console.error('Scan error:', error);
        showError('Scan failed: ' + error.message);
    }
}

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
    // Score
    const score = data.score || 0;
    scoreNumberEl.textContent = score;
    scoreCircleEl.style.background = getScoreColor(score);
    
    // Risk level
    const riskLevel = data.risk_level || 'Unknown';
    riskBadgeEl.textContent = riskLevel.toUpperCase();
    riskBadgeEl.className = `risk-badge risk-${riskLevel.toLowerCase()}`;
    
    // Stats
    pagesScannedEl.textContent = data.pages_scanned || 0;
    criticalIssuesEl.textContent = data.critical_issues || 0;
    highIssuesEl.textContent = data.high_issues || 0;
    totalIssuesEl.textContent = data.total_issues || 0;
    
    // Issues
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