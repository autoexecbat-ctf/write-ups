#!/usr/bin/env python3
"""One-session gear prep for 9999 (user will fight personally):
1) equip shotgun (slot 0) 2) try armor-heavy in equip slots 0..3, print stats each
3) buy potions/antidotes/meals at quartermaster 4) upgrade shotgun at blacksmith while gold >= reserve.
Usage: CG_USER=.. CG_PASS=.. python3 gear_prep6.py [reserve_gold=60]
"""
import math, ssl, sys, time
from collections import deque

sys.path.insert(0, '/ctf/agent-5/scripts')
from protolib import msg
from router_client import login, Router
from websocket import create_connection, ABNF

RESERVE = int(sys.argv[1]) if len(sys.argv) > 1 else 60
TARGETS = {'station-gunsmith': (32.5, 18.5), 'station-outfitter': (30.5, 18.5),
           'station-quartermaster': (34.5, 18.5), 'station-blacksmith': (35.5, 27.5)}


def mm(rt, m, body):
    rq = 'matchmaking.v1.' + {
        'GetActiveRoom': 'GetActiveRoomCommand', 'LeaveRoom': 'LeaveRoomCommand',
        'GetQueueInfo': 'GetQueueInfoCommand', 'JoinRoom': 'JoinRoomCommand'}[m]
    rs = {'GetActiveRoom': 'matchmaking.v1.ActiveRoomEvent',
          'GetQueueInfo': 'matchmaking.v1.GetQueueInfoResponse',
          'JoinRoom': 'matchmaking.v1.JoinRoomResponse'}.get(m)
    return rt.call('matchmaking', '/matchmaking.v1.MatchmakingClientService/' + m, rq, body, rs)


toks = login()
rt = Router(toks)
for attempt in range(8):
    ar = mm(rt, 'GetActiveRoom', {})
    if ar.get('room_kind') == 'lobby':
        break
    if ar.get('room_id'):
        mm(rt, 'LeaveRoom', {'room_id': ar['room_id']})
    time.sleep(float(ar.get('retry_after_seconds') or 1) + 0.5)
    qi = mm(rt, 'GetQueueInfo', {'room_kind': 'lobby'})
    mm(rt, 'JoinRoom', {'room_kind': 'lobby', 'queue_generation': (qi or {}).get('queue_generation', '')})
    time.sleep(2)
ar = mm(rt, 'GetActiveRoom', {})
if ar.get('room_kind') != 'lobby':
    print('FATAL: could not enter lobby, room_kind =', ar.get('room_kind'), flush=True)
    sys.exit(1)
ws = create_connection(ar['room_url'], header=['Authorization: Bearer ' + toks['lobby']],
                       sslopt={'cert_reqs': ssl.CERT_REQUIRED}, timeout=20)
Env = msg('game.v1.RoomCommandEnvelope')
seq = [0]
state = {'pos': None, 'layout': None}
hits = []
rej = []


def send_cmd(field, fields=None):
    e = Env()
    seq[0] += 1
    e.input_seq = seq[0]
    c = getattr(e, field)
    c.SetInParent()
    for k, v in (fields or {}).items():
        if isinstance(v, dict):
            sub = getattr(c, k)
            sub.SetInParent()
            for k2, v2 in v.items():
                setattr(sub, k2, v2)
        else:
            setattr(c, k, v)
    try:
        ws.send(e.SerializeToString(), opcode=ABNF.OPCODE_BINARY)
    except Exception as ex:
        print('[send failed]', ex, flush=True)


def pump(t):
    ws.settimeout(0.5)
    deadline = time.time() + t
    while time.time() < deadline:
        try:
            op, data = ws.recv_data()
        except Exception:
            continue
        if op != ABNF.OPCODE_BINARY:
            continue
        Sn = msg('game.v1.Snapshot')()
        try:
            Sn.ParseFromString(data)
        except Exception:
            continue
        for env in Sn.events:
            w = env.WhichOneof('event')
            if not w:
                continue
            ev = getattr(env, w)
            if w == 'room_heartbeat':
                # MUST echo every heartbeat with its server_time_ms or the server closes the WS
                seq[0] += 1
                h = Env()
                h.input_seq = seq[0]
                h.heartbeat_echo.server_time_ms = ev.server_time_ms
                try:
                    ws.send(h.SerializeToString(), opcode=ABNF.OPCODE_BINARY)
                except Exception:
                    pass
            if w == 'room_layout':
                state['layout'] = {'width': ev.width, 'height': ev.height, 'mask': bytes(ev.not_wall_mask)}
            if w == 'player_state_changed':
                state['pos'] = (ev.state.position.x, ev.state.position.y)
            if w == 'room_command_rejected':
                rej.append(str(ev))
                print('[REJ]', str(ev).replace('\n', ' ')[:180], flush=True)
            if w == 'achievement_earned':
                print('[ACH]', str(ev).replace('\n', ' ')[:180], flush=True)
            if w == 'player_private_state_changed':
                hits.append(ev.state)


def cur():
    return hits[-1] if hits else None


def show(tag):
    s = cur()
    if not s:
        print('[%s] no state' % tag); return
    print('[%s] gold %s | eq %s | bag %s | hp %s dmg %s' % (
        tag, dict(s.wallet).get('gold'),
        [(e.slot, e.item_id, e.upgrade_level) for e in s.equipment],
        [(it.item_id, it.upgrade_level) for it in s.inventory],
        s.resolved_stats.max_hp, s.resolved_stats.damage_multiplier), flush=True)


def walk_to(spec):
    tx, ty = TARGETS[spec]
    lay = state['layout']
    w_, h_ = lay['width'], lay['height']
    mask = lay['mask']
    grid = [[1 if (mask[(y * w_ + x) >> 3] >> ((y * w_ + x) & 7)) & 1 else 0 for x in range(w_)] for y in range(h_)]
    sc = (int(state['pos'][0]), int(state['pos'][1])); gc = (int(tx), int(ty))
    q = deque([sc]); prev = {sc: None}
    while q:
        c = q.popleft()
        if c == gc:
            break
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + d[0], c[1] + d[1])
            if 0 <= n[0] < w_ and 0 <= n[1] < h_ and grid[n[1]][n[0]] and n not in prev:
                prev[n] = c; q.append(n)
    path = []
    c = gc
    while c:
        path.append(c); c = prev.get(c)
    path = path[::-1]
    wps = [(x + 0.5, y + 0.5) for x, y in path]
    wi = 0
    t0 = time.time()
    while time.time() - t0 < 180 and wi < len(wps):
        px, py = state['pos']
        gx, gy = wps[wi]
        dx, dy = gx - px, gy - py
        if abs(dx) < 0.45 and abs(dy) < 0.45:
            wi += 1; continue
        n = max(math.hypot(dx, dy), 1e-6)
        send_cmd('move', {'direction': {'x': dx / n, 'y': dy / n}})
        pump(0.05)
    return wi >= len(wps)


def listings(shop):
    out = {}
    for s in hits:
        for it in s.shop_listings:
            if it.shop_id == shop and it.stack_count > 0:
                out[it.item_listing_id] = (it.item_id, it.price)
    return out


send_cmd('init_room')
pump(3)
send_cmd('heartbeat_echo', {})
pump(1)
show('start')

# 0) BUY shotgun at gunsmith + armor-heavy at outfitter (skip if already owned)
def buy_at(station, shop_id, item_id, max_price=9999):
    s = cur()
    if s and any(it.item_id == item_id for it in s.inventory):
        print('[own]', item_id, flush=True); return True
    walk_to(station)
    send_cmd('interact', {'interact_host_id': station}); pump(3)
    send_cmd('refresh_shop', {'shop_id': shop_id}); pump(3)
    ls = listings(shop_id)
    cands = sorted(((price, lid) for lid, (iid, price) in ls.items() if iid == item_id and price <= max_price))
    for price, lid in cands:
        n0 = len(rej)
        send_cmd('buy_item', {'shop_id': shop_id, 'item_listing_id': lid,
                             'quantity': 1, 'expected_price': price}); pump(2)
        s = cur()
        if s and any(it.item_id == item_id for it in s.inventory):
            print('[bought]', item_id, 'gold', dict(s.wallet).get('gold'), flush=True); return True
        if len(rej) > n0:
            print('[buy fail]', item_id, rej[-1][:120], flush=True)
    print('[no listing]', item_id, 'at', shop_id, ls, flush=True); return False

buy_at('station-gunsmith', 'lobby.gunsmith', 'shotgun')
buy_at('station-outfitter', 'lobby.outfitter', 'armor-heavy', max_price=200)

# 1) equip shotgun into weapon slot 0
s = cur()
idx = [i for i, it in enumerate(s.inventory) if it.item_id == 'shotgun']
if idx:
    send_cmd('swap_slots', {'slot_a': {'kind': 0, 'index': idx[0]}, 'slot_b': {'kind': 1, 'index': 0}})
    pump(2)
show('after shotgun equip')

# 2) armor-heavy into equip slots 0..3
s = cur()
aidx = [i for i, it in enumerate(s.inventory) if it.item_id == 'armor-heavy']
for slot in range(4):
    if not aidx:
        break
    n0 = len(rej)
    send_cmd('swap_slots', {'slot_a': {'kind': 0, 'index': aidx[0]}, 'slot_b': {'kind': 1, 'index': slot}})
    pump(2)
    show('armor try slot %d' % slot)
    s = cur()
    if any(e.item_id == 'armor-heavy' for e in s.equipment):
        print('ARMOR EQUIPPED at slot', slot, flush=True)
        break
    aidx = [i for i, it in enumerate(s.inventory) if it.item_id == 'armor-heavy']

# 3) buy consumables at quartermaster
walk_to('station-quartermaster')
send_cmd('interact', {'interact_host_id': 'station-quartermaster'})
pump(3)
send_cmd('refresh_shop', {'shop_id': 'lobby.quartermaster'})
pump(3)
ls = listings('lobby.quartermaster')
print('[QM]', ls, flush=True)
want = {'health-potion-minor': 3, 'antidote': 1}
for want_item, qty in want.items():
    # dedupe listings by item_id, prefer lowest price; retry other listings on unknown_listing
    cands = sorted(((price, lid) for lid, (iid, price) in ls.items() if iid == want_item))
    got = 0
    for price, lid in cands:
        while got < qty:
            n0 = len(rej)
            send_cmd('buy_item', {'shop_id': 'lobby.quartermaster', 'item_listing_id': lid,
                                  'quantity': 1, 'expected_price': price})
            pump(2)
            s = cur()
            g = dict(s.wallet).get('gold', 0) if s else 0
            if len(rej) > n0:
                print('[buy fail]', want_item, rej[-1][:120], flush=True)
                break
            got += 1
            print('[buy]', want_item, got, '-> gold', g, flush=True)
            if g < price:
                break
    print('[buy done]', want_item, got, flush=True)
show('after buys')

# 4) upgrade equipped weapon at blacksmith while gold >= reserve
walk_to('station-blacksmith')
send_cmd('interact', {'interact_host_id': 'station-blacksmith'})
pump(3)
lvl = 0
while True:
    s = cur()
    g = dict(s.wallet).get('gold', 0)
    eq = [e for e in s.equipment if e.item_id == 'shotgun'] or [e for e in s.equipment]
    if not eq or g < RESERVE:
        print('[upgrade stop] gold', g, 'eq', [(e.item_id, e.upgrade_level) for e in s.equipment], flush=True)
        break
    n0 = len(rej)
    send_cmd('upgrade_item', {'item_instance_id': eq[0].item_instance_id,
                              'expected_level': eq[0].upgrade_level})
    pump(3)
    if len(rej) > n0:
        print('[upgrade rejected]', rej[-1][:140], flush=True)
        break
    s = cur()
    print('[upgraded] gold', dict(s.wallet).get('gold'),
          [(e.item_id, e.upgrade_level) for e in s.equipment],
          'dmg', s.resolved_stats.damage_multiplier, flush=True)
    lvl += 1
    if lvl > 30:
        break
show('final')
ws.close()
print('done')