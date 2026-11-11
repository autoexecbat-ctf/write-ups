"""Dump the photo-kiosk hidden overview/settings screen (opened by edge swipe)."""
import json
import sys
import time

sys.path.insert(0, '/ctf/agent-6/scripts')
from kiosk_flow import Flow  # noqa: E402


def main():
    f = Flow()
    f.beat()
    got = f.recv(3)
    if not got or got[-1].get('screen') != 'overview':
        f.ws.send(json.dumps({'action': 'swipe', 'x1': 240, 'y1': 795, 'x2': 240, 'y2': 500, 'duration_ms': 400}))
        got = f.recv(3)
    if not got:
        print('NO FRAME')
        return
    g = got[-1]
    print('screen', g.get('screen'), 'accepts', g.get('accepts_text'), 'text_box', g.get('text_box'), 'link_box', g.get('link_box'), 'link_value', g.get('link_value'))
    for op in g['draw']:
        if op.get('op') == 'text':
            print('TXT "%s" (%s,%s) size %s color %s' % (op['text'], op['x'], op['y'], op.get('size'), op.get('color')))
        elif op.get('op') == 'rect' and op.get('w', 0) > 50 and op.get('h', 0) > 30:
            print('RECT (%s,%s) %sx%s %s' % (op['x'], op['y'], op['w'], op['h'], op.get('color')))
        elif op.get('op') == 'image':
            print('IMG', op)


if __name__ == '__main__':
    main()
