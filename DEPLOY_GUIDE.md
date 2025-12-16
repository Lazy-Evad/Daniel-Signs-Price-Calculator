# How to Deploy to Android (Streamlit Cloud)

### 1. Create a GitHub Repository
1. Go to [github.com/new](https://github.com/new).
2. Name it `daniel-signs-calc`.
3. Select **Public** (Private works but Streamlit Cloud sometimes needs permissions).
4. Click **Create repository**.
5. Upload ALL files from this folder EXCEPT:
   - `serviceAccountKey.json` (**NEVER UPLOAD THIS!**)
   - `.venv` folder
   - `__pycache__` folder

### 2. Connect to Streamlit
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select "Use existing repo" and find `daniel-signs-calc`.
4. Main file path: `main.py`.
5. Click **Deploy!**

### 3. Add the Database Key (The Magic Step)
The app will crash at first because it can't find the database. You need to give it the key securely.
1. On your deployed app dashboard, click "Manage App" (bottom right) or the **Settings (three dots)** inside the app > **Settings** > **Secrets**.
2. Copy the contents of your `serviceAccountKey.json` file.
3. Paste it into the "Secrets" box in this format:

```toml
[firebase]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."
```

(Basically, copy your JSON file content, and format it slightly so it sits under [`firebase`]).

**Easy Way to Format:**
Just open your `serviceAccountKey.json`, copy everything, and ask ChatGPT or Gemini: *"Convert this JSON to TOML format for Streamlit Secrets [firebase]"*.

### 4. Done!
You now have a URL like `https://daniel-signs-calc.streamlit.app`.
Open it on your Android phone and save it to your home screen!
