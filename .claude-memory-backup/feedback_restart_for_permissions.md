---
name: Restart Required After Permission Changes
description: Claude Code must be restarted for settings.local.json permission changes to take effect
type: feedback
---

After writing/updating `/root/.claude/settings.local.json`, permissions do NOT take effect mid-session.

**Why:** Claude Code loads permission rules at startup. Changes to settings files during a conversation are ignored until restart.

**How to apply:** When permissions get wiped or need updating, tell the user to restart Claude Code after the file is saved. Don't assume changes are live immediately.

Also: when user approves specific commands via the UI prompt, Claude Code OVERWRITES settings.local.json with ONLY those rules — it doesn't append. This wipes all existing auto-approve rules. Be aware of this and restore the full config if it happens.

Full auto-approve config location: `/root/.claude/settings.local.json`
