import sys
import json
import string
from pwn import remote, process
from Crypto.Util.number import isPrime

def send(io, user, msg):
    payload = '%s %s' % (user, json.dumps({'type':'communicate', 'ciphertext': msg.hex()}).replace(' ', ''))
    io.sendlineafter(b'  ', payload.encode())

def recv(io):
    res = json.loads(io.recvline().decode().strip())
    if 'ciphertext' in res:
        res['ciphertext'] = bytes.fromhex(res['ciphertext'])
    return res

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca18217c32905e462e36ce3be39e772c180e86039b2783a2ec07a28fb5c55df06f4c52c9de2bcbf6955817183995497cea956ae515d2261898fa051015728e5a8aacaa68ffffffffffffffff

assert isPrime(p)
assert isPrime((p-1)//2)

if __name__ == '__main__':

    if len(sys.argv) != 2 or sys.argv[1] not in ['remote', 'local']:
        raise Exception('run "python solve.py local" or "python solve.py remote"')

    mode = sys.argv[1]

    if mode == 'remote':
        io = remote('c24b-pigeon-2.hkcert24.pwnable.hk', 1337, ssl=True)
    elif mode == 'local':
        io = process(['python', 'chall.py'])

    alice_pub = recv(io)
    byron_pub = recv(io)
    alice_done = recv(io)
    send(io, 'byron', alice_done['ciphertext'])
    byron_flag = recv(io)
    send(io, 'alice', byron_flag['ciphertext'])
    alice_flag = recv(io)

    nonce = alice_flag['ciphertext'][:8]
    enc = alice_flag['ciphertext'][8:]

    encc = b''

    flag = ''

    # we knew the flag length
    # 21 to 67
    #for flag_idx in range(46):
    while not flag or (flag and flag[-1] != '}'):

        flag_idx = len(flag)

        found = False

        for c in string.printable[:95]:

            flag_test = flag + c

            # first 21 bytes are the known prefix of the message 'the flag is hkcert24{'
            enc_c_test = enc[:21+flag_idx] +  (ord(c) ^ ord('}') ^ enc[flag_idx+21]).to_bytes(1, byteorder='little')
            enc_test = nonce + enc_c_test

            send(io, 'byron', enc_test)
            test = recv(io)
            send(io, 'alice', test['ciphertext'])
            check = recv(io)

            if len(check['ciphertext']) == 10:   # length 8 (nonce) + length 2 ":)"
                found = True
                flag = flag_test
                encc = enc_c_test
                print('hkcertctf24{' + flag)
                break

        if not found:
            raise Exception(f'something wrong at {flag_idx}')

    io.close()