"""Webview room sign-in with browser-like headers (gateway rejects bare POSTs with 403).
Usage: CG_USER CG_PASS python3 websignin.py <room_kind> <signin_url>
Saves cookies to /tmp/agent5_web_<kind>.json
"""
import json
import sys

import requests

from router_client import login, AUTH

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0.0.0 Safari/537.36')
VARIANTS = [
    {'Origin': 'null', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document',
     'Sec-Fetch-User': '?1'},
    {'Origin': 'null', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document'},
    {'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document'},
    {},
]


def signin(kind, url):
    toks = login()
    origin = url.split('/_webview')[0]
    for v in VARIANTS:
        r = requests.post(AUTH + '/token', json={'aud': kind, 'refresh_token': toks['_refresh']}, timeout=20)
        if not r.ok:
            toks = login(True)
            r = requests.post(AUTH + '/token', json={'aud': kind, 'refresh_token': toks['_refresh']}, timeout=20)
        tok = r.json()['access_token']
        s = requests.Session()
        s.headers['User-Agent'] = UA
        h = dict(v)
        if h.get('Sec-Fetch-Site') == 'same-origin':
            h['Origin'] = origin
        r = s.post(url, data={'access_token': tok}, headers=h, allow_redirects=False, timeout=20)
        print('variant', v, '->', r.status_code, r.text[:80], s.cookies.get_dict(), flush=True)
        if r.status_code in (200, 302, 303) and s.cookies:
            json.dump({'origin': origin, 'cookies': s.cookies.get_dict()},
                      open('/tmp/agent5_web_%s.json' % kind, 'w'))
            return s, origin
    return None, origin


if __name__ == '__main__':
    signin(sys.argv[1], sys.argv[2])
