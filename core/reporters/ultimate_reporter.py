"""
Ultimate report generator with stunning graphics - COMPLETE VERSION
"""
import json
import base64
from datetime import datetime
from typing import Dict, List, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import re

class UltimateReporter:
    """Generate beautiful, comprehensive reports"""
    
    def __init__(self, config):
        self.config = config
        
    def generate(self, results: Dict, format: str = 'html') -> str:
        """Generate report in specified format"""
        if format == 'html':
            return self._generate_html(results)
        elif format == 'json':
            return json.dumps(results, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html(self, results: Dict) -> str:
        """Generate stunning HTML report with graphics"""
        
        # Generate charts
        charts = self._generate_charts(results)
        
        # Get counts for different categories
        issue_counts = self._count_issues_by_category(results.get('issues', []))
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> ssec-seo ULTIMATE SEO REPORT - {results.get('domain', 'Unknown')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }}
        
        .report-wrapper {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Header Styles */
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .domain {{
            font-size: 24px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header .date {{
            font-size: 16px;
            opacity: 0.8;
        }}
        
        .print-btn {{
            background: white;
            color: #1e3c72;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        
        .print-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        }}
        
        /* Score Cards */
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .score-card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        
        .score-card:hover {{
            transform: translateY(-5px);
        }}
        
        .score-card h3 {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 15px;
        }}
        
        .score-value {{
            font-size: 64px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .score-label {{
            font-size: 14px;
            opacity: 0.7;
        }}
        
        .critical-score {{ color: #ff6b6b; }}
        .warning-score {{ color: #feca57; }}
        .good-score {{ color: #1dd1a1; }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-item {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        
        /* Charts Container */
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 18px;
        }}
        
        /* Issues Section */
        .issues-section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 24px;
            margin-bottom: 25px;
            color: #333;
            display: flex;
            align-items: center;
        }}
        
        .section-title span {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 14px;
            margin-left: 15px;
        }}
        
        .issue-item {{
            background: #f8f9fa;
            border-left: 4px solid;
            margin-bottom: 15px;
            padding: 20px;
            border-radius: 10px;
            transition: transform 0.2s;
        }}
        
        .issue-item:hover {{
            transform: translateX(5px);
        }}
        
        .issue-critical {{ border-color: #ff6b6b; }}
        .issue-high {{ border-color: #ff9f43; }}
        .issue-medium {{ border-color: #feca57; }}
        .issue-low {{ border-color: #48dbfb; }}
        
        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .issue-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        
        .issue-severity {{
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .severity-critical {{ background: #ff6b6b; color: white; }}
        .severity-high {{ background: #ff9f43; color: white; }}
        .severity-medium {{ background: #feca57; color: #333; }}
        .severity-low {{ background: #48dbfb; color: white; }}
        
        .issue-url {{
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            margin-bottom: 10px;
            display: block;
            word-break: break-all;
        }}
        
        .issue-url:hover {{
            text-decoration: underline;
        }}
        
        .issue-description {{
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }}
        
        /* Recommendations Grid */
        .recommendations-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }}
        
        .recommendation-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 25px;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        
        .recommendation-priority {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .priority-high {{ background: #ff6b6b; }}
        .priority-medium {{ background: #feca57; color: #333; }}
        .priority-low {{ background: #48dbfb; }}
        
        .recommendation-title {{
            font-size: 20px;
            margin-bottom: 10px;
        }}
        
        .recommendation-desc {{
            opacity: 0.9;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        .recommendation-action {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .recommendation-examples {{
            margin-top: 10px;
            font-size: 12px;
            opacity: 0.8;
        }}
        
        /* Subdomains Grid */
        .subdomains-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .subdomain-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #e0e0e0;
        }}
        
        .subdomain-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            word-break: break-all;
        }}
        
        .subdomain-status {{
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 50px;
            display: inline-block;
        }}
        
        .status-active {{ background: #1dd1a1; color: white; }}
        .status-inactive {{ background: #ff6b6b; color: white; }}
        
        /* Exposed Data Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .data-table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            word-break: break-all;
        }}
        
        .data-table tr:hover {{
            background: #f5f5f5;
        }}
        
        /* SSL Info */
        .ssl-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .ssl-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
        }}
        
        .ssl-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .ssl-value {{
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: rgba(255,255,255,0.7);
            font-size: 14px;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .header {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .print-btn {{
                display: none;
            }}
            .score-card {{
                break-inside: avoid;
            }}
        }}
        
        /* Loading Animation */
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
    <div class="report-wrapper" id="report-content">
        <!-- Header -->
        <div class="header">
            <div class="header-content">
                <div>
                    <h1> 🔍 ssec-seo ULTIMATE SEO REPORT </h1>
                    <div class="domain">{results.get('domain', 'N/A')}</div>
                    <div class="date">Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    <div class="date">Target: {results.get('target_url', 'N/A')}</div>
                </div>
                <button class="print-btn" onclick="downloadPDF()" id="pdfBtn">
                    📥 Download PDF Report
                </button>
            </div>
        </div>
        
        <!-- Score Cards -->
        <div class="score-grid">
            <div class="score-card">
                <h3>Overall Score</h3>
                <div class="score-value {self._get_score_class(results.get('summary', {}).get('overall_score', 0))}">
                    {results.get('summary', {}).get('overall_score', 0)}
                </div>
                <div class="score-label">out of 100</div>
            </div>
            <div class="score-card">
                <h3>SEO Score</h3>
                <div class="score-value {self._get_score_class(results.get('summary', {}).get('seo_score', 0))}">
                    {results.get('summary', {}).get('seo_score', 0)}
                </div>
                <div class="score-label">Technical SEO</div>
            </div>
            <div class="score-card">
                <h3>Security Score</h3>
                <div class="score-value {self._get_score_class(results.get('summary', {}).get('security_score', 0))}">
                    {results.get('summary', {}).get('security_score', 0)}
                </div>
                <div class="score-label">Security & SSL</div>
            </div>
            <div class="score-card">
                <h3>Performance Score</h3>
                <div class="score-value {self._get_score_class(results.get('summary', {}).get('performance_score', 0))}">
                    {results.get('summary', {}).get('performance_score', 0)}
                </div>
                <div class="score-label">Speed & Core Web Vitals</div>
            </div>
        </div>
        
        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{results.get('statistics', {}).get('pages_crawled', 0)}</div>
                <div class="stat-label">Pages Crawled</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{results.get('statistics', {}).get('total_issues', 0)}</div>
                <div class="stat-label">Total Issues</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #ff6b6b;">{results.get('statistics', {}).get('critical_issues', 0)}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #ff9f43;">{results.get('statistics', {}).get('high_issues', 0)}</div>
                <div class="stat-label">High</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{results.get('statistics', {}).get('total_time', 0):.2f}s</div>
                <div class="stat-label">Scan Time</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-container">
            <div class="chart-card">
                <h3>Issues by Severity</h3>
                <div id="severityChart" style="height: 300px;"></div>
            </div>
            <div class="chart-card">
                <h3>Issues by Category</h3>
                <div id="categoryChart" style="height: 300px;"></div>
            </div>
            <div class="chart-card">
                <h3>Risk Distribution</h3>
                <div id="riskChart" style="height: 300px;"></div>
            </div>
            <div class="chart-card">
                <h3>Scan Progress</h3>
                <div id="progressChart" style="height: 300px;"></div>
            </div>
        </div>
        
        <!-- Executive Summary -->
        <div class="issues-section">
            <div class="section-title">
                📊 Executive Summary
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 30px;">
                <div>
                    <p style="font-size: 16px; line-height: 1.8; color: #333;">
                        SSEC-SEO scanned <strong>{results.get('statistics', {}).get('pages_crawled', 0)} pages</strong> 
                        on <strong>{results.get('domain', 'N/A')}</strong> and found 
                        <strong style="color: #ff6b6b;">{results.get('statistics', {}).get('critical_issues', 0)} critical</strong>,
                        <strong style="color: #ff9f43;">{results.get('statistics', {}).get('high_issues', 0)} high</strong>,
                        and <strong>{results.get('statistics', {}).get('total_issues', 0)} total issues</strong>.
                        The overall risk level is <strong>{results.get('summary', {}).get('risk_level', 'unknown').upper()}</strong>.
                    </p>
                    <p style="font-size: 16px; line-height: 1.8; color: #333; margin-top: 15px;">
                        <strong>Top Recommendations:</strong>
                    </p>
                    <ul style="margin-left: 20px; color: #666;">
                        {self._get_top_recommendations(results.get('recommendations', []))}
                    </ul>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 15px;">
                    <h4 style="margin-bottom: 15px;">Quick Stats</h4>
                    <table style="width: 100%;">
                        <tr><td>Pages with Issues:</td><td><strong>{self._get_pages_with_issues(results)}%</strong></td></tr>
                        <tr><td>Avg Load Time:</td><td><strong>{self._get_avg_load_time(results)}s</strong></td></tr>
                        <tr><td>SSL Expiry:</td><td><strong class="{self._get_expiry_class(results)}">{self._get_ssl_expiry(results)}</strong></td></tr>
                        <tr><td>Subdomains Found:</td><td><strong>{results.get('subdomains', {}).get('total_found', 0)}</strong></td></tr>
                        <tr><td>Exposed Items:</td><td><strong>{len(results.get('exposed_data', []))}</strong></td></tr>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Critical Issues -->
        {self._render_issues_section(results.get('issues', []), 'critical', '🔴 Critical Issues Found')}
        
        <!-- High Issues -->
        {self._render_issues_section(results.get('issues', []), 'high', '🟠 High Priority Issues')}
        
        <!-- Medium Issues -->
        {self._render_issues_section(results.get('issues', []), 'medium', '🟡 Medium Priority Issues', True)}
        
        <!-- Exposed Data Section -->
        {self._render_exposed_data(results.get('exposed_data', []))}
        
        <!-- Subdomains Section -->
        {self._render_subdomains(results.get('subdomains', {}))}
        
        <!-- SSL Information -->
        {self._render_ssl_info(results.get('ssl', {}))}
        
        <!-- Misconfigurations -->
        {self._render_misconfigurations(results.get('misconfigurations', {}))}
        
        <!-- Recommendations -->
        <div class="issues-section">
            <div class="section-title">
                💡 Actionable Recommendations
            </div>
            <div class="recommendations-grid">
                {self._render_recommendations(results.get('recommendations', []))}
            </div>
        </div>
        
        <!-- Crawled Pages (Summary) -->
        <div class="issues-section">
            <div class="section-title">
                📄 Crawled Pages ({results.get('statistics', {}).get('pages_crawled', 0)})
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Title</th>
                        <th>Load Time</th>
                    </tr>
                </thead>
                <tbody>
                    {self._render_crawled_pages(results.get('crawl', {}).get('pages', [])[:20])}
                </tbody>
            </table>
            {self._get_more_pages_link(results.get('crawl', {}).get('pages', []), 20)}
        </div>
        
        <!-- Footer -->
        <div class="footer">
            Generated by <strong>ssec-seo</strong> v0.1.0 | MIT License | Open Source | By ssecgroup<br>
            <span style="font-size: 12px;">Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
    </div>
    
    <script>
        // Severity Chart Data
        var severityData = {{
            values: [{results.get('summary', {}).get('critical_issues', 0)}, 
                     {results.get('summary', {}).get('high_issues', 0)},
                     {results.get('summary', {}).get('medium_issues', 0)},
                     {results.get('summary', {}).get('low_issues', 0)}],
            labels: ['Critical', 'High', 'Medium', 'Low'],
            type: 'pie',
            marker: {{
                colors: ['#ff6b6b', '#ff9f43', '#feca57', '#48dbfb']
            }},
            textinfo: 'label+percent',
            hoverinfo: 'label+value+percent',
            textposition: 'inside'
        }};
        
        var severityLayout = {{
            height: 300,
            margin: {{ t: 0, b: 0, l: 0, r: 0 }},
            showlegend: true,
            legend: {{ orientation: 'h', y: -0.2 }}
        }};
        
        Plotly.newPlot('severityChart', [severityData], severityLayout);
        
        // Category Chart
        var categoryData = {{
            x: {json.dumps(list(issue_counts.keys()))},
            y: {json.dumps(list(issue_counts.values()))},
            type: 'bar',
            marker: {{
                color: ['#ff6b6b', '#ff9f43', '#feca57', '#48dbfb', '#667eea', '#1dd1a1']
            }}
        }};
        
        var categoryLayout = {{
            height: 300,
            margin: {{ t: 20, b: 50, l: 50, r: 20 }},
            xaxis: {{ 
                title: 'Category',
                tickangle: -45
            }},
            yaxis: {{ 
                title: 'Number of Issues',
                gridcolor: '#e0e0e0'
            }},
            plot_bgcolor: 'white'
        }};
        
        Plotly.newPlot('categoryChart', [categoryData], categoryLayout);
        
        // Risk Distribution Chart
        var riskData = {{
            values: [{results.get('statistics', {}).get('critical_issues', 0)}, 
                     {results.get('statistics', {}).get('high_issues', 0)},
                     {results.get('statistics', {}).get('medium_issues', 0)},
                     {len(results.get('crawl', {}).get('pages', [])) - results.get('statistics', {}).get('total_issues', 0)}],
            labels: ['Critical Risk', 'High Risk', 'Medium Risk', 'Clean Pages'],
            type: 'pie',
            marker: {{
                colors: ['#ff6b6b', '#ff9f43', '#feca57', '#1dd1a1']
            }},
            textinfo: 'label+percent',
            hoverinfo: 'label+value+percent'
        }};
        
        var riskLayout = {{
            height: 300,
            margin: {{ t: 0, b: 0, l: 0, r: 0 }},
            showlegend: true,
            legend: {{ orientation: 'h', y: -0.2 }}
        }};
        
        Plotly.newPlot('riskChart', [riskData], riskLayout);
        
        // Progress Chart
        var progressData = {{
            x: ['Pages', 'Issues', 'Critical', 'Fixed'],
            y: [{results.get('statistics', {}).get('pages_crawled', 0)}, 
                {results.get('statistics', {}).get('total_issues', 0)},
                {results.get('statistics', {}).get('critical_issues', 0)},
                {results.get('statistics', {}).get('total_issues', 0) - results.get('statistics', {}).get('critical_issues', 0)}],
            type: 'bar',
            marker: {{
                color: ['#667eea', '#ff9f43', '#ff6b6b', '#1dd1a1']
            }}
        }};
        
        var progressLayout = {{
            height: 300,
            margin: {{ t: 20, b: 40, l: 50, r: 20 }},
            xaxis: {{ title: 'Category' }},
            yaxis: {{ title: 'Count', gridcolor: '#e0e0e0' }},
            plot_bgcolor: 'white'
        }};
        
        Plotly.newPlot('progressChart', [progressData], progressLayout);
        
        // PDF Download Function with loading indicator
        function downloadPDF() {{
            const btn = document.getElementById('pdfBtn');
            const originalText = btn.innerText;
            btn.innerHTML = '<span class="loading"></span> Generating PDF...';
            btn.disabled = true;
            
            const element = document.getElementById('report-content');
            const opt = {{
                margin:       0.5,
                filename:     'ssec-seo_ultimate_report_{results.get('domain', 'scan')}.pdf',
                image:        {{ type: 'jpeg', quality: 0.98 }},
                html2canvas:  {{ scale: 2, logging: false, dpi: 192, letterRendering: true }},
                jsPDF:        {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
            }};
            
            html2pdf().set(opt).from(element).save().then(() => {{
                btn.innerHTML = originalText;
                btn.disabled = false;
            }});
        }}
    </script>
</body>
</html>
'''
        return html
    
    def _generate_charts(self, results: Dict) -> Dict:
        """Generate base64 encoded charts for PDF"""
        charts = {}
        
        try:
            # Severity Pie Chart
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            severity_counts = [
                results.get('summary', {}).get('critical_issues', 0),
                results.get('summary', {}).get('high_issues', 0),
                results.get('summary', {}).get('medium_issues', 0),
                results.get('summary', {}).get('low_issues', 0)
            ]
            labels = ['Critical', 'High', 'Medium', 'Low']
            colors = ['#ff6b6b', '#ff9f43', '#feca57', '#48dbfb']
            
            if sum(severity_counts) > 0:
                wedges, texts, autotexts = ax1.pie(severity_counts, labels=labels, colors=colors,
                                                   autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')
                plt.setp(autotexts, size=8, weight="bold")
                plt.setp(texts, size=8)
                plt.title('Issues by Severity', pad=20)
                
                # Convert to base64
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                charts['severity'] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
            
            # Category Bar Chart
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            categories = self._count_issues_by_category(results.get('issues', []))
            if categories:
                bars = ax2.bar(categories.keys(), categories.values(), 
                              color=['#ff6b6b', '#ff9f43', '#feca57', '#48dbfb', '#667eea'])
                ax2.set_xlabel('Category')
                ax2.set_ylabel('Number of Issues')
                ax2.set_title('Issues by Category')
                plt.xticks(rotation=45, ha='right')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom')
                
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                charts['categories'] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close()
                
        except Exception as e:
            print(f"Chart generation error: {e}")
        
        return charts
    
    def _count_issues_by_category(self, issues: List) -> Dict:
        """Count issues by category"""
        categories = {}
        for issue in issues:
            category = issue.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _render_issues_section(self, issues: List, severity: str, title: str, collapsible: bool = False) -> str:
        """Render issues section by severity"""
        filtered = [i for i in issues if i.get('severity') == severity]
        if not filtered:
            if severity in ['critical', 'high']:
                return f'''
                <div class="issues-section">
                    <div class="section-title">
                        {title}
                        <span>0</span>
                    </div>
                    <p style="color: #27ae60; padding: 20px;">✅ No {severity} issues found!</p>
                </div>
                '''
            return ''
        
        issues_html = ''
        for issue in filtered[:20]:  # Show top 20
            issues_html += f'''
            <div class="issue-item issue-{severity}">
                <div class="issue-header">
                    <span class="issue-title">{issue.get('title', 'Issue')}</span>
                    <span class="issue-severity severity-{severity}">{severity}</span>
                </div>
                <a href="{issue.get('url', '#')}" class="issue-url" target="_blank">{issue.get('url', '')}</a>
                <div class="issue-description">{issue.get('description', '')}</div>
                {self._render_issue_metadata(issue)}
            </div>
            '''
        
        if len(filtered) > 20:
            issues_html += f'<p style="text-align: center; color: #666;">... and {len(filtered) - 20} more issues</p>'
        
        return f'''
        <div class="issues-section">
            <div class="section-title">
                {title}
                <span>{len(filtered)}</span>
            </div>
            {issues_html}
        </div>
        '''
    
    def _render_issue_metadata(self, issue: Dict) -> str:
        """Render additional issue metadata"""
        metadata = []
        if issue.get('count'):
            metadata.append(f"Count: {issue['count']}")
        if issue.get('element'):
            metadata.append(f"Element: {issue['element']}")
        if issue.get('line'):
            metadata.append(f"Line: {issue['line']}")
        
        if metadata:
            return f'<div style="margin-top: 10px; font-size: 12px; color: #999;">{" | ".join(metadata)}</div>'
        return ''
    
    def _render_exposed_data(self, exposed_data: List) -> str:
        """Render exposed data findings"""
        if not exposed_data:
            return ''
        
        # Group by severity
        critical = [e for e in exposed_data if e.get('severity') == 'critical']
        high = [e for e in exposed_data if e.get('severity') == 'high']
        medium = [e for e in exposed_data if e.get('severity') == 'medium']
        
        html = f'''
        <div class="issues-section">
            <div class="section-title">
                ⚠️ Exposed Sensitive Data
                <span>{len(exposed_data)}</span>
            </div>
            
            <div style="margin-bottom: 20px;">
                <span class="issue-severity severity-critical">Critical: {len(critical)}</span>
                <span class="issue-severity severity-high" style="margin-left: 10px;">High: {len(high)}</span>
                <span class="issue-severity severity-medium" style="margin-left: 10px;">Medium: {len(medium)}</span>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Type</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Sensitive Data</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        for item in exposed_data[:30]:  # Show top 30
            severity_class = {
                'critical': 'severity-critical',
                'high': 'severity-high',
                'medium': 'severity-medium',
                'low': 'severity-low'
            }.get(item.get('severity', 'low'), 'severity-low')
            
            sensitive = ', '.join(item.get('sensitive_data', [])) if item.get('sensitive_data') else 'None detected'
            
            html += f'''
            <tr>
                <td><a href="{item['url']}" target="_blank">{item['url'][:80]}...</a></td>
                <td>{item.get('type', 'unknown')}</td>
                <td><span class="issue-severity {severity_class}">{item.get('severity', 'low')}</span></td>
                <td>{item.get('status', 200)}</td>
                <td>{sensitive}</td>
            </tr>
            '''
        
        html += '''
                </tbody>
            </table>
        </div>
        '''
        return html
    
    def _render_subdomains(self, subdomains: Dict) -> str:
        """Render discovered subdomains"""
        if not subdomains or not subdomains.get('active'):
            return ''
        
        active = subdomains.get('active', [])
        all_found = subdomains.get('subdomains', [])
        
        html = f'''
        <div class="issues-section">
            <div class="section-title">
                🌐 Discovered Subdomains
                <span>{len(active)} active / {len(all_found)} total</span>
            </div>
            
            <div style="margin-bottom: 20px;">
                <p>Found {len(all_found)} subdomains using multiple techniques:</p>
                <ul style="margin-left: 20px; color: #666;">
        '''
        
        for technique, count in subdomains.get('techniques', {}).items():
            html += f'<li>{technique}: {count} found</li>'
        
        html += '''
                </ul>
            </div>
            
            <div class="subdomains-grid">
        '''
        
        for sub in active[:30]:  # Show top 30 active
            status_class = 'status-active' if sub.get('accessible') else 'status-inactive'
            html += f'''
            <div class="subdomain-item">
                <div class="subdomain-name">{sub.get('subdomain', '')}</div>
                <div><span class="subdomain-status {status_class}">
                    {'Active' if sub.get('accessible') else 'Inactive'}
                </span></div>
                <div style="font-size:12px; color:#666; margin-top:5px;">
                    Status: {sub.get('status', 'N/A')}<br>
                    Title: {sub.get('title', 'N/A')[:50]}
                </div>
            </div>
            '''
        
        html += '''
            </div>
        </div>
        '''
        return html
    
    def _render_ssl_info(self, ssl: Dict) -> str:
        """Render SSL information"""
        if not ssl or not ssl.get('certificate'):
            return ''
        
        cert = ssl.get('certificate', {})
        days_left = cert.get('days_until_expiry', 0)
        
        # Determine color based on days left
        expiry_color = 'critical-score' if days_left < 30 else 'warning-score' if days_left < 90 else 'good-score'
        
        html = f'''
        <div class="issues-section">
            <div class="section-title">
                🔒 SSL/TLS Certificate Analysis
            </div>
            
            <div class="ssl-grid">
                <div class="ssl-item">
                    <div class="ssl-label">Issuer</div>
                    <div class="ssl-value">{cert.get('issuer', {}).get('commonName', 'Unknown')}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Subject</div>
                    <div class="ssl-value">{cert.get('subject', {}).get('commonName', 'Unknown')}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Valid From</div>
                    <div class="ssl-value">{cert.get('not_valid_before', 'Unknown')[:10]}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Valid Until</div>
                    <div class="ssl-value">{cert.get('not_valid_after', 'Unknown')[:10]}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Days Until Expiry</div>
                    <div class="ssl-value {expiry_color}">{days_left} days</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Signature Algorithm</div>
                    <div class="ssl-value">{cert.get('signature_algorithm', 'Unknown')}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Serial Number</div>
                    <div class="ssl-value">{cert.get('serial_number', 'Unknown')[-12:]}</div>
                </div>
                <div class="ssl-item">
                    <div class="ssl-label">Version</div>
                    <div class="ssl-value">TLS {cert.get('version', 'Unknown')}</div>
                </div>
            </div>
            
            {self._render_protocols(ssl.get('protocols', {}))}
            {self._render_vulnerabilities(ssl.get('vulnerabilities', []))}
        </div>
        '''
        return html
    
    def _render_protocols(self, protocols: Dict) -> str:
        """Render supported protocols"""
        if not protocols:
            return ''
        
        html = '''
        <div style="margin-top: 20px;">
            <h4 style="margin-bottom: 15px;">Supported Protocols</h4>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        '''
        
        for protocol, supported in protocols.items():
            color = '#1dd1a1' if supported else '#ff6b6b'
            html += f'''
            <span style="background: {color}; color: white; padding: 5px 15px; border-radius: 50px; font-size: 12px;">
                {protocol} {'✅' if supported else '❌'}
            </span>
            '''
        
        html += '''
            </div>
        </div>
        '''
        return html
    
    def _render_vulnerabilities(self, vulnerabilities: List) -> str:
        """Render SSL vulnerabilities"""
        if not vulnerabilities:
            return ''
        
        html = '''
        <div style="margin-top: 20px;">
            <h4 style="margin-bottom: 15px;">⚠️ Vulnerabilities Detected</h4>
        '''
        
        for vuln in vulnerabilities:
            severity_class = {
                'critical': 'severity-critical',
                'high': 'severity-high',
                'medium': 'severity-medium',
                'low': 'severity-low'
            }.get(vuln.get('severity', 'medium'), 'severity-medium')
            
            html += f'''
            <div class="issue-item issue-{vuln.get('severity', 'medium')}">
                <div class="issue-header">
                    <span class="issue-title">{vuln.get('name', 'Unknown')}</span>
                    <span class="issue-severity {severity_class}">{vuln.get('severity', 'medium')}</span>
                </div>
                <div class="issue-description">{vuln.get('description', '')}</div>
                <div style="margin-top: 10px; font-size: 12px;">CVE: {vuln.get('cve', 'N/A')}</div>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def _render_misconfigurations(self, misconfig: Dict) -> str:
        """Render HTTP misconfigurations"""
        if not misconfig:
            return ''
        
        exposed = misconfig.get('exposed_paths', [])
        methods = misconfig.get('methods_allowed', {})
        directory_listing = misconfig.get('directory_listing', [])
        security_issues = misconfig.get('security_issues', [])
        
        if not any([exposed, methods, directory_listing, security_issues]):
            return ''
        
        html = f'''
        <div class="issues-section">
            <div class="section-title">
                ⚙️ HTTP Misconfigurations
            </div>
        '''
        
        # HTTP Methods
        if methods:
            allowed = [m for m, info in methods.items() if info.get('allowed')]
            if allowed:
                html += f'''
                <div style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">Allowed HTTP Methods</h4>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                '''
                for method in allowed:
                    color = '#ff6b6b' if method in ['PUT', 'DELETE', 'TRACE'] else '#1dd1a1'
                    html += f'<span style="background: {color}; color: white; padding: 5px 15px; border-radius: 50px;">{method}</span>'
                html += '</div></div>'
        
        # Security Issues
        if security_issues:
            html += '''
            <div style="margin-bottom: 20px;">
                <h4 style="margin-bottom: 10px;">Security Header Issues</h4>
            '''
            for issue in security_issues:
                severity_class = {
                    'critical': 'severity-critical',
                    'high': 'severity-high',
                    'medium': 'severity-medium',
                    'low': 'severity-low'
                }.get(issue.get('severity', 'medium'), 'severity-medium')
                
                html += f'''
                <div class="issue-item issue-{issue.get('severity', 'medium')}">
                    <div class="issue-header">
                        <span class="issue-title">{issue.get('header', 'Unknown')}</span>
                        <span class="issue-severity {severity_class}">{issue.get('severity', 'medium')}</span>
                    </div>
                    <div class="issue-description">{issue.get('description', '')}</div>
                </div>
                '''
            html += '</div>'
        
        # Directory Listing
        if directory_listing:
            html += '''
            <div style="margin-bottom: 20px;">
                <h4 style="margin-bottom: 10px;">Directory Listing Enabled</h4>
                <ul style="margin-left: 20px;">
            '''
            for dir in directory_listing:
                html += f'<li><a href="{dir.get("url")}" target="_blank">{dir.get("url")}</a></li>'
            html += '</ul></div>'
        
        html += '</div>'
        return html
    
    def _render_recommendations(self, recommendations: List) -> str:
        """Render recommendations"""
        if not recommendations:
            return '<p>No recommendations available at this time.</p>'
        
        html = ''
        for rec in recommendations[:6]:  # Show top 6
            priority_class = {
                'high': 'priority-high',
                'medium': 'priority-medium',
                'low': 'priority-low'
            }.get(rec.get('priority', 'medium'), 'priority-medium')
            
            examples_html = ''
            if rec.get('examples'):
                examples = '<br>'.join([f'• {ex}' for ex in rec['examples'][:3]])
                examples_html = f'<div class="recommendation-examples">{examples}</div>'
            
            html += f'''
            <div class="recommendation-card">
                <span class="recommendation-priority {priority_class}">{rec.get('priority', 'medium').upper()}</span>
                <div class="recommendation-title">{rec.get('title', '')}</div>
                <div class="recommendation-desc">{rec.get('description', '')}</div>
                <div class="recommendation-action">
                    <strong>Action:</strong> {rec.get('action', '')}
                </div>
                {examples_html}
            </div>
            '''
        return html
    
    def _render_crawled_pages(self, pages: List) -> str:
        """Render crawled pages summary"""
        if not pages:
            return '<tr><td colspan="4" style="text-align: center;">No pages crawled</td></tr>'
        
        html = ''
        for page in pages[:20]:
            status_color = '#27ae60' if page.get('status_code', 0) == 200 else '#e74c3c'
            html += f'''
            <tr>
                <td><a href="{page.get('url', '#')}" target="_blank">{page.get('url', '')[:80]}...</a></td>
                <td style="color: {status_color};">{page.get('status_code', 'N/A')}</td>
                <td>{page.get('title', 'N/A')[:60]}</td>
                <td>{page.get('load_time', 0):.2f}s</td>
            </tr>
            '''
        return html
    
    def _get_more_pages_link(self, pages: List, shown: int) -> str:
        """Get link to show more pages"""
        if len(pages) > shown:
            return f'<p style="text-align: center; margin-top: 10px;"><a href="#" onclick="alert(\'Full list in JSON export\')">... and {len(pages) - shown} more pages</a></p>'
        return ''
    
    def _get_top_recommendations(self, recommendations: List) -> str:
        """Get top 3 recommendations as list items"""
        if not recommendations:
            return '<li>No recommendations available</li>'
        
        html = ''
        for rec in recommendations[:3]:
            html += f'<li><strong>{rec.get("title", "")}:</strong> {rec.get("description", "")[:100]}...</li>'
        return html
    
    def _get_pages_with_issues(self, results: Dict) -> int:
        """Calculate percentage of pages with issues"""
        total_pages = results.get('statistics', {}).get('pages_crawled', 0)
        if total_pages == 0:
            return 0
        issues_count = results.get('statistics', {}).get('total_issues', 0)
        return min(100, int((issues_count / total_pages) * 100))
    
    def _get_avg_load_time(self, results: Dict) -> float:
        """Calculate average load time"""
        pages = results.get('crawl', {}).get('pages', [])
        if not pages:
            return 0.0
        times = [p.get('load_time', 0) for p in pages if p.get('load_time')]
        if not times:
            return 0.0
        return round(sum(times) / len(times), 2)
    
    def _get_ssl_expiry(self, results: Dict) -> str:
        """Get SSL expiry status"""
        ssl = results.get('ssl', {})
        cert = ssl.get('certificate', {})
        days = cert.get('days_until_expiry', 365)
        
        if days < 0:
            return 'Expired'
        elif days < 30:
            return f'Expires in {days} days'
        elif days < 90:
            return f'Expires in {days} days'
        else:
            return f'Valid ({days} days)'
    
    def _get_expiry_class(self, results: Dict) -> str:
        """Get CSS class for SSL expiry"""
        ssl = results.get('ssl', {})
        cert = ssl.get('certificate', {})
        days = cert.get('days_until_expiry', 365)
        
        if days < 30:
            return 'critical-score'
        elif days < 90:
            return 'warning-score'
        else:
            return 'good-score'
    
    def _get_score_class(self, score: int) -> str:
        """Get CSS class based on score"""
        if score >= 80:
            return 'good-score'
        elif score >= 50:
            return 'warning-score'
        else:
            return 'critical-score'
