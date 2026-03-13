#!/usr/bin/env bash
# Record the swarm-agency demo as an asciinema cast file.
#
# Usage: ./demo/record_demo.sh
# Output: demo/demo.cast (asciinema v2 format)
#
# Play back with: asciinema play demo/demo.cast
# Upload with:    asciinema upload demo/demo.cast

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CAST_FILE="${SCRIPT_DIR}/demo.cast"

echo "Recording demo to ${CAST_FILE}..."

asciinema rec \
  --cols 140 \
  --rows 50 \
  --title "swarm-agency: AI agents debate your decisions" \
  --command "python3 ${SCRIPT_DIR}/generate_demo.py" \
  --overwrite \
  "${CAST_FILE}"

echo ""
echo "Done! Cast file saved to ${CAST_FILE}"
echo ""
echo "Play back:  asciinema play ${CAST_FILE}"
echo "Upload:     asciinema upload ${CAST_FILE}"
