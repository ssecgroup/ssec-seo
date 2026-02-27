"""
HTML Report Generator with built-in PDF export
"""
from datetime import datetime
from typing import List, Dict
import json

class HTMLReportGenerator:
    """Generate beautiful HTML reports"""
    
    def __init__(self):
        self.template = ""
        
    def generate(self, scan_results: Dict) -> str:
        """Generate HTML report from scan results"""
        
        # Count issues by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in scan_results.get('issues', []):
            sev = issue.get('severity', 'low')
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 SPYGLASS SEO Report by https://github/ssecgroup - {scan_results.get('target_url', '')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .print-btn {{
            background: white;
            color: #1e3c72;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .print-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .card h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .card .value {{
            font-size: 48px;
            font-weight: bold;
        }}
        
        .critical {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .good {{ color: #27ae60; }}
        
        .section {{
            padding: 30px;
            border-top: 1px solid #ecf0f1;
        }}
        
        .section h2 {{
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        
        .issue-list {{
            list-style: none;
        }}
        
        .issue-item {{
            background: #f8f9fa;
            border-left: 4px solid;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .issue-critical {{ border-color: #e74c3c; }}
        .issue-high {{ border-color: #e67e22; }}
        .issue-medium {{ border-color: #f1c40f; }}
        .issue-low {{ border-color: #3498db; }}
        
        .severity-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .badge-critical {{ background: #e74c3c; color: white; }}
        .badge-high {{ background: #e67e22; color: white; }}
        .badge-medium {{ background: #f1c40f; color: black; }}
        .badge-low {{ background: #3498db; color: white; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .print-btn {{ display: none; }}
            .header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>
    <div class="report-container" id="report-content">
        <div class="header">
            <div>
                <h1>🔍 SPYGLASS SEO Report by https://github/ssecgroup </h1>
                <p>Target: {scan_results.get('target_url', 'N/A')}</p>
                <p>Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <button class="print-btn" onclick="downloadPDF()">
                📥 Download PDF Report
            </button>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Overall Score</h3>
                <div class="value {self._get_score_class(scan_results.get('overall_score', 0))}">
                    {scan_results.get('overall_score', 0)}/100
                </div>
            </div>
            <div class="card">
                <h3>Pages Scanned</h3>
                <div class="value">{scan_results.get('pages_scanned', 0)}</div>
            </div>
            <div class="card">
                <h3>Critical Issues</h3>
                <div class="value critical">{severity_counts['critical']}</div>
            </div>
            <div class="card">
                <h3>Dead Links</h3>
                <div class="value warning">{len(scan_results.get('dead_links', []))}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔴 Critical Issues Found</h2>
            {self._render_issues(scan_results.get('issues', []), 'critical')}
        </div>
        
        <div class="section">
            <h2>⚠️ High Priority Issues</h2>
            {self._render_issues(scan_results.get('issues', []), 'high')}
        </div>
        
        <div class="section">
            <h2>📊 Scan Details</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Pages</td>
                    <td>{scan_results.get('pages_scanned', 0)}</td>
                </tr>
                <tr>
                    <td>Average Load Time</td>
                    <td>{self._avg_load_time(scan_results):.2f}s</td>
                </tr>
                <tr>
                    <td>Total Issues</td>
                    <td>{len(scan_results.get('issues', []))}</td>
                </tr>
            </table>
        </div>
    </div>
    
    <script>
        function downloadPDF() {{
            const element = document.getElementById('report-content');
            const opt = {{
                margin:       1,
                filename:     'spyglass_report_{scan_results.get('target_domain', 'scan')}.pdf',
                image:        {{ type: 'jpeg', quality: 0.98 }},
                html2canvas:  {{ scale: 2 }},
                jsPDF:        {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
            }};
            html2pdf().set(opt).from(element).save();
        }}
    </script>
</body>
</html>
'''
        return html
    
    def _render_issues(self, issues: List, severity: str) -> str:
        """Render issues by severity"""
        filtered = [i for i in issues if i.get('severity') == severity]
        if not filtered:
            return '<p>No issues found ✓</p>'
        
        html = '<ul class="issue-list">'
        for issue in filtered[:10]:
            html += f'''
            <li class="issue-item issue-{severity}">
                <strong>{issue.get('title', 'Issue')}</strong><br>
                {issue.get('description', '')}<br>
                <small>URL: {issue.get('url', 'N/A')}</small>
                <span class="severity-badge badge-{severity}">{severity}</span>
            </li>
            '''
        html += '</ul>'
        return html
    
    def _get_score_class(self, score: int) -> str:
        """Get CSS class based on score"""
        if score >= 80: return 'good'
        if score >= 50: return 'warning'
        return 'critical'
    
    def _avg_load_time(self, results: Dict) -> float:
        """Calculate average load time"""
        # This would come from actual scan results
        return 0.5
