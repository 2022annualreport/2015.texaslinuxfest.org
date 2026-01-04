import os
import subprocess
import urllib.parse
import random
import string
import math
from datetime import datetime

# =============================
# Detect domain from CNAME
# =============================
def get_site_url():
    if os.path.exists("CNAME"):
        with open("CNAME", "r", encoding="utf-8") as f:
            domain = f.read().strip()
            if domain:
                return f"https://{domain}"
    raise Exception("CNAME file not found")

SITE_URL = get_site_url()

# =============================
EXCLUDED_DIRS = {
    ".git", ".github", "assets", "css", "js"
}

EXCLUDED_FILES = {
    "index.html",
    "404.html"
}

URLS_PER_FILE = 3000  # آمن جدًا لجوجل

# =============================
def last_modified(path):
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", path],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        return datetime.today().strftime("%Y-%m-%d")

def rand_name():
    return "m_" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=12)
    ) + ".xml"

# =============================
urls = []

for root, dirs, files in os.walk(".", topdown=True):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

    for file in files:
        if not file.endswith(".html"):
            continue
        if file in EXCLUDED_FILES:
            continue

        path = os.path.join(root, file).replace("\\", "/").lstrip("./")

        if path == "index.html":
            continue

        url = f"{SITE_URL}/{urllib.parse.quote(path)}"
        urls.append((url, last_modified(path)))

if not urls:
    print("⚠️ No internal pages found")
    exit(0)

# =============================
# Split sitemaps
# =============================
parts = math.ceil(len(urls) / URLS_PER_FILE)
sitemap_files = []

for i in range(parts):
    filename = rand_name()
    sitemap_files.append(filename)

    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url, mod in urls[i * URLS_PER_FILE:(i + 1) * URLS_PER_FILE]:
        content.append(
f"""  <url>
    <loc>{url}</loc>
    <lastmod>{mod}</lastmod>
  </url>"""
        )

    content.append("</urlset>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

# =============================
# Random index name
# =============================
index_name = rand_name()

today = datetime.today().strftime("%Y-%m-%d")

index = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
]

for sm in sitemap_files:
    index.append(
f"""  <sitemap>
    <loc>{SITE_URL}/{sm}</loc>
    <lastmod>{today}</lastmod>
  </sitemap>"""
    )

index.append("</sitemapindex>")

with open(index_name, "w", encoding="utf-8") as f:
    f.write("\n".join(index))

# =============================
# robots.txt (auto update)
# =============================
robots = f"Sitemap: {SITE_URL}/{index_name}\n"

with open("robots.txt", "w", encoding="utf-8") as f:
    f.write(robots)

print("✅ Random sitemap generated")
print(f"🧩 Index file: {index_name}")
print(f"📄 Pages indexed: {len(urls)}")
