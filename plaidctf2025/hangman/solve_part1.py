from pwn import context, remote, process
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Util.strxor import strxor
from collections import defaultdict
# context.log_level = 'DEBUG'


# below constant bytes from binary, renamed
# data = open('bin/libhash.so', 'rb').read()
# a1_xor_box = data[0x3060:0x3060+256]
# state_replace = data[0x3160:0x3160+256]
# indexshiftbox = data[0x3260:0x3260+240]
# kshiftbox = data[0x3360:0x3360+128]

a1_xor_box = bytes.fromhex('98e86cf491a7ee7bf521635c2c2f7cc88a9f40e460bd9bb6d66e03e0a5abbba270c94a9d59f3653e150a0cda06c32b2eaf0f7731d361a41992f0684911e178feaa084b53c5f979fc86552ad8675d5033727ecacd38a12d2539b5cb27d475cc897a3d483220a80ece52b7741fc282103595ec7f41dc51e7993b143a42b0defdeb24c6e24d64058bc1beff019ea028ef5f29566a71887dd9941eea1a76b3305b5aac04b89c8fbffb8066d146dd96850209c7f637dfd034620de50bc0c4e63c26a6b2455707e9d2aea336b917815eb41812fa4f6d47d7d51b908edb13ed3f8443877322a900696f8d1df2b1ba4c8c4e1c546b58f8f7ad23e3bc164497f1939a83cf')
state_replace = bytes.fromhex('c25318895ecf841576e7ac3dea7b30a11382c9588f1e55c4a7367dec3baae170ff6e25b463f2b9284bda9100d7460d9c2ebff465b22368f99a0b40d10697dc4dbc2d66f720b1fa6b0899d24394054edf6dfcb726f1602bbad948039245d49f0e81105bca1d8cc75635a4ef7ea93873e250c18a1bcc5d1687e4753eaf78e9a2330495de4f980942d3b0216afb2cbdf667d5440f9e49d8930261f0bb2afd6c27b639a8e372a5347fee8d1c57c61180cb5ae87932a374e5ae3f5ccd8617c0511a8b7aeba031e6773cadce5f148552c38819ab3a71e037a6ed7c1f8ec554831259c847d69d0cdb4a0190f36229b86ffeb52496074cdd0a9bd04122b3f869be2f64f5')
indexshiftbox = bytes.fromhex('ee389c0c49763c93951927c417a5bcf5cf46fd77fb5129855e662b7bf1396560e7c15fd89ebbf9e92d83a953cd45500423d2374ac06e42bdb1225224d463c9db8a31011a701c05728cd60a3a33efb58de055788e09a02f75b8d988aa148669c5dc4beb0784ac5426ec289056039dd7f0970bb3d38081b0c6594e91be36b9fcb7102e3d87e56d96160002997306da4f324cc33b2a944825622c8b98b2e6e25a71b6ea080da7897af7df1ee3437c3f351dccae1b82e86fd0c8b4923e34edd1670ec73041f4dd5c4d205812f815a161d5f3c2a4794021e46baba3a66af27e477f5b749f7d6818bf8fad13cbbaa86c64a2ca')
kshiftbox = bytes.fromhex('7d32092356362e3d050c7e495c4d474543101e1b5f1622026679135b784c7a57205a0a4f3b333012530860354117243e461f765e7129483a4e6d2c4a7c522d381d0e672f61113427441a6a312a3f28750f774b14636e69253c641821705804506b655d0d74260700620b017b556f397f4051597368192b6c54420306151c7237')


def hash_compute(bandit_salt, input_data):
    """
    Compute a hash from the input data.

    Args:
        bandit_salt: A bytes-like object representing the bandit input
        input_data: A bytes-like object representing the input data

    Returns:
        A list of 2 integers (the computed hash)
    """
    # Allocate memory for block_data (16 bytes)
    block_data = bytearray(16)

    # Copy values from a1 to ptr
    ptr = bandit_salt

    # Process data in chunks of 16 bytes
    i = 0
    while i <= len(input_data):
        for j in range(16):
            if j + i >= len(input_data):
                block_data[j] = len(input_data) - i
            else:
                block_data[j] = input_data[i + j]
        # print(block_data)
        assert strxor(inner(b'\x00' * 15 + b'\x01', block_data, bandit_salt), inner(b'\x00' * 14 + b'\x01\x00', block_data, bandit_salt)) == strxor(inner(b'\x00' * 16, block_data, bandit_salt), inner(b'\x00' * 14 + b'\x01\x01', block_data, bandit_salt))
        old_ptr = ptr
        ptr = inner(ptr, block_data, bandit_salt)
        # print(strxor(inner_mix(old_ptr), ptr))
        i += 16

    return ptr


def inner(ptr, block_data, bandit_salt):
    """
    Manipulate bytes in a1 based on a2 and a3.

    Args:
        ptr: the
        block_data: A bytearray of 16 bytes
        bandit_salt: A list of 2 integers (QWORDs)

    Returns:
        Nothing (modifies a1 in-place)
    """
    # Convert a1 to a bytearray for byte-level operations
    ptr2 = bytearray(ptr)

    state = bytearray(16)

    for i in range(15):  # 0 to 14
        for j in range(16):  # 0 to 15
            index = j | (16 * i)
            s1 = indexshiftbox[index] >> 4
            s2 = indexshiftbox[index] & 0xF

            state[j] = state_replace[ptr2[j] ^ a1_xor_box[bandit_salt[s1] ^ bandit_salt[s2] ^ block_data[j]]] # state_replace is linear.
            ptr2[j] = 0

        # state, ptr2 = ptr2, state
        
        # scrambles bits of ptr

        for k in range(128):  # 0 to 127
            new_byte = k >> 3
            new_bit = k & 7

            original_byte = kshiftbox[k] >> 3
            original_bit = kshiftbox[k] & 7


            ptr2[new_byte] ^= (((state[original_byte] >> original_bit) & 1) << new_bit)

    return bytes(ptr2)


words = open('dictionary.txt').read().split('\n')
word_set = defaultdict(list)
candidates = []
for w in words:
    if len(w) > 5:
        continue
    word_set[w[:4]].append(w)
for k,v in word_set.items():
    if len(v) < 5:
        continue
    if k not in v:
        continue
    #print(k, v)
    candidates.append((k,v))
print('cand', len(candidates))
# [
#     ('shin', ['shin', 'shine', 'shing', 'shino', 'shins', 'shinu', 'shiny']),
#     .....,
# ]



io = remote('hangman.chal.pwni.ng', 6001)
#io = remote('localhost', 6001)
# custom own salt
salt = b'abcdefghijklmnop'

# 50 rounds
for word_4, word_5s in candidates[:50]:

    # store correct position for each character, 1-indexed
    loc_map = defaultdict(list)
    for idx, c in enumerate(word_4):
        loc_map[c].append(idx+1)

    io.recvuntil(b'Salt: ')
    bandit_salt = bytes.fromhex(io.recvline().strip().decode())

    payload = word_4.encode() + b'\x00' + b'\x00' + salt
    hsh = hash_compute(bandit_salt, payload)
    io.sendlineafter(b'Your hash: ', hsh.hex().encode())
    io.sendlineafter(b'Length of your word: ', b'5')
    failed_count = 0

    while failed_count < 5:

        io.recvuntil(b'The bandit guesses: ')
        guess = io.recv(1).decode()
        if guess in word_4:
            for loc in loc_map[guess]:
                io.sendlineafter(b"or an empty line if it ain't there) ", str(loc).encode())
            io.sendlineafter(b"or an empty line if it ain't there) ", b'')
        else:
            io.sendlineafter(b"or an empty line if it ain't there) ", b'')
            failed_count += 1
    io.sendlineafter(b'Blast it all! What was your word?! ', word_4.encode() + b'\x00')
    io.sendlineafter(b'And the salt (in hex)? ', salt.hex().encode())

print(io.recvall())