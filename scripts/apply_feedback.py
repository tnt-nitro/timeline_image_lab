import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: apply_feedback.py <feedback.json> <output_patch.txt>")
    sys.exit(1)

fb_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

fb = json.loads(fb_path.read_text())
rules = json.loads(Path("schemas/feedback_to_rule.map.json").read_text())

patches = []
for item in fb.get("items", []):
    key = f'{item.get("type")}:{item.get("severity")}'
    patches += rules.get(key, [])

unique_patches = sorted(set(patches))
patch = "\n".join(f"- {p}" for p in unique_patches)

out_path.write_text(patch)
print("Patch generated:", out_path)

