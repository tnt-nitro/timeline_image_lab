#!/usr/bin/env python3
"""
Batch Analyze: Mehrere Runs vergleichen, Metriken ableiten
Lokal, offline, keine Netzwerk-Kommunikation.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_config(config_path):
    """Lädt batch_config.json"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_merged_files(runs_path, include_runs):
    """Findet alle merged_v*.json Dateien in den angegebenen Runs"""
    merged_files = []
    runs_dir = Path(runs_path)
    
    if not runs_dir.exists():
        return merged_files
    
    for run_id in include_runs:
        run_dir = runs_dir / run_id
        merged_dir = run_dir / "merged"
        if merged_dir.exists():
            for merged_file in sorted(merged_dir.glob("merged_v*.json")):
                try:
                    data = json.loads(merged_file.read_text(encoding='utf-8'))
                    merged_files.append({
                        'run_id': run_id,
                        'version': data.get('version', 0),
                        'path': str(merged_file),
                        'data': data
                    })
                except Exception as e:
                    print(f"Warning: Could not load {merged_file}: {e}", file=sys.stderr)
    
    return merged_files

def load_feedback(run_id, version, runs_path):
    """Lädt Feedback-Datei für einen Run"""
    feedback_path = Path(runs_path) / run_id / "annotations" / f"feedback_v{version:03d}.json"
    if feedback_path.exists():
        try:
            return json.loads(feedback_path.read_text(encoding='utf-8'))
        except:
            return None
    return None

def aggregate_metrics(merged_files, runs_path):
    """Aggregiert Metriken über alle Runs"""
    metrics = {
        'runs': [],
        'summary': {
            'total_runs': 0,
            'total_iterations': 0,
            'total_issues': 0,
            'critical_total': 0,
            'major_total': 0,
            'minor_total': 0,
            'by_type': defaultdict(int),
            'by_area': defaultdict(int),
            'by_color_meaning': defaultdict(int)
        }
    }
    
    for item in merged_files:
        run_id = item['run_id']
        version = item['version']
        data = item['data']
        
        # Basis-Metriken aus merged.json
        run_metrics = {
            'run_id': run_id,
            'version': version,
            'issues_total': data.get('summary', {}).get('issues_total', 0),
            'critical': data.get('summary', {}).get('critical', 0),
            'major': data.get('summary', {}).get('major', 0),
            'minor': data.get('summary', {}).get('minor', 0),
            'by_type': defaultdict(int),
            'by_area': defaultdict(int),
            'by_color_meaning': defaultdict(int)
        }
        
        # Detaillierte Metriken aus Feedback
        feedback = load_feedback(run_id, version, runs_path)
        if feedback and 'items' in feedback:
            for fb_item in feedback['items']:
                # by_type
                item_type = fb_item.get('type', 'unknown')
                run_metrics['by_type'][item_type] += 1
                metrics['summary']['by_type'][item_type] += 1
                
                # by_area
                area = fb_item.get('area', 'unknown')
                run_metrics['by_area'][area] += 1
                metrics['summary']['by_area'][area] += 1
                
                # by_color_meaning
                ann_ref = fb_item.get('annotation_ref', {})
                meaning = ann_ref.get('meaning', 'unknown')
                if not meaning:
                    color = ann_ref.get('color', 'unknown')
                    meaning_map = {
                        'red': 'error',
                        'green': 'correct',
                        'yellow': 'uncertain',
                        'blue': 'reference'
                    }
                    meaning = meaning_map.get(color, 'unknown')
                run_metrics['by_color_meaning'][meaning] += 1
                metrics['summary']['by_color_meaning'][meaning] += 1
        
        # Konvertiere defaultdict zu dict für JSON
        run_metrics['by_type'] = dict(run_metrics['by_type'])
        run_metrics['by_area'] = dict(run_metrics['by_area'])
        run_metrics['by_color_meaning'] = dict(run_metrics['by_color_meaning'])
        
        metrics['runs'].append(run_metrics)
        
        # Summary aktualisieren
        metrics['summary']['total_runs'] = len(set(m['run_id'] for m in metrics['runs']))
        metrics['summary']['total_iterations'] += 1
        metrics['summary']['total_issues'] += run_metrics['issues_total']
        metrics['summary']['critical_total'] += run_metrics['critical']
        metrics['summary']['major_total'] += run_metrics['major']
        metrics['summary']['minor_total'] += run_metrics['minor']
    
    # Konvertiere defaultdict zu dict
    metrics['summary']['by_type'] = dict(metrics['summary']['by_type'])
    metrics['summary']['by_area'] = dict(metrics['summary']['by_area'])
    metrics['summary']['by_color_meaning'] = dict(metrics['summary']['by_color_meaning'])
    
    return metrics

def generate_html_report(metrics, output_path):
    """Generiert statischen HTML-Report"""
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Batch Report – Timeline Image Lab</title>
  <style>
    body {{ font-family: sans-serif; margin: 20px; background: #f5f5f5; }}
    .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
    h1 {{ color: #333; }}
    .summary {{ background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    .summary h2 {{ margin-top: 0; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
    .summary-item {{ background: white; padding: 10px; border-radius: 4px; }}
    .summary-item strong {{ display: block; color: #666; font-size: 0.9em; }}
    .summary-item span {{ font-size: 1.5em; color: #2196F3; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
    th {{ background: #2196F3; color: white; cursor: pointer; user-select: none; }}
    th:hover {{ background: #1976D2; }}
    tr:hover {{ background: #f5f5f5; }}
    .bar-container {{ width: 100%; background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; }}
    .bar {{ height: 100%; background: linear-gradient(90deg, #f44336, #ff9800, #4CAF50); transition: width 0.3s; }}
    .bar-critical {{ background: #f44336; }}
    .bar-major {{ background: #ff9800; }}
    .bar-minor {{ background: #4CAF50; }}
    .metrics-detail {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 4px; }}
    .metrics-detail h4 {{ margin: 0 0 10px 0; }}
    .metrics-tags {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .tag {{ background: #e0e0e0; padding: 4px 8px; border-radius: 3px; font-size: 0.85em; }}
    .tag strong {{ color: #2196F3; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Batch Report – Timeline Image Lab</h1>
    <p>Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
      <h2>Gesamtübersicht</h2>
      <div class="summary-grid">
        <div class="summary-item">
          <strong>Runs</strong>
          <span>{metrics['summary']['total_runs']}</span>
        </div>
        <div class="summary-item">
          <strong>Iterationen</strong>
          <span>{metrics['summary']['total_iterations']}</span>
        </div>
        <div class="summary-item">
          <strong>Gesamt-Issues</strong>
          <span>{metrics['summary']['total_issues']}</span>
        </div>
        <div class="summary-item">
          <strong>Critical</strong>
          <span style="color: #f44336;">{metrics['summary']['critical_total']}</span>
        </div>
        <div class="summary-item">
          <strong>Major</strong>
          <span style="color: #ff9800;">{metrics['summary']['major_total']}</span>
        </div>
        <div class="summary-item">
          <strong>Minor</strong>
          <span style="color: #4CAF50;">{metrics['summary']['minor_total']}</span>
        </div>
      </div>
    </div>
    
    <h2>Runs im Detail</h2>
    <table id="runsTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Run ID ↕</th>
          <th onclick="sortTable(1)">Version ↕</th>
          <th onclick="sortTable(2)">Total ↕</th>
          <th onclick="sortTable(3)">Critical ↕</th>
          <th onclick="sortTable(4)">Major ↕</th>
          <th onclick="sortTable(5)">Minor ↕</th>
          <th>Verteilung</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
"""
    
    max_issues = max((r['issues_total'] for r in metrics['runs']), default=1)
    
    for run in metrics['runs']:
        total = run['issues_total']
        critical = run['critical']
        major = run['major']
        minor = run['minor']
        
        # Balken für Verteilung
        bar_html = ""
        if total > 0:
            critical_pct = (critical / total) * 100
            major_pct = (major / total) * 100
            minor_pct = (minor / total) * 100
            bar_html = f"""
            <div class="bar-container">
              <div class="bar" style="width: {critical_pct}%; background: #f44336;"></div>
              <div class="bar" style="width: {major_pct}%; background: #ff9800; margin-left: -{critical_pct}%;"></div>
              <div class="bar" style="width: {minor_pct}%; background: #4CAF50; margin-left: -{major_pct}%;"></div>
            </div>
            """
        
        # Details (by_type, by_area)
        details_html = "<div class='metrics-detail'>"
        if run['by_type']:
            details_html += "<h4>By Type:</h4><div class='metrics-tags'>"
            for k, v in sorted(run['by_type'].items()):
                details_html += f"<span class='tag'><strong>{k}:</strong> {v}</span>"
            details_html += "</div>"
        if run['by_area']:
            details_html += "<h4>By Area:</h4><div class='metrics-tags'>"
            for k, v in sorted(run['by_area'].items()):
                details_html += f"<span class='tag'><strong>{k}:</strong> {v}</span>"
            details_html += "</div>"
        details_html += "</div>"
        
        html += f"""
        <tr>
          <td>{run['run_id']}</td>
          <td>{run['version']}</td>
          <td>{total}</td>
          <td style="color: #f44336;">{critical}</td>
          <td style="color: #ff9800;">{major}</td>
          <td style="color: #4CAF50;">{minor}</td>
          <td>{bar_html}</td>
          <td>{details_html}</td>
        </tr>
"""
    
    html += """
      </tbody>
    </table>
    
    <script>
      let sortDirection = {};
      
      function sortTable(column) {
        const table = document.getElementById('runsTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isNumeric = column >= 2 && column <= 5;
        const dir = sortDirection[column] || 'asc';
        
        rows.sort((a, b) => {
          let aVal = a.cells[column].textContent.trim();
          let bVal = b.cells[column].textContent.trim();
          
          if (isNumeric) {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
            return dir === 'asc' ? aVal - bVal : bVal - aVal;
          } else {
            return dir === 'asc' 
              ? aVal.localeCompare(bVal)
              : bVal.localeCompare(aVal);
          }
        });
        
        rows.forEach(row => tbody.appendChild(row));
        sortDirection[column] = dir === 'asc' ? 'desc' : 'asc';
      }
    </script>
  </div>
</body>
</html>
"""
    
    output_path.write_text(html, encoding='utf-8')

def main():
    if len(sys.argv) < 2:
        config_path = Path("batch/batch_config.json")
    else:
        config_path = Path(sys.argv[1])
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    config = load_config(config_path)
    runs_path = config.get('runs_path', 'runs')
    include_runs = config.get('include_runs', [])
    
    # Finde alle merged-Dateien
    merged_files = find_merged_files(runs_path, include_runs)
    
    if not merged_files:
        print("Warning: No merged files found.", file=sys.stderr)
        sys.exit(0)
    
    # Aggregiere Metriken
    metrics = aggregate_metrics(merged_files, runs_path)
    
    # Bestimme Report-Version
    reports_dir = Path("batch/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    existing_reports = sorted(reports_dir.glob("batch_report_v*.json"))
    if existing_reports:
        last_version = int(existing_reports[-1].stem.split("_v")[1])
        version = last_version + 1
    else:
        version = 1
    
    # Schreibe JSON-Report
    json_path = reports_dir / f"batch_report_v{version:03d}.json"
    json_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"JSON report written: {json_path}")
    
    # Generiere HTML-Report
    html_path = reports_dir / f"batch_report_v{version:03d}.html"
    generate_html_report(metrics, html_path)
    print(f"HTML report written: {html_path}")

if __name__ == "__main__":
    main()
