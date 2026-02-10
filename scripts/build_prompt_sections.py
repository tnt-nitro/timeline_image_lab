#!/usr/bin/env python3
"""
Build Prompt Sections: Regeln → Prompt-Sektionen
Lokal, deterministisch, keine KI.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def load_rules_backlog(backlog_path):
    """Lädt Rules-Backlog"""
    with open(backlog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rules_priority(priority_path):
    """Lädt Rules-Prioritäten"""
    if not priority_path.exists():
        return {'priorities': []}
    with open(priority_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rules_mapping(map_path):
    """Lädt Mapping von Regel-IDs zu Sections"""
    with open(map_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_section_template(section_name, sections_dir):
    """Lädt Section-Template"""
    template_path = sections_dir / f"{section_name}.txt"
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return None

def get_active_rules(rules_backlog, rules_priority, min_priority='low'):
    """Gibt aktive Regeln zurück, gefiltert nach Priorität"""
    active_rules = []
    priority_map = {p['rule_id']: p['priority'] for p in rules_priority.get('priorities', [])}
    
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    min_priority_level = priority_order.get(min_priority, 1)
    
    for rule in rules_backlog.get('rules', []):
        if rule.get('status') != 'active':
            continue
        
        rule_id = rule['rule_id']
        priority = priority_map.get(rule_id, 'low')
        priority_level = priority_order.get(priority, 1)
        
        if priority_level >= min_priority_level:
            active_rules.append(rule)
    
    return active_rules

def group_rules_by_section(rules, rules_mapping):
    """Gruppiert Regeln nach Section"""
    by_section = {}
    
    for rule in rules:
        rule_id = rule['rule_id']
        mapping = rules_mapping.get(rule_id, {})
        section = mapping.get('section', 'base')
        rule_text = mapping.get('text', rule.get('description', ''))
        
        if section not in by_section:
            by_section[section] = []
        
        by_section[section].append({
            'rule_id': rule_id,
            'text': rule_text
        })
    
    return by_section

def inject_rules(template, rules):
    """Ersetzt {RULES} Platzhalter durch Regel-Text"""
    if not rules:
        return template.replace('{RULES}', '')
    
    rules_text = '\n'.join(f"- {rule['text']}" for rule in rules)
    return template.replace('{RULES}', rules_text)

def assemble_full_prompt(sections_dir, rules_by_section, rules_mapping):
    """Baut vollständigen Prompt aus Sections zusammen"""
    section_order = ['base', 'front', 'headlights', 'roof', 'rear']
    prompt_parts = []
    
    for section_name in section_order:
        template = load_section_template(section_name, sections_dir)
        if template:
            rules = rules_by_section.get(section_name, [])
            section_text = inject_rules(template, rules)
            prompt_parts.append(section_text)
    
    # Füge weitere Sections hinzu, die nicht in der Standard-Liste sind
    for section_name in rules_by_section.keys():
        if section_name not in section_order:
            template = load_section_template(section_name, sections_dir)
            if template:
                rules = rules_by_section.get(section_name, [])
                section_text = inject_rules(template, rules)
                prompt_parts.append(section_text)
    
    return '\n\n'.join(prompt_parts)

def generate_patch(old_prompt, new_prompt):
    """Generiert Patch-Diff zwischen altem und neuem Prompt"""
    old_lines = old_prompt.split('\n')
    new_lines = new_prompt.split('\n')
    
    patch_lines = []
    patch_lines.append(f"# Prompt Patch - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Einfacher Diff (Zeilenweise)
    old_set = set(old_lines)
    new_set = set(new_lines)
    
    added = new_set - old_set
    removed = old_set - new_set
    
    if added:
        patch_lines.append("## Added:")
        for line in sorted(added):
            if line.strip():
                patch_lines.append(f"+ {line}")
    
    if removed:
        patch_lines.append("\n## Removed:")
        for line in sorted(removed):
            if line.strip():
                patch_lines.append(f"- {line}")
    
    return '\n'.join(patch_lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: build_prompt_sections.py <version> [min_priority]")
        print("  version: z.B. 1.3")
        print("  min_priority: high, medium, low (default: low)")
        sys.exit(1)
    
    version = sys.argv[1]
    min_priority = sys.argv[2] if len(sys.argv) > 2 else 'low'
    
    # Pfade
    rules_dir = Path("rules")
    sections_dir = Path("docs/master_prompt/sections")
    output_dir = Path("docs/master_prompt")
    
    backlog_path = rules_dir / "rules_backlog.json"
    priority_path = rules_dir / "rules_priority.json"
    map_path = rules_dir / "rules_to_prompt.map.json"
    
    # Lade Daten
    rules_backlog = load_rules_backlog(backlog_path)
    rules_priority = load_rules_priority(priority_path)
    rules_mapping = load_rules_mapping(map_path)
    
    # Filtere aktive Regeln
    active_rules = get_active_rules(rules_backlog, rules_priority, min_priority)
    print(f"Found {len(active_rules)} active rules (min priority: {min_priority})")
    
    # Gruppiere nach Section
    rules_by_section = group_rules_by_section(active_rules, rules_mapping)
    
    # Baue vollständigen Prompt
    full_prompt = assemble_full_prompt(sections_dir, rules_by_section, rules_mapping)
    
    # Lade alten Prompt für Patch (falls vorhanden)
    old_prompt = None
    old_prompt_files = sorted(output_dir.glob("master_prompt_v*.txt"))
    old_patch_files = sorted(output_dir.glob("master_prompt_v*.patch.txt"))
    if old_prompt_files:
        # Finde neuesten vollständigen Prompt (ohne .patch.txt)
        full_prompts = [f for f in old_prompt_files if ".patch.txt" not in f.name]
        if full_prompts:
            old_prompt = full_prompts[-1].read_text(encoding='utf-8')
    
    # Schreibe neuen Prompt
    output_path = output_dir / f"master_prompt_v{version}.txt"
    output_path.write_text(full_prompt, encoding='utf-8')
    print(f"Prompt written: {output_path}")
    
    # Generiere Patch (falls alter Prompt vorhanden)
    if old_prompt:
        patch = generate_patch(old_prompt, full_prompt)
        patch_path = output_dir / f"master_prompt_v{version}.patch.txt"
        patch_path.write_text(patch, encoding='utf-8')
        print(f"Patch written: {patch_path}")
    
    # Zeige verwendete Regeln
    print("\nUsed rules by section:")
    for section, rules in sorted(rules_by_section.items()):
        print(f"  {section}: {len(rules)} rules")
        for rule in rules:
            print(f"    - {rule['rule_id']}: {rule['text'][:60]}...")

if __name__ == "__main__":
    main()
