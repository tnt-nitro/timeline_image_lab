import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: generate_prompt.py <metadata.user.json> <output_prompt.txt>")
    sys.exit(1)

metadata_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

data = json.loads(metadata_path.read_text())

template = Path("docs/master_prompt/master_prompt_v1.2.txt").read_text()


def get(path, default="UNKNOWN"):
    cur = data
    for p in path.split("."):
        cur = cur.get(p, default)
    return cur


prompt = template.format(
    **{
        "class": get("class"),
        "car.team": get("car.team"),
        "car.model": get("car.model"),
        "car.number": get("car.number"),
        "car.is_scale_model": get("car.is_scale_model"),
        "scene": get("scene"),
        "view": get("view"),
        "front.splitter": get("front.splitter"),
        "front.cooling_inlet": get("front.cooling_inlet"),
        "front.center_keel": get("front.center_keel"),
        "front.inlet_braces": get("front.inlet_braces"),
        "front.tow_hooks": get("front.tow_hooks"),
        "headlights.layout": get("headlights.layout"),
        "headlights.blind_plate_is_flush": get("headlights.blind_plate_is_flush"),
        "windshield_banner.background": get("windshield_banner.background"),
        "windshield_banner.text_color": get("windshield_banner.text_color"),
    }
)

output_path.write_text(prompt)
print("Prompt generated:", output_path)

