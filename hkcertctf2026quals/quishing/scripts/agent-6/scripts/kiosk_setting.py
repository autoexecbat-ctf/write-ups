"""Open photo-kiosk setting screen and dump layout; optional tap coords as args."""
import json
import sys
import time

sys.path.insert(0, '/ctf/agent-6/scripts')
from kiosk_flow import Flow  # noqa: E402


def open_setting(f):
    got = f.recv(2)
    if not got or got[-1].get('screen') != 'overview':
        f.ws.send(json.dumps({'action': 'swipe', 'x1': 240, 'y1': 795, 'x2': 240, 'y2': 500, 'duration_ms': 400}))
        got = f.recv(3)
    if got and got[-1].get('screen') == 'overview':
        got = f.tap(432, 144, wait=3)
    return got


def dump(g):
    print('screen', g.get('screen'), 'theme', g.get('theme'), 'link_box', g.get('link_box'))
    print('link_value:', g.get('link_value'))
    for op in g['draw']:
        if op.get('op') == 'text':
            print('TXT "%s" (%s,%s) %s' % (op['text'], op['x'], op['y'], op.get('color')))
        elif op.get('op') == 'rect' and op.get('w', 0) > 60 and op.get('h', 0) > 30:
            print('RECT (%s,%s) %sx%s %s' % (op['x'], op['y'], op['w'], op['h'], op.get('color')))


def main():
    f = Flow()
    f.beat()
    got = open_setting(f)
    if not got:
        print('NO FRAME')
        return
    dump(got[-1])
    for arg in sys.argv[1:]:
        x, y = map(int, arg.split(','))
        f.beat()
        got = f.tap(x, y, wait=3)
        if got:
            dump(got[-1])


if __name__ == '__main__':
    main()
