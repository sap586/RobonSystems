import os
import subprocess
import requests
from datetime import datetime
import time

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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robon Systems</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            color: #222;
        }}

        header {{
            background: #111;
            color: #fff;
            padding: 20px;
            text-align: center;
        }}

        .container {{
            width: 90%;
            max-width: 900px;
            margin: 40px auto;
        }}

        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .quote {{
            font-size: 1.3rem;
            font-style: italic;
            text-align: center;
            margin-top: 20px;
            color: #444;
        }}

        marquee {{
            font-size: 1.4rem;
            font-weight: bold;
            color: #b30000;
            margin-top: 30px;
        }}
    </style>
</head>

<body>

<header>
    <h1>Robon Systems</h1>
    <p>Innovating the Future of Robotics Machinery</p>
</header>

<div class="container">

    <div class="section">
        <h2>About Us</h2>
        <p>
            Robon Systems designs and builds advanced robotics machinery for industrial automation,
            precision manufacturing, and next‑generation smart factories. Our mission is to create
            intelligent machines that enhance productivity, safety, and efficiency across industries.
        </p>
    </div>

    <div class="section">
        <h2>Our Focus</h2>
        <ul>
            <li>Industrial Robotics</li>
            <li>Automation Systems</li>
            <li>Machine Vision Integration</li>
            <li>Custom Robotic Machinery</li>
            <li>Smart Manufacturing Solutions</li>
        </ul>
    </div>

    <div class="quote">
        “Robotics and automation aren’t just about machines — they’re about building a future where precision, efficiency, and intelligence work together.”
    </div>

    <marquee>🚧 Under Construction 🚧</marquee>

</div>

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
pages_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/pages"
pages_data = {"source": {"branch": "main", "path": "/"}}

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
