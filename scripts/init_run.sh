#!/usr/bin/env bash
set -e

IMG_PATH="$1"
RUN_ID="$2"

if [ -z "$IMG_PATH" ] || [ -z "$RUN_ID" ]; then
  echo "Usage: ./init_run.sh <image_path> <run_id>"
  exit 1
fi

RUN_DIR="runs/${RUN_ID}"

mkdir -p \
  "${RUN_DIR}/original" \
  "${RUN_DIR}/copy" \
  "${RUN_DIR}/metadata" \
  "${RUN_DIR}/prompt" \
  "${RUN_DIR}/annotations" \
  "${RUN_DIR}/renders"

cp "$IMG_PATH" "${RUN_DIR}/original/original.jpg"
cp "$IMG_PATH" "${RUN_DIR}/copy/original_copy.jpg"

cat > "${RUN_DIR}/metadata/metadata.user.json" <<EOF
{
  "image_id": "${RUN_ID}",
  "status": "initialized",
  "notes": []
}
EOF

cat > "${RUN_DIR}/prompt/prompt.used.txt" <<EOF
MASTER_PROMPT_v1.2
EOF

echo "Run ${RUN_ID} initialized."

