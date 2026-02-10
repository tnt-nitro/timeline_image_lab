#!/usr/bin/env python3
"""
Verify Dry Run: Prüft alle Erfolgskriterien eines End-to-End Dry-Runs
Lokal, offline, auditierbar.
"""
import json
import sys
from pathlib import Path
import re

def check_artifacts(run_id):
    """Prüft, ob alle erwarteten Artefakte vorhanden sind"""
    run_dir = Path(f"runs/{run_id}")
    errors = []
    warnings = []
    
    # Erwartete Struktur
    expected = {
        'original/original.jpg': 'Originalbild',
        'copy/original_copy.jpg': 'Kopie',
        'metadata/metadata.user.json': 'User-Metadaten',
        'prompt/prompt.used.txt': 'Verwendeter Prompt',
        'renders/render_001.png': 'Render (optional)',
        'annotations/annotate_v001.png': 'Annotation (optional)',
        'annotations/feedback_v001.json': 'Feedback (optional)',
        'merged/merged_v001.json': 'Merged-Artefakt (optional)'
    }
    
    for rel_path, desc in expected.items():
        full_path = run_dir / rel_path
        if full_path.exists():
            print(f"✅ {desc}: {rel_path}")
        else:
            if 'optional' in desc:
                warnings.append(f"⚠️  {desc} fehlt (optional): {rel_path}")
            else:
                errors.append(f"❌ {desc} fehlt: {rel_path}")
    
    return errors, warnings

def check_json_schema(file_path, schema_path):
    """Prüft, ob JSON-Datei gegen Schema valide ist (einfache Prüfung)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Prüfe required Felder
        required = schema.get('required', [])
        missing = [field for field in required if field not in data]
        
        if missing:
            return False, f"Fehlende required Felder: {missing}"
        
        return True, None
    except Exception as e:
        return False, f"Fehler beim Laden: {e}"

def check_no_sensitive_data(file_path):
    """Prüft, ob Datei keine sensiblen Daten enthält"""
    sensitive_patterns = [
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP-Adresse'),
        (r'[C-Z]:\\[^\s]+', 'Windows-Pfad'),
        (r'/home/[^\s]+', 'Linux-Pfad'),
        (r'/Users/[^\s]+', 'macOS-Pfad'),
        (r'pve-\d+', 'Proxmox-Container-ID'),
    ]
    
    try:
        content = file_path.read_text(encoding='utf-8')
        found = []
        for pattern, desc in sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found.append(f"{desc}: {matches[:3]}")  # Erste 3 Matches
        
        if found:
            return False, f"Sensible Daten gefunden: {', '.join(found)}"
        return True, None
    except:
        return True, None  # Binärdateien ignorieren

def check_relative_paths(run_id):
    """Prüft, ob alle Pfade in merged.json relativ sind"""
    merged_path = Path(f"runs/{run_id}/merged/merged_v001.json")
    if not merged_path.exists():
        return True, None  # Optional
    
    try:
        with open(merged_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Prüfe alle Pfade in inputs, derived, trace
        absolute_paths = []
        for section in ['inputs', 'derived', 'trace']:
            if section in data:
                for key, value in data[section].items():
                    if isinstance(value, str) and (value.startswith('/') or ':' in value[:3]):
                        absolute_paths.append(f"{section}.{key}: {value}")
        
        if absolute_paths:
            return False, f"Absolute Pfade gefunden: {absolute_paths}"
        return True, None
    except Exception as e:
        return False, f"Fehler beim Laden: {e}"

def check_versioning(run_id):
    """Prüft Versionierung (monoton steigend)"""
    run_dir = Path(f"runs/{run_id}")
    errors = []
    
    # Prüfe Annotation-Versionen
    annotate_files = sorted(run_dir.glob("annotations/annotate_v*.png"))
    feedback_files = sorted(run_dir.glob("annotations/feedback_v*.json"))
    merged_files = sorted(run_dir.glob("merged/merged_v*.json"))
    
    # Extrahiere Versionen
    def extract_version(filename):
        match = re.search(r'_v(\d+)', filename.name)
        return int(match.group(1)) if match else 0
    
    versions = {
        'annotate': [extract_version(f) for f in annotate_files],
        'feedback': [extract_version(f) for f in feedback_files],
        'merged': [extract_version(f) for f in merged_files]
    }
    
    # Prüfe Monotonie
    for type_name, vers in versions.items():
        if len(vers) > 1:
            for i in range(1, len(vers)):
                if vers[i] <= vers[i-1]:
                    errors.append(f"❌ {type_name}: Version {vers[i]} ist nicht größer als {vers[i-1]}")
    
    if not errors:
        print(f"✅ Versionierung korrekt: {versions}")
    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_dry_run.py <run_id>")
        sys.exit(1)
    
    run_id = sys.argv[1]
    run_dir = Path(f"runs/{run_id}")
    
    if not run_dir.exists():
        print(f"❌ Run-Verzeichnis nicht gefunden: {run_dir}")
        sys.exit(1)
    
    print(f"Verifiziere Dry-Run für: {run_id}\n")
    
    # 1. Artefakte prüfen
    print("1. Prüfe Artefakte...")
    errors, warnings = check_artifacts(run_id)
    for err in errors:
        print(f"  {err}")
    for warn in warnings:
        print(f"  {warn}")
    print()
    
    # 2. JSON-Schemas prüfen
    print("2. Prüfe JSON-Schemas...")
    metadata_path = run_dir / "metadata/metadata.user.json"
    if metadata_path.exists():
        valid, msg = check_json_schema(metadata_path, Path("schemas/metadata.user.schema.json"))
        if valid:
            print(f"  ✅ metadata.user.json valide")
        else:
            print(f"  ❌ metadata.user.json: {msg}")
            errors.append(msg)
    
    feedback_path = run_dir / "annotations/feedback_v001.json"
    if feedback_path.exists():
        valid, msg = check_json_schema(feedback_path, Path("schemas/feedback.schema.json"))
        if valid:
            print(f"  ✅ feedback_v001.json valide")
        else:
            print(f"  ❌ feedback_v001.json: {msg}")
            errors.append(msg)
    print()
    
    # 3. Sensible Daten prüfen
    print("3. Prüfe auf sensible Daten...")
    for file_path in run_dir.rglob("*.json"):
        valid, msg = check_no_sensitive_data(file_path)
        if not valid:
            print(f"  ❌ {file_path.relative_to(run_dir)}: {msg}")
            errors.append(msg)
        else:
            print(f"  ✅ {file_path.relative_to(run_dir)}: Keine sensiblen Daten")
    print()
    
    # 4. Relative Pfade prüfen
    print("4. Prüfe relative Pfade...")
    valid, msg = check_relative_paths(run_id)
    if valid:
        print(f"  ✅ Alle Pfade sind relativ")
    else:
        print(f"  ❌ {msg}")
        errors.append(msg)
    print()
    
    # 5. Versionierung prüfen
    print("5. Prüfe Versionierung...")
    version_errors = check_versioning(run_id)
    errors.extend(version_errors)
    print()
    
    # Zusammenfassung
    print("=" * 60)
    if errors:
        print(f"❌ {len(errors)} Fehler gefunden:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ Alle Prüfungen erfolgreich!")
        print("✅ Dry-Run verifiziert!")
        sys.exit(0)

if __name__ == "__main__":
    main()
