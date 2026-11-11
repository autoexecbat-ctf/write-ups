"""Set a custom QR link in photo-kiosk settings, then walk back and share.
Usage: python3 kiosk_setlink.py '<new-link-value>'
"""
import json
import sys
import time

sys.path.insert(0, '/ctf/agent-6/scripts')
from kiosk_flow import Flow  # noqa: E402

SWIPE = {'action': 'swipe', 'x1': 240, 'y1': 795, 'x2': 240, 'y2': 500, 'duration_ms': 400}


def dump(g):
    print('screen', g.get('screen'), 'link_box', g.get('link_box'), 'accepts', g.get('accepts_text'), 'text_box', g.get('text_box'))
    print('link_value', g.get('link_value'))
    for op in g['draw']:
        if op.get('op') == 'text':
            print('TXT "%s" (%s,%s)' % (op['text'], op['x'], op['y']))


def main():
    newlink = sys.argv[1] if len(sys.argv) > 1 else None
    f = Flow()
    f.beat()
    got = f.recv(2)
    if not got or got[-1].get('screen') != 'overview':
        f.ws.send(json.dumps(SWIPE))
        got = f.recv(3)
    if got and got[-1].get('screen') == 'overview':
        got = f.tap(124, 144, wait=3)
    if not got or got[-1].get('screen') != 'setting':
        # maybe swipe needed to center Setting card first
        f.ws.send(json.dumps({'action': 'swipe', 'x1': 400, 'y1': 300, 'x2': 100, 'y2': 300, 'duration_ms': 400}))
        got = f.recv(2)
        if got and got[-1].get('screen') == 'overview':
            got = f.tap(240, 144, wait=3)
    g = got[-1]
    dump(g)
    f.beat()
    # find Set button: dump rects
    for op in g['draw']:
        if op.get('op') == 'rect' and op.get('w', 0) > 100 and op.get('h', 0) > 40 and op.get('y', 0) > 300:
            print('CAND SET BTN (%s,%s) %sx%s' % (op['x'], op['y'], op['w'], op['h']))
    # text field is link_box (32,212,416,72) -> sendField: accepts_text False -> sends link value
    if newlink:
        f.ws.send(json.dumps({'action': 'text', 'value': newlink}))
        got = f.recv(3)
        if got: dump(got[-1])
        f.beat()


if __name__ == '__main__':
    main()
