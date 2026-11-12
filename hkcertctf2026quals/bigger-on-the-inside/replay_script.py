#!/usr/bin/env python3
"""Replay bigger_on_the_inside on ctf-player-9997, FREE (no gold):
bag is full (slots 0-19). Swap 2 stash porridges into bag OVERFLOW slots
20 and 21 -> 22 items. Then CreateParty(room_kind=dungeon) -> server's
'carrying more than bag holds' check fires the award (proven on 9801
at 2026-11-07T22:58:48Z). Never StartParty; never leave lobby."""
import json, math, os, ssl, sys, time
from collections import deque
sys.path.insert(0, '/ctf/agent-18/scripts/vendor')
sys.path.insert(0, '/ctf/agent-5/scripts')
from protolib import msg
import router_client
from websocket import create_connection, ABNF

TARGET = 'ctf-player-9997'
if os.environ.get('CG_USER') != TARGET:
    sys.exit('CG_USER must be ' + TARGET)
router_client.CACHE = '/ctf/agent-18/assets_extracted/.private_tokens_%s.json' % TARGET
P = '/matchmaking.v1.MatchmakingClientService/'
LOG = '/ctf/agent-18/assets_extracted/bigger_9997_replay.jsonl'
STATION_STASH = 'station-stash'
STASH_XY = (20.5, 8.5)
BAG, STASH = 0, 2
TARGET_OVERFLOW_SLOTS = [20, 21]


def jlog(tag, obj):
    with open(LOG, 'a') as f:
        f.write(json.dumps({'t': time.time(), 'tag': tag, 'data': obj}, default=str) + '\n')
    print('[%s]' % tag, str(obj)[:260], flush=True)


toks = router_client.login()
rt = router_client.Router(toks)


def mm(m, body):
    rq = 'matchmaking.v1.' + {'GetActiveRoom': 'GetActiveRoomCommand', 'LeaveRoom': 'LeaveRoomCommand',
                              'GetQueueInfo': 'GetQueueInfoCommand', 'JoinRoom': 'JoinRoomCommand',
                              'CreateParty': 'CreatePartyCommand', 'StartParty': 'StartPartyCommand',
                              'LeaveParty': 'LeavePartyCommand'}[m]
    rs = {'GetActiveRoom': 'ActiveRoomEvent', 'GetQueueInfo': 'GetQueueInfoResponse',
          'JoinRoom': 'JoinRoomResponse', 'CreateParty': 'PartyEvent', 'StartParty': 'PartyEvent',
          'LeaveParty': 'PartyEvent'}[m]
    return rt.call('matchmaking', P + m, rq, body, 'matchmaking.v1.' + rs)


for _ in range(10):
    ar = mm('GetActiveRoom', {})
    if ar.get('room_kind') == 'lobby':
        break
    if ar.get('room_id'):
        mm('LeaveRoom', {'room_id': ar['room_id']})
    time.sleep(2)
    qi = mm('GetQueueInfo', {'room_kind': 'lobby'})
    mm('JoinRoom', {'room_kind': 'lobby', 'queue_generation': qi.get('queue_generation', '')})
    time.sleep(3)
if ar.get('room_kind') != 'lobby':
    jlog('FATAL_not_in_lobby', ar); sys.exit(1)
jlog('lobby_ok', {'room_id': ar.get('room_id')})

Env = msg('game.v1.RoomCommandEnvelope')
Snap = msg('game.v1.Snapshot')
ws = create_connection(ar['room_url'], header=['Authorization: Bearer ' + toks['lobby']],
                       sslopt={'cert_reqs': ssl.CERT_REQUIRED}, timeout=20)
seq = [int(time.time() * 1000) % 1000000]
state = {'pos': None, 'layout': None, 'priv': None}
rej, ach = [], []


def send_cmd(field, fields=None):
    e = Env()
    seq[0] += 1
    e.input_seq = seq[0]
    c = getattr(e, field)
    c.SetInParent()
    for k, v in (fields or {}).items():
        if isinstance(v, dict):
            sub = getattr(c, k); sub.SetInParent()
            for k2, v2 in v.items():
                setattr(sub, k2, v2)
        else:
            setattr(c, k, v)
    ws.send(e.SerializeToString(), opcode=ABNF.OPCODE_BINARY)


def pump(t):
    ws.settimeout(0.5)
    d = time.time() + t
    while time.time() < d:
        try:
            op, data = ws.recv_data()
        except Exception:
            continue
        if op != ABNF.OPCODE_BINARY:
            continue
        Sn = Snap()
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
                seq[0] += 1
                h = Env(); h.input_seq = seq[0]
                h.heartbeat_echo.server_time_ms = ev.server_time_ms
                try:
                    ws.send(h.SerializeToString(), opcode=ABNF.OPCODE_BINARY)
                except Exception:
                    pass
            elif w == 'room_layout':
                state['layout'] = {'width': ev.width, 'height': ev.height, 'mask': bytes(ev.not_wall_mask)}
            elif w == 'player_state_changed':
                state['pos'] = (ev.state.position.x, ev.state.position.y)
            elif w == 'room_command_rejected':
                rej.append(str(ev).replace('\n', ' '))
                jlog('REJECT', rej[-1][:180])
            elif w == 'achievement_earned':
                d2 = str(ev).replace('\n', ' ')
                ach.append(d2)
                jlog('ACHIEVEMENT_EARNED', d2[:300])
            elif w == 'player_private_state_changed':
                state['priv'] = ev.state


def bag():
    p = state['priv']
    return sorted((it.slot, it.item_id) for it in (p.inventory if p else []))


def stash():
    p = state['priv']
    return sorted((it.slot, it.item_id) for it in (p.stash if p else []))


def walk_to(tx, ty):
    lay = state['layout']
    w_, h_, mask = lay['width'], lay['height'], lay['mask']
    ok = lambda x, y: (mask[(y*w_+x) >> 3] >> ((y*w_+x) & 7)) & 1
    sc, gc = (int(state['pos'][0]), int(state['pos'][1])), (int(tx), int(ty))
    q, prev = deque([sc]), {sc: None}
    while q:
        c = q.popleft()
        if c == gc:
            break
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0]+d[0], c[1]+d[1])
            if 0 <= n[0] < w_ and 0 <= n[1] < h_ and ok(*n) and n not in prev:
                prev[n] = c; q.append(n)
    path, c = [], gc
    while c:
        path.append(c); c = prev.get(c)
    wps = [(x+0.5, y+0.5) for x, y in path[::-1]]
    wi, t0 = 0, time.time()
    while time.time()-t0 < 150 and wi < len(wps):
        px, py = state['pos']
        dx, dy = wps[wi][0]-px, wps[wi][1]-py
        if abs(dx) < 0.45 and abs(dy) < 0.45:
            wi += 1; continue
        n = max(math.hypot(dx, dy), 1e-6)
        send_cmd('move', {'direction': {'x': dx/n, 'y': dy/n}})
        pump(0.05)


send_cmd('init_room', {})
pump(5)
jlog('start', {'bag_n': len(bag()), 'bag': bag(), 'stash_porridge': [s for s, i in stash() if 'porridge' in i]})

# ---- overflow slots 20 & 21 with 2 stash porridges (FREE swaps) ----
por_stash = [s for s, i in stash() if i == 'meal-barley-porridge'][:2]
if len(por_stash) < 2:
    jlog('FATAL_no_porridge_in_stash', {}); sys.exit(1)
walk_to(*STASH_XY)
send_cmd('interact', {'interact_host_id': STATION_STASH})
pump(3)
for src, dst in zip(por_stash, TARGET_OVERFLOW_SLOTS):
    n0 = len(rej)
    send_cmd('swap_slots', {'slot_a': {'kind': STASH, 'index': src},
                             'slot_b': {'kind': BAG, 'index': dst}})
    pump(2)
    if len(rej) > n0:
        jlog('swap_reject', {'src': src, 'dst': dst, 'rej': rej[-1][:150]})
    else:
        jlog('overflowed', {'stash_slot': src, 'bag_slot': dst, 'bag_n': len(bag())})
jlog('overflow_state', {'bag_n': len(bag()), 'bag': bag()})
pump(2)
ws.close()

# ---- trigger: CreateParty(room_kind=dungeon) — NO StartParty, stay in lobby ----
party = mm('CreateParty', {'room_kind': 'dungeon'})
jlog('party_created', {'party_id': party.get('party_id'), 'state': party.get('state')})
time.sleep(8)  # allow achievement push to land on lobby socket / router

# cleanup: leave party so 9997 stays clean in lobby
try:
    pid = party.get('party_id')
    if pid:
        mm('LeaveParty', {'party_id': pid})
        jlog('party_left', {'party_id': pid})
except Exception as ex:
    jlog('leave_party_err', str(ex)[:120])

# ---- verify ----
toks2 = router_client.login()
rt2 = router_client.Router(toks2)
resp = rt2.call('achievement', '/achievement.v1.AchievementClientService/ListAchievements',
                'achievement.v1.ListAchievementsRequest', {},
                'achievement.v1.ListAchievementsResponse')
rt2.ws.close()
entry = next((a for a in resp.get('achievements', []) if a.get('achievement_id') == 'bigger_on_the_inside'), None)
jlog('FINAL_VERIFY', entry)
json.dump(resp, open('/ctf/agent-18/assets_extracted/ach_9997_after_replay.json', 'w'), indent=1)
