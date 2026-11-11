"""Photo-kiosk webview WS client: connect, print frames, send actions.
Usage: CG_USER=.. CG_PASS=.. python3 kiosk6.py [--observe] | --cmd '<json>'
"""
import json
import sys
import threading
import time

import requests

sys.path.insert(0, '/ctf/agent-5/scripts')
from router_client import login, AUTH  # noqa: E402
from websignin import signin  # noqa: E402
from websocket import create_connection  # noqa: E402

ORIGIN_CACHE = '/tmp/agent6_kiosk_origin.txt'


def get_session(kind='photo-kiosk'):
    from router_client import Router
    toks = login()
    rt = Router(toks)
    P = '/matchmaking.v1.MatchmakingClientService/'

    def c(m, rq, body, rs=None):
        return rt.call('matchmaking', P + m, 'matchmaking.v1.' + rq, body, 'matchmaking.v1.' + rs if rs else None)
    ar = c('GetActiveRoom', 'GetActiveRoomCommand', {}, 'ActiveRoomEvent')
    if not (isinstance(ar, dict) and ar.get('room_kind') == kind and ar.get('room_url')):
        if isinstance(ar, dict) and ar.get('room_id'):
            c('LeaveRoom', 'LeaveRoomCommand', {'room_id': ar['room_id']})
        c('JoinRoom', 'JoinRoomCommand', {'room_kind': kind, 'queue_generation': ''}, 'JoinRoomResponse')
        for _ in range(30):
            ar = c('GetActiveRoom', 'GetActiveRoomCommand', {}, 'ActiveRoomEvent')
            if isinstance(ar, dict) and ar.get('room_kind') == kind and ar.get('room_url'):
                break
            time.sleep(2)
    if not (isinstance(ar, dict) and ar.get('room_url')):
        raise RuntimeError('join failed: %r' % (ar,))
    url = ar['room_url']
    signin_url = url if url.rstrip('/').endswith('signin') else url.rstrip('/') + '/_webview/signin'
    s, origin = signin(kind, signin_url)
    if not s:
        raise RuntimeError('signin failed')
    return s, origin


def ws_connect(origin, cookie_str):
    ws = create_connection('wss://' + origin.split('//')[1] + '/ws',
                           header=['Cookie: ' + cookie_str,
                                   'Origin: ' + origin,
                                   'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'],
                           timeout=10)
    return ws


def main():
    s, origin = get_session()
    print('origin', origin, file=sys.stderr)
    cookies = s.cookies.get_dict()
    cookie_str = '; '.join('%s=%s' % kv for kv in cookies.items())
    ws = ws_connect(origin, cookie_str)
    print('ws connected', file=sys.stderr)
    frames = []
    t0 = time.time()

    def reader():
        while time.time() - t0 < 20:
            try:
                ws.settimeout(5)
                data = ws.recv()
                print('FRAME:', data[:2000], flush=True)
                frames.append(data)
            except Exception as ex:
                if 'timed out' in str(ex):
                    continue
                print('reader exit', ex, flush=True)
                return
    th = threading.Thread(target=reader, daemon=True)
    th.start()
    time.sleep(8)
    if '--cmd' in sys.argv:
        cmd = json.loads(sys.argv[sys.argv.index('--cmd') + 1])
        print('SEND', cmd, flush=True)
        ws.send(json.dumps(cmd))
        time.sleep(5)
        ws.settimeout(3)
    th.join(timeout=10)
    ws.close()


if __name__ == '__main__':
    main()
