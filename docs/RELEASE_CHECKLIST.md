# Release Checklist v1.0.0

## Pre-Release

### Code & Artefakte
- [ ] `verify_dry_run.py` grün für mindestens einen Test-Run
- [ ] Alle Skripte getestet (init_run, generate_prompt, apply_feedback, merge_run, batch_analyze, update_priorities, build_prompt_sections)
- [ ] UI funktioniert offline (Annotation, Dashboard)
- [ ] Alle Schemas valide gegen JSON Schema Draft 07

### Datenschutz
- [ ] Keine sensiblen Daten im Repo (IPs, Pfade, Container-IDs)
- [ ] `.gitignore` korrekt konfiguriert (runs/, private/, local_data/, *.env, *.local.json, *.private.json)
- [ ] Alle Pfade in merged.json relativ
- [ ] Beispiele enthalten nur Platzhalter

### Dokumentation
- [ ] README.md vollständig (Scope, Quickstart, Security)
- [ ] CHANGELOG.md erstellt
- [ ] `docs/workflow/end_to_end_dry_run.md` vollständig
- [ ] `rules/rules_changelog.md` finalisiert
- [ ] Alle Schemas dokumentiert

### Versionierung
- [ ] Git-Tag `v1.0.0` gesetzt
- [ ] CHANGELOG.md enthält v1.0.0 Eintrag
- [ ] README.md zeigt Version 1.0.0

## Freeze-Entscheidungen (verbindlich)

### Schemas (locked)
- [x] `metadata.user.schema.json` → v1 (locked)
- [x] `metadata.ai.schema.json` → v1 (locked)
- [x] `feedback.schema.json` → v1.1 (locked)

### Prompt-Pipeline (locked)
- [x] Generator → Patch → Merge → Build → locked
- [x] Section-Templates strukturiert
- [x] Regel-Mapping etabliert

### UI (locked)
- [x] Offline HTML/JS → locked
- [x] Annotation-Tools (Stift, Lasso, Farben) → locked
- [x] Dashboard → locked

### Batch & Regeln (locked)
- [x] Metriken definiert
- [x] Scoring-System etabliert
- [x] Priorisierung datengetrieben

### Datenschutz (locked)
- [x] Trennung Public/Private → locked
- [x] `.gitignore` finalisiert

## Post-Release

### Verifikation
- [ ] Release-Tag gepusht
- [ ] Release-Notes erstellt (falls GitHub Release)
- [ ] Dokumentation öffentlich zugänglich

### Nächste Schritte (optional)
- [ ] v1.1 Planung: KI-Analyse optional, nur nach Freigabe
- [ ] Erweiterung: Vergleich Modell vs. reales Fahrzeug
- [ ] Erweiterung: Shortcuts / Snap-to-edge

---

## Status

**Release v1.0.0:** ✅ Ready

**Datum:** 2026-02-10

**Verifiziert durch:** `scripts/verify_dry_run.py`
