# 🚀 DEPLOYMENT GUIDE — Daniel Signs Calculator

**Updated**: 2026-02-18  
**App**: Streamlit Python Application  
**Target**: Streamlit Community Cloud (free) + optional Hostinger redirect

---

## ⚠️ IMPORTANT: About Hostinger

**Hostinger cannot run Python/Streamlit apps directly.**  
Hostinger is a PHP/HTML web hosting platform. Your calculator is a Python app.

**The correct deployment path is:**

```
Your Code (GitHub) → Streamlit Community Cloud (FREE) → Your App URL
                                                              ↓
                                          Hostinger can redirect to this URL
```

**Good news**: Streamlit Community Cloud is **completely free** and gives you a URL like:  
`https://daniel-signs-calc.streamlit.app`

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Before uploading anything, verify these files are ready:

### ✅ Files to Upload (to GitHub)
```
shining-observatory/
├── main.py                          ✅ Main entry point
├── requirements.txt                 ✅ Python dependencies
├── components/
│   ├── calc_v5.py                   ✅ Calculator (v5 with Unit Economics)
│   └── supplier.py                  ✅ Supplier Manager
├── utils/
│   ├── db.py                        ✅ Firebase database layer
│   ├── logic_engine.py              ✅ Pricing calculations
│   ├── nesting_optimizer.py         ✅ Batch nesting optimizer
│   ├── pdf_gen.py                   ✅ PDF quote generator
│   └── styles.py                    ✅ CSS theme system
└── .gitignore                       ✅ Excludes secrets
```

### 🚫 Files to NEVER Upload
```
serviceAccountKey.json               ❌ NEVER — Contains Firebase private key
.venv/                               ❌ Virtual environment (too large, not needed)
__pycache__/                         ❌ Compiled Python cache
.git/                                ❌ Git internals
```

---

## 🔧 STEP 1: Prepare GitHub Repository

### 1a. Check your current GitHub repo
If you already have a repo from the previous deployment, skip to Step 1b.

If starting fresh:
1. Go to [github.com/new](https://github.com/new)
2. Name: `daniel-signs-calc`
3. Set to **Private** (safer for business tools)
4. Click **Create repository**

### 1b. Push latest code to GitHub

Open a terminal in your project folder and run:

```bash
# If repo already connected:
git add .
git commit -m "v1.3 - Unit Economics + Nesting Optimizer"
git push

# If starting fresh:
git init
git add .
git commit -m "Initial deploy - v1.3"
git remote add origin https://github.com/YOUR_USERNAME/daniel-signs-calc.git
git push -u origin main
```

**Verify on GitHub** that `serviceAccountKey.json` is NOT in the repository.

---

## 🌐 STEP 2: Deploy to Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `YOUR_USERNAME/daniel-signs-calc`
   - **Branch**: `main`
   - **Main file path**: `main.py`
5. Click **"Deploy!"**

The app will build (takes 2-3 minutes). It will fail at first — that's expected.

---

## 🔑 STEP 3: Add Firebase Secrets (Critical!)

The app crashes without the database key. Here's how to add it securely:

### 3a. Open App Settings
In Streamlit Cloud, find your app and click:
`⋮ (three dots)` → **Settings** → **Secrets**

### 3b. Format Your Firebase Key

Open your `serviceAccountKey.json` file and convert it to TOML format:

**Your JSON looks like:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Convert to TOML (paste this into Streamlit Secrets):**
```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**⚠️ Important**: The `private_key` value must keep the `\n` characters as literal `\n` (not actual newlines).

### 3c. Save and Reboot
Click **Save** → The app will restart and connect to Firebase.

---

## 🏠 STEP 4: Optional — Hostinger Redirect

If you want `https://yourdomain.com/calculator` to redirect to your Streamlit app:

### Option A: Simple HTML Redirect Page

Create a file called `calculator.html` on your Hostinger account:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://daniel-signs-calc.streamlit.app">
  <title>Daniel Signs Calculator</title>
</head>
<body>
  <p>Redirecting to calculator... 
     <a href="https://daniel-signs-calc.streamlit.app">Click here if not redirected</a>
  </p>
</body>
</html>
```

Upload this to your Hostinger `public_html` folder via File Manager or FTP.

### Option B: .htaccess Redirect (Apache)

Add to your Hostinger `.htaccess` file:
```apache
Redirect 301 /calculator https://daniel-signs-calc.streamlit.app
```

### Option C: Custom Domain (Advanced)

Streamlit Cloud supports custom domains on paid plans. If you want `calc.danielsigns.co.uk` to work directly, you'd need to upgrade Streamlit Cloud.

---

## 📦 STEP 5: Verify Deployment

After deploying, test these features:

### Calculator Tab
- [ ] Add a material (e.g., Standard Vinyl, 30cm × 42cm, qty 6)
- [ ] Set production hours (e.g., 1h)
- [ ] Check **Unit Economics** panel appears with per-item breakdown
- [ ] Enable **Batch Nesting Optimizer** and verify nesting analysis
- [ ] Toggle **Print Ready** — design hours should zero out
- [ ] Download PDF quote

### Supplier Manager Tab
- [ ] Materials load from Firebase (not mock data)
- [ ] Can add a new vinyl material
- [ ] Can edit existing material prices

### Job History Tab
- [ ] Save a job (click "Save Estimate")
- [ ] Job appears in history with correct date, client, profit

### Settings Tab
- [ ] Rates are editable (Workshop, Fitting, Travel, Overhead)

---

## 🐛 COMMON ISSUES & FIXES

### Issue: "ModuleNotFoundError: No module named 'fpdf'"
**Fix**: Check `requirements.txt` has `fpdf2` (not `fpdf`)

### Issue: "Firebase: Could not load credentials"
**Fix**: Check Streamlit Secrets are formatted correctly as TOML under `[firebase]`

### Issue: App shows mock materials instead of real ones
**Fix**: Firebase secrets not set correctly — check the `private_key` has `\n` not actual newlines

### Issue: PDF download gives wrong filename
**Fix**: Already fixed in current code — downloads as `Quote.pdf`

### Issue: "protobuf" import error
**Fix**: `requirements.txt` now includes `protobuf>=4.25.0` — redeploy

---

## 📊 CURRENT APP VERSION SUMMARY

**Version**: v1.3 (2026-02-18)

### Features:
- ✅ **Unit Economics** — Per-item cost/sell/profit/margin breakdown
- ✅ **Batch Nesting Optimizer** — Minimizes material waste for batch jobs
- ✅ **Print Ready Toggle** — Zeros design time for ready artwork
- ✅ **Repeat Job Toggle** — Zeros design time for repeat orders
- ✅ **Design Hours** — Conditional design time billing
- ✅ **PDF Quote Export** — Professional branded PDF
- ✅ **Job History** — Save and review past quotes
- ✅ **Supplier Manager** — Manage material price lists
- ✅ **Dark/Light Theme** — Toggle between themes
- ✅ **Firebase Integration** — Cloud database for materials & jobs

### Files Changed in v1.3:
- `components/calc_v5.py` — Unit Economics section (fixed billable vs internal costs)
- `requirements.txt` — Added protobuf, pinned versions
- `utils/logic_engine.py` — Design hours, print ready, repeat job, nesting support

---

## 🔒 SECURITY NOTES

1. **Never commit `serviceAccountKey.json`** — it's in `.gitignore` ✅
2. **Use Streamlit Secrets** for all credentials — never hardcode keys
3. **Private GitHub repo** recommended for business tools
4. **Firebase rules** — Consider restricting Firestore access to authenticated users only

---

## 📞 SUPPORT

If deployment fails:
1. Check Streamlit Cloud logs (click "Manage app" → "Logs")
2. Look for the specific error message
3. Most common fix: requirements.txt or Secrets formatting

**Your app URL will be**: `https://daniel-signs-calc.streamlit.app`  
(or similar, based on your GitHub username and repo name)
