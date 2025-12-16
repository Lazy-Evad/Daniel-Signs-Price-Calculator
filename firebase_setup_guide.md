# How to Set Up Google Firebase for Your Calculator

To save your Jobs and Materials permanently in the cloud, you need to link this app to a free Google Firebase database.

### Step 1: Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **"Add project"**.
3. Name it (e.g., `DanielSignsCalculator`) and click Continue.
4. Disable Google Analytics (simpler setup) and click **"Create project"**.

### Step 2: Create the Database
1. Once the project is ready, click **"Build"** > **"Firestore Database"** in the left sidebar.
2. Click **"Create database"**.
3. Choose a location (e.g., `eur3 (europe-west)` for UK).
4. **Crucial:** Select **"Start in test mode"** (this allows read/write access easily for now).
5. Click **"Create"**.

### Step 3: Get the Service Key
1. Click the **Gear icon (Project Settings)** at the top left (next to Project Overview).
2. Go to the **"Service accounts"** tab.
3. Click **"Generate new private key"**.
4. Confirm by clicking **"Generate key"**.
5. This will download a file named something like `danielsignscalculator-firebase-adminsdk-xxxxx.json`.

### Step 4: Add to Project
1. Rename that downloaded file to exactly: `serviceAccountKey.json`.
2. Drag and drop it into this project folder alongside `main.py`.
   - **OR**: Open the file in Notepad, copy ALL the text, paste it to me here, and I will save it for you.

Once this file is present, the calculator will automatically switch from "Mock Mode" to "Live Database Mode".
