"""Minimal main-router client for 401Unauthorized (reimplemented from CTFGame.Networking.Transport).

Credentials are read from env CG_USER / CG_PASS (see README) so they are not stored in the repo.

    python3 router_client.py ListAchievements
    python3 router_client.py call achievement /achievement.v1.AchievementClientService/SubmitFlag achievement.v1.AchievementClientServiceSubmitFlagRequest '{"flag":"..."}' achievement.v1.AchievementClientServiceSubmitFlagResponse
"""
import json
import os
import ssl
import sys
import uuid

import requests
from google.protobuf import json_format
from websocket import create_connection, ABNF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from protolib import msg  # noqa: E402

AUTH = 'https://auth.cg.chal.sh'
AUDS = ["main-router", "matchmaking", "achievement", "metadata", "mailbox", "dungeon", "lobby", "casino", "vault"]
CACHE = '/tmp/agent5_tokens_%s.json' % os.environ.get('CG_USER', 'default')  # per-account: agents share /tmp


def login(force=False):
    if not force and os.path.exists(CACHE):
        return json.load(open(CACHE))
    r = requests.post(AUTH + '/login', json={'account': os.environ['CG_USER'], 'password': os.environ['CG_PASS'],
                                             'aud': 'main-router'}, timeout=20)
    r.raise_for_status()
    j = r.json()
    toks = {'main-router': j['access_token'], '_refresh': j['refresh_token'], '_router': j.get('main_router_url')}
    for a in AUDS[1:]:
        t = requests.post(AUTH + '/token', json={'aud': a, 'refresh_token': j['refresh_token']}, timeout=20)
        if t.ok:
            toks[a] = t.json()['access_token']
        else:
            print('token', a, t.status_code, t.text, file=sys.stderr)
    json.dump(toks, open(CACHE, 'w'))
    return toks


def token_for(toks, aud):
    if aud not in toks:
        t = requests.post(AUTH + '/token', json={'aud': aud, 'refresh_token': toks['_refresh']}, timeout=20)
        print('token', aud, t.status_code, t.text[:200], file=sys.stderr)
        t.raise_for_status()
        toks[aud] = t.json()['access_token']
    return toks[aud]


class Router:
    def __init__(self, toks):
        self.toks = toks
        url = toks.get('_router') or 'wss://router.cg.chal.sh/'
        try:
            self.ws = create_connection(url, header=['Authorization: Bearer ' + toks['main-router']],
                                        subprotocols=['hkcert.messaging.v1'],
                                        sslopt={'cert_reqs': ssl.CERT_REQUIRED}, timeout=20)
        except Exception as e:
            if '401' not in str(e):
                raise
            toks.clear(); toks.update(login(force=True))
            self.ws = create_connection(url, header=['Authorization: Bearer ' + toks['main-router']],
                                        subprotocols=['hkcert.messaging.v1'],
                                        sslopt={'cert_reqs': ssl.CERT_REQUIRED}, timeout=20)

    def call(self, service, method, req_type, req_obj, resp_type=None, aud=None, metadata=None):
        Req = msg('clientmsg.v1.Request')
        r = Req()
        rid = str(uuid.uuid4())
        r.metadata.req_id = rid
        r.metadata.service = service
        r.metadata.method = method
        e = r.metadata.rpc_metadata.add()
        e.key = 'authorization'
        e.value = ('Bearer ' + token_for(self.toks, aud or service)).encode()
        for k, v in (metadata or {}).items():
            e = r.metadata.rpc_metadata.add()
            e.key = k
            e.value = v.encode() if isinstance(v, str) else v
        payload = msg(req_type)()
        if isinstance(req_obj, (dict, str)):
            json_format.Parse(req_obj if isinstance(req_obj, str) else json.dumps(req_obj), payload)
        else:
            payload = req_obj
        r.payload = payload.SerializeToString()
        self.ws.send(r.SerializeToString(), opcode=ABNF.OPCODE_BINARY)
        while True:
            op, data = self.ws.recv_data()
            if op != ABNF.OPCODE_BINARY:
                print('non-binary', op, data[:200])
                continue
            o = msg('clientmsg.v1.Outbound')()
            o.ParseFromString(data)
            if o.metadata.req_id != rid:
                self.on_push(o)
                continue
            if o.kind == 'error':
                return {'error': o.code, 'method': o.metadata.method}
            if resp_type:
                rm = msg(resp_type)()
                rm.ParseFromString(o.payload)
                return json_format.MessageToDict(rm, preserving_proto_field_name=True)
            return o.payload

    def on_push(self, o):
        print('[push]', o.kind, o.metadata.service, o.metadata.method, o.code, o.payload[:300], file=sys.stderr)


SHORT = {
    'ListAchievements': ('achievement', '/achievement.v1.AchievementClientService/ListAchievements',
                         'achievement.v1.ListAchievementsRequest', 'achievement.v1.ListAchievementsResponse'),
    'GetMyProfile': ('metadata', '/metadata.v1.MetadataClientService/GetMyProfile',
                     'metadata.v1.GetMyProfileRequest', 'metadata.v1.GetMyProfileResponse'),
    'ListAndClaimQuests': ('metadata', '/metadata.v1.MetadataClientService/ListAndClaimQuests',
                           'metadata.v1.ListAndClaimQuestsRequest', 'metadata.v1.ListAndClaimQuestsResponse'),
    'GetMervynStory': ('metadata', '/metadata.v1.MetadataClientService/GetMervynStory',
                       'metadata.v1.GetMervynStoryRequest', 'metadata.v1.GetMervynStoryResponse'),
    'GetLeaderboard': ('metadata', '/metadata.v1.MetadataClientService/GetLeaderboard',
                       'metadata.v1.GetLeaderboardRequest', 'metadata.v1.GetLeaderboardResponse'),
    'GetActiveRoom': ('matchmaking', '/matchmaking.v1.MatchmakingClientService/GetActiveRoom',
                      'matchmaking.v1.GetActiveRoomCommand', 'matchmaking.v1.ActiveRoomEvent'),
    'SubmitFlag': ('achievement', '/achievement.v1.AchievementClientService/SubmitFlag',
                   'achievement.v1.AchievementClientServiceSubmitFlagRequest',
                   'achievement.v1.AchievementClientServiceSubmitFlagResponse'),
}

if __name__ == '__main__':
    toks = login('--relogin' in sys.argv)
    argv = [a for a in sys.argv[1:] if a != '--relogin']
    rt = Router(toks)
    if argv[0] == 'call':
        svc, meth, rq, body = argv[1:5]
        rs = argv[5] if len(argv) > 5 else None
        print(json.dumps(rt.call(svc, meth, rq, body, rs), indent=1, ensure_ascii=False))
    else:
        svc, meth, rq, rs = SHORT[argv[0]]
        body = argv[1] if len(argv) > 1 else '{}'
        print(json.dumps(rt.call(svc, meth, rq, body, rs), indent=1, ensure_ascii=False))
