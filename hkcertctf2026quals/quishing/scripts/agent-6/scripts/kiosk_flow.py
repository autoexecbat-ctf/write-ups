"""Photo-kiosk full-flow driver with layout dump.
Usage: python3 kiosk_flow.py [pic_x] [pic_y] [effect_x] [url]
"""
import json
import sys
import time

sys.path.insert(0, '/ctf/agent-6/scripts')
from kiosk6 import get_session, ws_connect  # noqa: E402


class Flow:
    def __init__(self):
        s, origin = get_session()
        self.s = s
        self.origin = origin
        self.cs = '; '.join('%s=%s' % kv for kv in s.cookies.get_dict().items())
        self.ws = ws_connect(origin, self.cs)
        self.ws.settimeout(1.5)

    def recv(self, wait=2.5):
        end = time.time() + wait
        out = []
        while time.time() < end:
            try:
                out.append(json.loads(self.ws.recv()))
            except Exception:
                time.sleep(0.1)
        return out

    def tap(self, x, y, wait=2.0):
        self.ws.send(json.dumps({'action': 'tap', 'x': x, 'y': y}))
        return self.recv(wait)

    def text(self, v, wait=2.0):
        self.ws.send(json.dumps({'action': 'text', 'value': v}))
        return self.recv(wait)

    def show(self, tag, fr):
        if not fr:
            print('[%s] NO FRAME' % tag)
            return None
        f = fr[-1]
        texts = [op['text'] for op in f['draw'] if op.get('op') == 'text']
        print('[%s] %s | %s' % (tag, f.get('screen'), ' | '.join(texts)))
        return f

    def dump(self, f):
        for op in f['draw']:
            if op.get('op') == 'image':
                print('  IMG', op['name'], op.get('x'), op.get('y'), op.get('w'), op.get('h'))
            elif op.get('op') == 'text':
                print('  TXT "%s" (%s,%s)' % (op['text'], op['x'], op['y']))
        print('  accepts_text', f.get('accepts_text'), 'text_box', f.get('text_box'), 'link_box', f.get('link_box'), 'link_value', f.get('link_value'))

    def beat(self):
        try:
            self.s.post(self.origin + '/_webview/heartbeat', timeout=10)
        except Exception:
            pass


def main():
    f = Flow()
    f.beat()
    f.recv(2)
    # attract -> gallery
    g = f.show('gallery', f.tap(240, 684))
    f.dump(g)
    f.beat()
    # gallery -> effect via picture (HKCERT 80,300)
    e = f.show('effect', f.tap(80, 300))
    f.dump(e)
    f.beat()
    # effect: Cool (240,586)
    e2 = f.show('cool', f.tap(240, 586))
    f.dump(e2)
    f.beat()
    # share
    sh = f.show('share', f.tap(240, 724))
    f.dump(sh)
    f.beat()


if __name__ == '__main__':
    main()
