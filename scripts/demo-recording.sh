#!/bin/bash
# Demo recording script for swarm-agency
# Run: bash scripts/demo-recording.sh
# Or record: asciinema rec demo.cast -c "bash scripts/demo-recording.sh"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

type_slow() {
    local text="$1"
    local delay="${2:-0.04}"
    for ((i=0; i<${#text}; i++)); do
        printf '%s' "${text:$i:1}"
        sleep "$delay"
    done
}

pause() {
    sleep "${1:-1.5}"
}

clear
echo ""
echo -e "${CYAN}${BOLD}  swarm-agency — Pressure-test decisions from multiple AI perspectives${NC}"
echo -e "${DIM}  ─────────────────────────────────────────────────────────────────${NC}"
echo ""
pause 2

# Step 1: Install
echo -e "${DIM}  # Install (takes 10 seconds)${NC}"
type_slow "  $ pip install swarm-agency" 0.03
echo ""
pause 1
echo -e "${DIM}  Successfully installed swarm-agency-1.0.0${NC}"
pause 2
echo ""

# Step 2: Try a demo
echo -e "${DIM}  # Try instantly — no API key needed${NC}"
type_slow "  $ swarm-agency --demo startup-pivot" 0.03
echo ""
pause 1

# Run the actual demo
swarm-agency --demo startup-pivot
pause 3

# Step 3: See full debate
echo -e "${DIM}  # Want to see how the agents argued?${NC}"
type_slow "  $ swarm-agency --last" 0.03
echo ""
pause 1

swarm-agency --last 2>&1 | head -45
pause 3

# Step 4: Live debate
echo ""
echo -e "${DIM}  # Ask your own question (needs API key)${NC}"
type_slow "  $ swarm-agency \"Should we open-source our core SDK?\" -d Strategy" 0.03
echo ""
pause 1

# Use a demo for this to avoid needing real API
swarm-agency --demo open-source
pause 3

# Step 5: Show agents
echo ""
echo -e "${DIM}  # 43 agents across 10 departments${NC}"
type_slow "  $ swarm-agency --agents" 0.03
echo ""
pause 1

swarm-agency --agents 2>&1 | head -20
echo -e "${DIM}  ... (43 agents total)${NC}"
pause 2

# Outro
echo ""
echo -e "${CYAN}${BOLD}  ─────────────────────────────────────────────────────────────────${NC}"
echo -e "${CYAN}  github.com/Miles0sage/swarm-agency${NC}"
echo -e "${DIM}  43 agents · 10 departments · 7 model families · MIT licensed${NC}"
echo ""
pause 3
