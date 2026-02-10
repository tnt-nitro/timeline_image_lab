# Changelog

Alle wichtigen Änderungen werden in diesem Dokument festgehalten.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0] - 2026-02-10

### Hinzugefügt
- **MVP-Grundfunktionalität**
  - `init_run.sh`: Run-Verzeichnisstruktur erstellen
  - Bild-Import (Original + Kopie)
  - Pflichtdateien automatisch anlegen

- **Metadaten-Schema v1**
  - `metadata.user.schema.json`: Vollständiges Schema für User-Analyse
  - `metadata.ai.schema.json`: Schema für KI-Analyse (optional)
  - Trennung User vs. KI-Metadaten

- **Prompt-Generator**
  - `generate_prompt.py`: Schema → Prompt (deterministisch)
  - Template-basiert, versionierbar

- **Annotation & Feedback**
  - `ui/index.html`: Offline Annotation-UI
  - Stift, Lasso, mehrere Farben (Rot/Grün/Gelb/Blau)
  - Undo/Redo, Versionierung
  - `feedback.schema.json`: Strukturiertes Feedback-Format

- **Prompt-Patch-System**
  - `apply_feedback.py`: Feedback → Regel-Mapping → Patch
  - Automatische Regelableitung

- **Merge & Konsolidierung**
  - `merge_run.py`: User-Metadaten + Feedback + Prompt-Patch zusammenführen
  - `merged_v00X.json`: Single Source of Truth pro Iteration

- **Batch-Analyse**
  - `batch_analyze.py`: Mehrere Runs vergleichen
  - Metriken: issues_total, critical/major/minor, by_type, by_area, by_color_meaning
  - HTML-Report mit sortierbarer Tabelle

- **Regel-Management**
  - `rules_backlog.json`: Zentrale Regel-Sammlung
  - `rules_priority.json`: Priorisierung datengetrieben
  - `update_priorities.py`: Automatische Prioritätsberechnung

- **Prompt-Section-Generator**
  - `build_prompt_sections.py`: Regeln → Prompt-Sektionen
  - Modular, versioniert, auditierbar

- **Review-Dashboard**
  - `dashboard/index.html`: Statisches Review-UI
  - Vorher/Nachher-Vergleich, Feedback-Übersicht

- **End-to-End Workflow**
  - `docs/workflow/end_to_end_dry_run.md`: Vollständige Anleitung
  - `verify_dry_run.py`: Automatische Verifikation

- **Dokumentation**
  - README.md: Scope, Security, Quickstart
  - Schemas dokumentiert
  - Beispiele für alle Formate

### Sicherheit
- **Strikte Trennung Public/Private**
  - `.gitignore`: runs/, private/, local_data/, *.env, *.local.json, *.private.json
  - Keine sensiblen Daten im Repo
  - Alle Pfade relativ

- **Offline-First**
  - Keine automatischen Uploads
  - Keine Telemetrie
  - Keine externen API-Calls ohne explizite Freigabe

### Fixes
- Keine (Initial Release)

### Geändert
- Keine (Initial Release)

### Entfernt
- Keine (Initial Release)

---

## Versionierung

- **v1.0.0**: Initial Release (2026-02-10)
- **v1.x**: Feature-Erweiterungen (semver-konform)
- **v2.0**: Breaking Changes

---

## Nächste Versionen (geplant)

### v1.1 (optional)
- KI-Analyse optional, nur nach expliziter Freigabe
- Erweiterung: Vergleich Modell vs. reales Fahrzeug
- Erweiterung: Shortcuts / Snap-to-edge
