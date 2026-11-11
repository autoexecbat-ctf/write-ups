"""Photo-kiosk driver (agent-5). Runs a sequence of actions and prints every frame.
Usage: CG_USER=.. CG_PASS=.. python3 kiosk5.py 'tap:240:684' 'text:VALUE' 'swipe:x1:y1:x2:y2' 'wait:3' ...
Uses agent-6's kiosk6 session helper (joins photo-kiosk room, webview signin, WS).
"""
import json
import sys
import time

sys.path.insert(0, '/ctf/agent-6/scripts')
from kiosk6 import get_session, ws_connect  # noqa: E402

VERBOSE = '-v' in sys.argv


def show(f):
    texts = [op['text'] for op in f.get('draw', []) if op.get('op') == 'text']
    extra = {k: v for k, v in f.items() if k not in ('draw',)}
    print('  FRAME', json.dumps(extra, ensure_ascii=False)[:600])
    print('   TXT', ' | '.join(texts)[:900])
    if VERBOSE:
        for op in f.get('draw', []):
            if True:
                print('    ', op)


def main():
    s, origin = get_session()
    cs = '; '.join('%s=%s' % kv for kv in s.cookies.get_dict().items())
    ws = ws_connect(origin, cs)
    ws.settimeout(0.5)

    def drain(wait=2.0):
        end = time.time() + wait
        while time.time() < end:
            try:
                msg = ws.recv()
            except Exception:
                continue
            try:
                show(json.loads(msg))
            except Exception:
                print('  RAW', msg[:500])

    drain(2)
    for a in [x for x in sys.argv[1:] if x != '-v']:
        p = a.split(':', 1)
        kind = p[0]
        if kind == 'tap':
            x, y = p[1].split(':')
            act = {'action': 'tap', 'x': float(x), 'y': float(y)}
        elif kind == 'text':
            act = {'action': 'text', 'value': p[1] if len(p) > 1 else ''}
        elif kind == 'swipe':
            x1, y1, x2, y2 = map(float, p[1].split(':'))
            act = {'action': 'swipe', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'duration_ms': 400}
        elif kind == 'raw':
            act = json.loads(p[1])
        elif kind == 'wait':
            drain(float(p[1]))
            continue
        else:
            continue
        print('>>>', json.dumps(act))
        ws.send(json.dumps(act))
        drain(2)
        try:
            s.post(origin + '/_webview/heartbeat', timeout=10)
        except Exception:
            pass


if __name__ == '__main__':
    main()
