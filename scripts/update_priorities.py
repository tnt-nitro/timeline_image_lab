#!/usr/bin/env python3
"""
Update Priorities: Berechnet Prioritäten aus Batch-Reports
Lokal, offline, datengetrieben.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def load_batch_report(report_path):
    """Lädt Batch-Report JSON"""
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rules_backlog(backlog_path):
    """Lädt Rules-Backlog"""
    with open(backlog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_feedback_for_runs(runs_path, run_ids):
    """Lädt alle Feedback-Dateien für gegebene Runs"""
    feedback_items = []
    runs_dir = Path(runs_path)
    
    for run_id in run_ids:
        run_dir = runs_dir / run_id
        annotations_dir = run_dir / "annotations"
        if annotations_dir.exists():
            for feedback_file in sorted(annotations_dir.glob("feedback_v*.json")):
                try:
                    fb = json.loads(feedback_file.read_text(encoding='utf-8'))
                    if 'items' in fb:
                        for item in fb['items']:
                            item['run_id'] = run_id
                            item['version'] = fb.get('version', 0)
                            feedback_items.append(item)
                except Exception as e:
                    print(f"Warning: Could not load {feedback_file}: {e}", file=sys.stderr)
    
    return feedback_items

def map_feedback_to_rules(feedback_items, rules_backlog):
    """Mappt Feedback-Items zu Regeln basierend auf derived_from"""
    rule_scores = defaultdict(lambda: {'score': 0, 'occurrences': 0, 'items': []})
    
    # Erstelle Mapping von derived_from zu rule_id
    derived_to_rules = {}
    for rule in rules_backlog['rules']:
        for derived in rule.get('derived_from', []):
            if derived not in derived_to_rules:
                derived_to_rules[derived] = []
            derived_to_rules[derived].append(rule['rule_id'])
    
    # Scoring-Config (wird später aus rules_priority.json geladen)
    scoring = {'critical': 5, 'major': 3, 'minor': 1}
    
    # Durchlaufe Feedback-Items
    for item in feedback_items:
        item_type = item.get('type', '')
        severity = item.get('severity', 'minor')
        derived_key = f"{item_type}:{severity}"
        
        # Finde zugehörige Regeln
        rule_ids = derived_to_rules.get(derived_key, [])
        
        for rule_id in rule_ids:
            rule_scores[rule_id]['score'] += scoring.get(severity, 1)
            rule_scores[rule_id]['occurrences'] += 1
            rule_scores[rule_id]['items'].append({
                'run_id': item.get('run_id'),
                'version': item.get('version'),
                'area': item.get('area'),
                'severity': severity
            })
    
    return rule_scores

def calculate_priorities(rule_scores, scoring_config):
    """Berechnet Prioritäten aus Scores"""
    priorities = []
    
    for rule_id, data in rule_scores.items():
        score = data['score']
        occurrences = data['occurrences']
        
        # Priorität bestimmen
        if score >= 15 or occurrences >= 5:
            priority = "high"
        elif score >= 6 or occurrences >= 2:
            priority = "medium"
        else:
            priority = "low"
        
        priorities.append({
            'rule_id': rule_id,
            'score': score,
            'occurrences': occurrences,
            'priority': priority
        })
    
    # Sortiere nach Score (absteigend)
    priorities.sort(key=lambda x: x['score'], reverse=True)
    
    return priorities

def main():
    if len(sys.argv) < 2:
        batch_report_path = Path("batch/reports")
        # Finde neuesten Batch-Report
        reports = sorted(batch_report_path.glob("batch_report_v*.json"))
        if not reports:
            print("Error: No batch reports found.", file=sys.stderr)
            sys.exit(1)
        batch_report_path = reports[-1]
    else:
        batch_report_path = Path(sys.argv[1])
    
    if not batch_report_path.exists():
        print(f"Error: Batch report not found: {batch_report_path}", file=sys.stderr)
        sys.exit(1)
    
    backlog_path = Path("rules/rules_backlog.json")
    if not backlog_path.exists():
        print(f"Error: Rules backlog not found: {backlog_path}", file=sys.stderr)
        sys.exit(1)
    
    # Lade Daten
    batch_report = load_batch_report(batch_report_path)
    rules_backlog = load_rules_backlog(backlog_path)
    
    # Extrahiere Run-IDs aus Batch-Report
    run_ids = list(set(r['run_id'] for r in batch_report.get('runs', [])))
    
    # Lade Feedback für diese Runs
    runs_path = "runs"
    feedback_items = load_feedback_for_runs(runs_path, run_ids)
    
    # Mappe Feedback zu Regeln
    rule_scores = map_feedback_to_rules(feedback_items, rules_backlog)
    
    # Lade Scoring-Config (oder verwende Default)
    priority_path = Path("rules/rules_priority.json")
    if priority_path.exists():
        with open(priority_path, 'r', encoding='utf-8') as f:
            priority_data = json.load(f)
            scoring_config = priority_data.get('scoring', {'critical': 5, 'major': 3, 'minor': 1})
    else:
        scoring_config = {'critical': 5, 'major': 3, 'minor': 1}
    
    # Berechne Prioritäten
    priorities = calculate_priorities(rule_scores, scoring_config)
    
    # Aktualisiere rules_priority.json
    priority_data = {
        'scoring': scoring_config,
        'priorities': priorities
    }
    
    priority_path.parent.mkdir(parents=True, exist_ok=True)
    priority_path.write_text(
        json.dumps(priority_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print(f"Priorities updated: {priority_path}")
    print(f"\nTop priorities:")
    for p in priorities[:5]:
        print(f"  {p['rule_id']}: {p['priority']} (score: {p['score']}, occurrences: {p['occurrences']})")

if __name__ == "__main__":
    main()
