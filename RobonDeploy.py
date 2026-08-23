import os
import subprocess
import requests
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
LOCAL_PATH = os.getcwd()  # run script inside the folder
HTML_FILE = "index.html"

GITHUB_USERNAME = "sap586"
REPO_NAME = os.path.basename(LOCAL_PATH)  # folder name = repo name
TOKEN_FILE = "/Users/Sagar/Software/.gh_token"

with open(TOKEN_FILE, "r") as f:
    GITHUB_TOKEN = f.read().strip()



# -----------------------------
# 1. CREATE / UPDATE HTML PAGE
# -----------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{REPO_NAME}</title>
</head>
<body>
    <h1>Auto Deployment Test</h1>
    <p>Last updated: {datetime.now()}</p>
</body>
</html>
"""

with open(os.path.join(LOCAL_PATH, HTML_FILE), "w") as f:
    f.write(html_content)

print("✔ HTML page created/updated")

# -----------------------------
# 2. INITIALIZE GIT IF NEEDED
# -----------------------------
if not os.path.exists(os.path.join(LOCAL_PATH, ".git")):
    print("⚠ No git repo found — creating one")
    subprocess.run(["git", "init"], cwd=LOCAL_PATH)

# -----------------------------
# 3. CREATE GITHUB REPO IF NEEDED
# -----------------------------
repo_api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

response = requests.get(repo_api_url, headers=headers)

if response.status_code == 404:
    print("⚠ GitHub repo does not exist — creating it")

    create_url = "https://api.github.com/user/repos"
    data = {"name": REPO_NAME, "private": False}

    create_response = requests.post(create_url, json=data, headers=headers)

    if create_response.status_code == 201:
        print("✔ GitHub repo created")
    else:
        print("❌ Failed to create repo:", create_response.json())
        exit(1)
else:
    print("✔ GitHub repo already exists")

# -----------------------------
# 4. ADD REMOTE ORIGIN IF NEEDED
# -----------------------------
push_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

# Check if remote exists
remotes = subprocess.run(["git", "remote"], cwd=LOCAL_PATH, capture_output=True, text=True)

if "origin" not in remotes.stdout:
    subprocess.run(["git", "remote", "add", "origin", push_url], cwd=LOCAL_PATH)
    print("✔ Added remote origin")

# -----------------------------
# 5. COMMIT + PUSH
# -----------------------------
subprocess.run(["git", "add", "."], cwd=LOCAL_PATH)
subprocess.run(["git", "commit", "-m", "Auto-create and deploy"], cwd=LOCAL_PATH)
subprocess.run(["git", "push", "-u", "origin", "main"], cwd=LOCAL_PATH)

print("✔ Pushed to GitHub")

# -----------------------------
# 6. GitHub Pages auto-deploys
# -----------------------------
print("🚀 GitHub Pages will deploy automatically")




# -----------------------------
# 7. ENABLE GITHUB PAGES (with retry)
# -----------------------------
import time

pages_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/pages"
pages_data = {
    "source": {"branch": "main", "path": "/"}
}

print("⏳ Enabling GitHub Pages...")

for attempt in range(5):
    pages_response = requests.put(pages_url, json=pages_data, headers=headers)

    if pages_response.status_code in [201, 204, 202]:
        print("✔ GitHub Pages enabled")
        break

    print(f"⚠ Pages not ready yet (attempt {attempt+1}) — retrying...")
    time.sleep(5)
else:
    print("❌ Failed to enable GitHub Pages:", pages_response.json())






print(f"🌍 Your site will be live at: https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/")
