import base64
import hashlib

s = 'Y6XykQFxyOY='
challenge = base64.b64decode(s)

for i in range(1000000, 10000000):
    answer = 'crtA' + str(i)
    response = base64.b64decode(base64.b64encode(answer.encode('ascii')))
    h = hashlib.sha256(challenge + response).digest()
    if h.startswith(b'\x00\x00\x00'):
        print(base64.b64encode(answer.encode('ascii')))
        break
