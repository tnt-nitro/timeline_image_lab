#!/usr/bin/env python3
"""
Merge Run: Zusammenführung User-Metadaten + Feedback + Prompt-Patch
Lokal, offline, keine Netzwerk-Kommunikation.
"""
import json
import sys
from pathlib import Path
from glob import glob

if len(sys.argv) < 2:
    print("Usage: merge_run.py <run_id> [version]")
    print("  run_id: z.B. 2026-02-10_ref01")
    print("  version: optional, sonst wird höchste Version verwendet")
    sys.exit(1)

run_id = sys.argv[1]
run_dir = Path(f"runs/{run_id}")

if not run_dir.exists():
    print(f"Error: Run directory not found: {run_dir}")
    sys.exit(1)

# Version bestimmen
if len(sys.argv) >= 3:
    version = int(sys.argv[2])
else:
    # Höchste vorhandene Version finden
    feedback_files = list(run_dir.glob("annotations/feedback_v*.json"))
    if feedback_files:
        versions = []
        for f in feedback_files:
            try:
                v = int(f.stem.split("_v")[1])
                versions.append(v)
            except:
                pass
        version = max(versions) if versions else 1
    else:
        version = 1

# Pfade
metadata_path = run_dir / "metadata" / "metadata.user.json"
feedback_path = run_dir / "annotations" / f"feedback_v{version:03d}.json"
annotate_path = run_dir / "annotations" / f"annotate_v{version:03d}.png"

# Inputs lesen
inputs = {}
if metadata_path.exists():
    inputs["metadata_user"] = str(metadata_path.relative_to(run_dir))
else:
    inputs["metadata_user"] = None

if feedback_path.exists():
    inputs["feedback"] = str(feedback_path.relative_to(run_dir))
    fb_data = json.loads(feedback_path.read_text())
else:
    inputs["feedback"] = None
    fb_data = {"items": []}

# Prompt-Basis finden (neueste Version)
prompt_base_files = sorted(Path("docs/master_prompt").glob("master_prompt_v*.txt"))
if prompt_base_files:
    # .patch.txt ausschließen, nur vollständige Prompts
    full_prompts = [f for f in prompt_base_files if ".patch.txt" not in f.name]
    if full_prompts:
        inputs["prompt_base"] = str(full_prompts[-1].relative_to(Path(".")))
    else:
        inputs["prompt_base"] = None
else:
    inputs["prompt_base"] = None

# Derived: Prompt-Patch finden
patch_files = sorted(Path("docs/master_prompt").glob("master_prompt_v*.patch.txt"))
if patch_files:
    inputs["prompt_patch"] = str(patch_files[-1].relative_to(Path(".")))
    # Final-Prompt-Version aus Patch ableiten
    patch_name = patch_files[-1].stem.replace(".patch", "")
    final_prompt_path = Path("docs/master_prompt") / f"{patch_name}.txt"
    if final_prompt_path.exists():
        inputs["prompt_final"] = str(final_prompt_path.relative_to(Path(".")))
    else:
        inputs["prompt_final"] = None
else:
    inputs["prompt_patch"] = None
    inputs["prompt_final"] = None

# Trace: Render-Dateien finden
render_files = sorted((run_dir / "renders").glob("render_*.png"))
trace = {}
if annotate_path.exists():
    trace["annotation_png"] = str(annotate_path.relative_to(run_dir))
if len(render_files) >= 2:
    trace["render_prev"] = str(render_files[-2].relative_to(run_dir))
    trace["render_next"] = str(render_files[-1].relative_to(run_dir))
elif len(render_files) == 1:
    trace["render_prev"] = None
    trace["render_next"] = str(render_files[0].relative_to(run_dir))
else:
    trace["render_prev"] = None
    trace["render_next"] = None

# Summary: Feedback auswerten
summary = {
    "issues_total": len(fb_data.get("items", [])),
    "critical": sum(1 for item in fb_data.get("items", []) if item.get("severity") == "critical"),
    "major": sum(1 for item in fb_data.get("items", []) if item.get("severity") == "major"),
    "minor": sum(1 for item in fb_data.get("items", []) if item.get("severity") == "minor")
}

# Merged-Struktur
merged = {
    "run_id": run_id,
    "version": version,
    "inputs": {
        "metadata_user": inputs["metadata_user"],
        "feedback": inputs["feedback"],
        "prompt_base": inputs["prompt_base"]
    },
    "derived": {
        "prompt_patch": inputs["prompt_patch"],
        "prompt_final": inputs["prompt_final"]
    },
    "trace": trace,
    "summary": summary
}

# Ausgabe
merged_dir = run_dir / "merged"
merged_dir.mkdir(exist_ok=True)
output_path = merged_dir / f"merged_v{version:03d}.json"
output_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
print(f"Merged artifact created: {output_path}")
