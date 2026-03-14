---
name: TASK-GWS-OAUTH-SETUP
description: Step-by-step Google Workspace Setup for PA Gmail/Calendar/Drive integration
type: task
---

# TASK: Complete GWS OAuth Setup for PA

**Owner**: Miles (or delegate)
**Deadline**: March 15, 2026
**Time estimate**: 1-2 hours
**Impact**: Enables PA email/calendar automation in investor demo

---

## Prerequisites
- Google account with admin access to workspace
- Google Cloud Console access (or ability to create project)
- VPS SSH access (`152.53.55.207`)

---

## STEP 1: Create Service Account (Google Cloud Console)

### 1a. Go to Google Cloud Console
```
https://console.cloud.google.com/
```

### 1b. Create new project (if needed)
- Click "Select a Project" → "New Project"
- Name: `OpenClaw PA`
- Region: Any (doesn't matter for service account)

### 1c. Enable APIs
Go to "APIs & Services" → "Library"
Enable these 3 APIs:
1. **Gmail API**
   - Search: "Gmail API"
   - Click "Enable"

2. **Google Calendar API**
   - Search: "Google Calendar API"
   - Click "Enable"

3. **Google Drive API**
   - Search: "Google Drive API"
   - Click "Enable"

### 1d. Create Service Account
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "Service Account"
- Fill in:
  - Service account name: `openclaw-pa`
  - Service account ID: (auto-filled, keep default)
  - Description: "OpenClaw Personal Assistant automation"
- Click "Create and Continue"
- Grant roles: **Editor** (for simplicity; can restrict later)
- Click "Continue"

### 1e. Create and Download Key
- On Service Account page, go to "Keys" tab
- Click "Add Key" → "Create new key"
- Format: **JSON** (important!)
- Downloads as `openclaw-pa-*.json`
- **SAVE THIS FILE** - you'll need it next

---

## STEP 2: Configure Domain-Wide Delegation

### 2a. Enable Domain-Wide Delegation
- Go back to Service Account → "Details" tab
- Under "Domain-wide delegation", click "Enable"
- Agree to terms

### 2b. Copy the Client ID
- You'll need this in next step
- Format: `123456789-xxx.iam.gserviceaccount.com`

---

## STEP 3: Grant Scopes in Google Workspace Admin Console

This step assumes you're using Google Workspace (not just personal Gmail).
If personal Gmail: skip to Step 4.

### 3a. Go to Google Workspace Admin
```
https://admin.google.com/
```

### 3b. Navigate to Security
- Left menu: "Security" → "API controls"
- Select "Domain wide delegation"

### 3c. Add OAuth Client
- Click "Add new"
- Paste Client ID from Step 2b
- Add these OAuth scopes (comma-separated):
  ```
  https://www.googleapis.com/auth/gmail.send,
  https://www.googleapis.com/auth/gmail.readonly,
  https://www.googleapis.com/auth/gmail.modify,
  https://www.googleapis.com/auth/calendar,
  https://www.googleapis.com/auth/drive,
  https://www.googleapis.com/auth/userinfo.email
  ```
- Click "Authorize"

---

## STEP 4: Add Credentials to VPS

### 4a. SSH into VPS
```bash
ssh root@152.53.55.207
```

### 4b. Upload the JSON Key File
On your local machine:
```bash
scp ~/Downloads/openclaw-pa-*.json root@152.53.55.207:/root/openclaw/config/
```

Or manually:
1. Copy entire contents of JSON file
2. Create on VPS: `/root/openclaw/config/gws-credentials.json`
3. Paste contents

### 4c. Verify File Permissions
```bash
sudo chmod 600 /root/openclaw/config/gws-credentials.json
ls -la /root/openclaw/config/gws-credentials.json
# Should show: -rw------- (only root readable)
```

---

## STEP 5: Update .env File

### 5a. Edit VPS .env
```bash
sudo nano /root/openclaw/.env
```

### 5b. Add These Variables
```bash
# Google Workspace Setup
GOOGLE_SERVICE_ACCOUNT_JSON=/root/openclaw/config/gws-credentials.json
GOOGLE_WORKSPACE_DOMAIN=your-domain.com  # e.g., overseerclaw.uk
GMAIL_SENDER=you@your-domain.com
```

### 5c. Save & Exit
Press `Ctrl+X`, then `Y`, then `Enter`

---

## STEP 6: Test OAuth Flow

### 6a. Restart PA Service
```bash
systemctl restart openclaw-gateway
```

### 6b. Test Gmail API
```bash
curl -X POST https://gateway.overseerclaw.uk/api/pa/email/send \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: <your-token>" \
  -d '{
    "to": "yourself@example.com",
    "subject": "Test from PA",
    "body": "OpenClaw PA is working!"
  }'
```

Expected response: `{"status": "sent", "message_id": "..."}`

### 6c. Test Calendar API
```bash
curl -X GET https://gateway.overseerclaw.uk/api/pa/calendar/today \
  -H "X-Auth-Token: <your-token>"
```

Expected response: List of today's events

### 6d. Test Drive API
```bash
curl -X GET https://gateway.overseerclaw.uk/api/pa/drive/list \
  -H "X-Auth-Token: <your-token>"
```

Expected response: List of files in Google Drive

---

## STEP 7: Verify & Document

### 7a. Check Logs
```bash
journalctl -u openclaw-gateway -f | grep -i "gmail\|calendar\|drive"
```

### 7b. Run PA Health Check
```bash
curl https://pa.overseerclaw.uk/health
# Should include: "gmail": true, "calendar": true, "drive": true
```

### 7c. Update Status File
Edit: `/root/.claude/projects/-root/memory/pa-deploy-status.md`
Mark as COMPLETE:
```markdown
### High Priority
- [x] Gmail OAuth (send/receive emails)
- [x] Google Calendar (schedule management)
- [x] Google Drive (file storage)
```

---

## Troubleshooting

### "403 Forbidden" errors
→ Workspace admin didn't grant scopes (return to Step 3c)

### "401 Unauthorized"
→ Service account not enabled or credentials path wrong (check Step 4c)

### "Service account not found"
→ JSON file corrupt or in wrong location (re-download from Step 1e)

### Gmail sends but Calendar returns null
→ Calendar API not enabled (go back to Step 1c)

---

## Success Criteria
- [x] Service account created
- [x] APIs enabled (Gmail, Calendar, Drive)
- [x] Domain-wide delegation configured
- [x] Credentials on VPS
- [x] .env updated
- [x] All 3 APIs responding (test calls successful)
- [x] Logs showing no auth errors
- [x] PA health check shows green

---

## Time Tracking
- Start: ______
- End: ______
- Total: ______

## Notes
(Space for issues encountered and solutions)

---

**Next Task**: TASK-EDGEBOARD-RECOVERY.md (search for source, rebuild if needed)
