#!/usr/bin/env python3
"""Save settings custom-config var and verify persistence (value echoes in form)."""
import requests, re, sys

BASE = "http://127.0.0.1:8765/"

s = requests.Session()
r = s.post(BASE + "admin.php?p=login", data={"sEmail": "contextgrave-admin@chal.sh",
         "sPass": "admin", "bAcceptLicense": "1", "iAcceptLicense": "true"}, timeout=30)
assert "p=logout" in r.text, "login failed"

def csrf(page="admin.php?p=settings"):
    rr = s.get(BASE + page, timeout=30)
    return re.search(r'name="sCsrfToken" value="([0-9a-f]+)"', rr.text).group(1)

tok = csrf()
val = sys.argv[1] if len(sys.argv) > 1 else 'TESTVAL123'
data = {"sCsrfToken": tok, "sOption": "save",
        "start_page": "1",
        "name_of_config_variable_here": val}
r = s.post(BASE + "admin.php?p=settings", data=data, timeout=30)
print("save:", r.status_code)
rr = s.get(BASE + "admin.php?p=settings", timeout=30)
m = re.search(r'name="name_of_config_variable_here"[^>]*value="([^"]*)"', rr.text)
print("persisted value:", m.group(1) if m else "FIELD NOT FOUND")
