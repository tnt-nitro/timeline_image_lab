# Timeline Image Lab

**Version:** 1.0.0  
**Status:** Stable Release  
**Lizenz:** Siehe LICENSE-Datei

## Überblick

Timeline Image Lab ist ein lokales, offline-fähiges Tool für die systematische Analyse und Verbesserung von Rennwagen-Illustrationen. Es ermöglicht:

- Strukturierte Metadaten-Erfassung
- Visuelle Annotation von Fehlern
- Feedback-basierte Prompt-Verbesserung
- Batch-Analyse mehrerer Runs
- Regel-basierte Prompt-Generierung

**Kernprinzipien:**

- ✅ 100% lokal, offline
- ✅ Keine sensiblen Daten im Repo
- ✅ Deterministisch, reproduzierbar
- ✅ Auditierbar, versioniert

---

## Quickstart

### 1. Run initialisieren

```bash
./scripts/init_run.sh /pfad/zum/bild.jpg 2026-02-10_ref01
```

### 2. Metadaten erfassen

Bearbeite `runs/2026-02-10_ref01/metadata/metadata.user.json` gemäß Schema.

### 3. Prompt generieren

```bash
python3 scripts/generate_prompt.py \
  runs/2026-02-10_ref01/metadata/metadata.user.json \
  runs/2026-02-10_ref01/prompt/prompt.used.txt
```

### 4. Render (extern)

Verwende den generierten Prompt in deinem Render-Tool.

### 5. Annotation & Feedback

Öffne `ui/index.html` im Browser, annotiere Fehler, speichere Feedback.

### 6. Prompt-Patch

```bash
python3 scripts/apply_feedback.py \
  runs/2026-02-10_ref01/annotations/feedback_v001.json \
  docs/master_prompt/master_prompt_v1.3.patch.txt
```

### 7. Merge

```bash
python3 scripts/merge_run.py 2026-02-10_ref01
```

### 8. Review

Öffne `dashboard/index.html`, lade `runs/2026-02-10_ref01/merged/merged_v001.json`.

**Vollständige Anleitung:** Siehe [docs/workflow/end_to_end_dry_run.md](docs/workflow/end_to_end_dry_run.md)

---

## Projektstruktur

```
timeline_image_lab/
├── scripts/          # Ausführbare Skripte
├── schemas/          # JSON-Schemas
├── rules/            # Regel-Backlog & Prioritäten
├── docs/              # Dokumentation
│   ├── master_prompt/  # Prompt-Templates & Sections
│   └── workflow/       # Workflow-Dokumentation
├── ui/               # Annotation-UI (HTML/JS)
├── dashboard/        # Review-Dashboard
├── batch/            # Batch-Konfiguration & Reports
├── examples/         # Beispiel-Dateien (Platzhalter)
└── runs/             # Lokale Runs (gitignored)
```

---

## Security & Data Separation

### Public Development (GitHub)

This repository contains **only**:

- Source code
- Scripts
- Schemas
- Documentation
- **Example files with placeholders only**

No real data is stored or committed.

### Private / Local Data (Never Commit)

The following directories and files are **strictly local** and must never be pushed:

- runs/
- private/
- local_data/
- *.env
- *.local.json
- *.private.json

They may contain:

- Original images
- Image copies
- Real metadata
- Annotations
- Prompts with real references
- Any sensitive or personal information

### API & External Services

- No automatic uploads
- No background sync
- No telemetry
- Any external API usage requires explicit user approval

---

## Verifikation

Führe nach einem Dry-Run aus:

```bash
python3 scripts/verify_dry_run.py <run_id>
```

Das Skript prüft:

- ✅ Alle Artefakte vorhanden
- ✅ JSON-Schemas valide
- ✅ Keine sensiblen Daten
- ✅ Alle Pfade relativ
- ✅ Versionierung korrekt

---

## Versionierung

- **v1.0.0**: Initial Release (2026-02-10)
- **v1.x**: Feature-Erweiterungen (semver-konform)
- **v2.0**: Breaking Changes

Siehe [CHANGELOG.md](CHANGELOG.md) für Details.

---

## Dokumentation

- **Workflow:** [docs/workflow/end_to_end_dry_run.md](docs/workflow/end_to_end_dry_run.md)
- **Schemas:** `schemas/*.schema.json`
- **Beispiele:** `examples/*.example.json`
- **Regeln:** `rules/rules_changelog.md`

---

## Lizenz

Siehe LICENSE-Datei.
