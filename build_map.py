import os
import subprocess
import urllib.parse
import math
import random
import string
from datetime import datetime


# ==========================================
# استخراج رابط الموقع (CNAME له أولوية مطلقة)
# ==========================================
def get_site_url():
    # إذا كان هناك CNAME → استخدم الدومين فقط (بدون اسم الريبو)
    if os.path.isfile("CNAME"):
        with open("CNAME", "r", encoding="utf-8") as f:
            domain = f.read().strip()
            if domain:
                return f"https://{domain}"

    # fallback إلى GitHub Pages (Project Pages)
    remote = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"]
    ).decode().strip()

    if remote.startswith("git@"):
        user, repo = remote.replace("git@github.com:", "").replace(".git", "").split("/")
    else:
        user, repo = remote.replace("https://github.com/", "").replace(".git", "").split("/")

    return f"https://{user}.github.io/{repo}"


SITE_URL = get_site_url()

# ==========================================
# إعدادات
# ==========================================
EXCLUDED_DIRS = {".git", ".github", "assets", "css", "js"}
EXCLUDED_FILES = {"404.html"}
URLS_PER_FILE = 5000


def last_modified(path):
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", path]
        ).decode().strip()
    except:
        return datetime.today().strftime("%Y-%m-%d")


def rand_name():
    return "m_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=9)) + ".xml"


def main():
    urls = []

    for root, dirs, files in os.walk(".", topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

        for file in files:
            if not file.endswith(".html"):
                continue
            if file in EXCLUDED_FILES:
                continue

            path = os.path.join(root, file).replace("\\", "/").lstrip("./")
            url = f"{SITE_URL}/{urllib.parse.quote(path)}"
            urls.append((url, last_modified(path)))

    sitemap_files = []
    parts = math.ceil(len(urls) / URLS_PER_FILE)

    for i in range(parts):
        filename = rand_name()
        sitemap_files.append(filename)

        content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]

        for url, mod in urls[i*URLS_PER_FILE:(i+1)*URLS_PER_FILE]:
            content.append(f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{mod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

        content.append("</urlset>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    index = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    today = datetime.today().strftime("%Y-%m-%d")

    for sm in sitemap_files:
        index.append(f"""
  <sitemap>
    <loc>{SITE_URL}/{sm}</loc>
    <lastmod>{today}</lastmod>
  </sitemap>""")

    index.append("</sitemapindex>")

    with open("map-root.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(index))

    print(f"✅ Done: {len(urls)} pages indexed")
    print("🚀 Submit ONLY map-root.xml to Google")


if __name__ == "__main__":
    main()
