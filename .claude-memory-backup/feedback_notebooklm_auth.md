---
name: NotebookLM Auth Persistence Issue
description: NotebookLM storage_state.json keeps disappearing - need to investigate on restart
type: feedback
---

NotebookLM auth (`~/.notebooklm/storage_state.json`) keeps disappearing. The browser_profile dir exists but is empty.

**Why:** Playwright chromium binary gets wiped on upgrades, and the storage_state.json either wasn't saved properly or got cleaned up. Need to check on fresh session.

**How to apply:** On next session, run `find / -name "storage_state*"` and `ls -laR /root/.notebooklm/` to find if auth is there. If not, user needs to re-run `notebooklm login`. The VPS needs an interactive browser — may need SSH -X forwarding or login from local PC and scp the file over.

NotebookLM notebook ID for speed build research: `0ccfaf91-fe89-4b07-9b4a-d6098391e7c4`
