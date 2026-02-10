# End-to-End Dry-Run – Vollständiger Workflow

## Ziel
Verifizierung des gesamten Workflows: Image → Run → Review → Batch → Regel → Prompt

**Wichtig**: Alle Schritte sind lokal, offline, auditierbar. Keine externen Zugriffe.

---

## Checkliste

### 1️⃣ Image → Run

**Ausführung:**
```bash
./scripts/init_run.sh /pfad/zum/bild.jpg 2026-02-10_ref01
```

**Erwartetes Ergebnis:**
- ✅ `runs/2026-02-10_ref01/` existiert
- ✅ `runs/2026-02-10_ref01/original/original.jpg` vorhanden
- ✅ `runs/2026-02-10_ref01/copy/original_copy.jpg` vorhanden
- ✅ `runs/2026-02-10_ref01/metadata/metadata.user.json` vorhanden (leer/initialisiert)
- ✅ `runs/2026-02-10_ref01/prompt/prompt.used.txt` vorhanden

**Verifikation:**
```bash
ls -la runs/2026-02-10_ref01/
```

---

### 2️⃣ Metadaten erfassen

**Ausführung:**
- Öffne `runs/2026-02-10_ref01/metadata/metadata.user.json`
- Fülle gemäß `schemas/metadata.user.schema.json` aus
- Verwende `examples/metadata.user.example.json` als Vorlage

**Erwartetes Ergebnis:**
- ✅ `metadata.user.json` valide gegen Schema
- ✅ Alle `required` Felder vorhanden
- ✅ Keine IPs, Pfade, Geräte-IDs enthalten

**Verifikation:**
```bash
python3 -m json.tool runs/2026-02-10_ref01/metadata/metadata.user.json
```

---

### 3️⃣ Prompt generieren

**Ausführung:**
```bash
python3 scripts/generate_prompt.py \
  runs/2026-02-10_ref01/metadata/metadata.user.json \
  runs/2026-02-10_ref01/prompt/prompt.used.txt
```

**Erwartetes Ergebnis:**
- ✅ `prompt.used.txt` enthält vollständigen Prompt
- ✅ Alle Platzhalter (`{class}`, `{car.team}`, etc.) ersetzt
- ✅ Keine `{...}` Platzhalter mehr vorhanden

**Verifikation:**
```bash
cat runs/2026-02-10_ref01/prompt/prompt.used.txt
```

---

### 4️⃣ Render (manuell / extern)

**Hinweis:** Dieser Schritt ist nicht Teil des Tools. Render wird extern erstellt.

**Ausführung:**
- Verwende `prompt.used.txt` in deinem Render-Tool (z.B. DALL-E, Midjourney, etc.)
- Speichere Ergebnis als `runs/2026-02-10_ref01/renders/render_001.png`

**Erwartetes Ergebnis:**
- ✅ `renders/render_001.png` vorhanden
- ✅ Bild entspricht Prompt-Spezifikation

---

### 5️⃣ Annotation & Feedback

**Ausführung:**
1. Öffne `ui/index.html` im Browser (lokal)
2. Lade `renders/render_001.png`
3. Annotiere Fehler (Stift/Lasso, Farben: Rot/Gelb/Blau)
4. Fülle Feedback-Formular aus
5. Speichere:
   - `annotate_v001.png`
   - `feedback_v001.json`

**Erwartetes Ergebnis:**
- ✅ `runs/2026-02-10_ref01/annotations/annotate_v001.png` vorhanden
- ✅ `runs/2026-02-10_ref01/annotations/feedback_v001.json` vorhanden
- ✅ `feedback_v001.json` valide gegen `schemas/feedback.schema.json`
- ✅ Jedes Item hat `annotation_id`, `annotation_ref`, `area`, `type`, `severity`

**Verifikation:**
```bash
python3 -m json.tool runs/2026-02-10_ref01/annotations/feedback_v001.json
```

---

### 6️⃣ Prompt-Patch

**Ausführung:**
```bash
python3 scripts/apply_feedback.py \
  runs/2026-02-10_ref01/annotations/feedback_v001.json \
  docs/master_prompt/master_prompt_v1.3.patch.txt
```

**Erwartetes Ergebnis:**
- ✅ `master_prompt_v1.3.patch.txt` erstellt
- ✅ Enthält Regel-Text basierend auf Feedback (type:severity → Mapping)

**Verifikation:**
```bash
cat docs/master_prompt/master_prompt_v1.3.patch.txt
```

---

### 7️⃣ Merge

**Ausführung:**
```bash
python3 scripts/merge_run.py 2026-02-10_ref01
```

**Erwartetes Ergebnis:**
- ✅ `runs/2026-02-10_ref01/merged/merged_v001.json` erstellt
- ✅ Enthält: `inputs`, `derived`, `trace`, `summary`
- ✅ Alle Pfade sind relativ (keine absoluten Pfade)
- ✅ `summary` enthält korrekte Zählungen

**Verifikation:**
```bash
python3 -m json.tool runs/2026-02-10_ref01/merged/merged_v001.json
```

---

### 8️⃣ Batch (optional bei mehreren Runs)

**Voraussetzung:** Mindestens 2 Runs vorhanden

**Ausführung:**
1. Bearbeite `batch/batch_config.json`:
   ```json
   {
     "runs_path": "runs",
     "include_runs": ["2026-02-10_ref01", "2026-02-11_ref02"],
     "metrics": ["issues_total", "critical", "major", "minor", "by_type", "by_area"]
   }
   ```
2. Führe aus:
   ```bash
   python3 scripts/batch_analyze.py
   ```

**Erwartetes Ergebnis:**
- ✅ `batch/reports/batch_report_v001.json` erstellt
- ✅ `batch/reports/batch_report_v001.html` erstellt
- ✅ HTML-Report zeigt Tabelle mit allen Runs
- ✅ Metriken aggregiert (by_type, by_area, by_color_meaning)

**Verifikation:**
```bash
open batch/reports/batch_report_v001.html
```

---

### 9️⃣ Regeln & Prompt

**Ausführung:**
1. Prioritäten aktualisieren:
   ```bash
   python3 scripts/update_priorities.py
   ```
2. Prompt aus Regeln bauen:
   ```bash
   python3 scripts/build_prompt_sections.py 1.3 medium
   ```

**Erwartetes Ergebnis:**
- ✅ `rules/rules_priority.json` aktualisiert (Scores, Prioritäten)
- ✅ `docs/master_prompt/master_prompt_v1.3.txt` erstellt
- ✅ `docs/master_prompt/master_prompt_v1.3.patch.txt` erstellt (Diff)
- ✅ Prompt enthält alle aktiven Regeln (priority >= medium)

**Verifikation:**
```bash
cat docs/master_prompt/master_prompt_v1.3.txt
cat docs/master_prompt/master_prompt_v1.3.patch.txt
```

---

### 🔟 Review

**Ausführung:**
1. Öffne `dashboard/index.html` im Browser
2. Lade `runs/2026-02-10_ref01/merged/merged_v001.json`
3. Prüfe:
   - Summary (Total/Critical/Major/Minor)
   - Render vorher/nachher
   - Feedback-Items Liste
   - Prompt (Base/Patch/Final)

**Erwartetes Ergebnis:**
- ✅ Dashboard zeigt alle Daten korrekt
- ✅ Render-Bilder laden
- ✅ Feedback-Items klickbar
- ✅ Prompt-Diff sichtbar

---

## Erfolgskriterien ✅

### Artefakte
- ✅ Jeder Schritt erzeugt genau ein neues Artefakt
- ✅ Versionen steigen monoton (v001 → v002 → v003)
- ✅ Alle Referenzen sind relativ (keine absoluten Pfade)

### Datenschutz
- ✅ Kein Artefakt enthält:
  - IP-Adressen
  - System-Pfade
  - Geräte-IDs
  - Container-IDs
  - Originalbilder außerhalb `runs/`

### Konsistenz
- ✅ Alle JSON-Dateien valide gegen Schemas
- ✅ Alle Referenzen auf existierende Dateien
- ✅ Versionierung nachvollziehbar

### Auditierbarkeit
- ✅ Jede Änderung nachvollziehbar
- ✅ Prompt-Patches zeigen Diff
- ✅ Feedback → Regel → Prompt nachvollziehbar

---

## Verifikations-Skript

Führe aus:
```bash
python3 scripts/verify_dry_run.py 2026-02-10_ref01
```

Das Skript prüft automatisch alle Erfolgskriterien.

---

## Nächste Schritte

Nach erfolgreichem Dry-Run:
- ✅ Pipeline verifiziert
- ✅ Produktionsreif für Timeline-Projekt
- ✅ Erweiterbar ohne Strukturbruch

**Optionen:**
- Schritt 15: Stabilisierung & Doku-Freeze (v1.0 Release)
- Erweiterung: Shortcuts / Snap-to-edge
- Erweiterung: Vergleich Modell vs. reales Fahrzeug
