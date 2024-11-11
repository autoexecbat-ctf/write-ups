# sage --python *.py
from sage.all import *

def tobin32(num):
    return bin(num)[2:].zfill(32)

def get_known_bits(intervals):
    known_bits = {}
    start = 0
    for num, mbti in intervals:
        a = tobin32(int(round(start / 201 * 0x7fffff)))
        b = tobin32(int(round(num / 201 * 0x7fffff)))
        for idx, (bit1, bit2) in enumerate(zip(a, b)):
            if bit1 != bit2:
                break
        known_bits[mbti] = a[9:idx]    # top 9 bits are thrown away due to & 0x7fffff from the 32-bit state
        start = num
    return known_bits


def get_seed(name):
    char_list = '0123456789abcdefghijklmnopqrstuvwxyz'
    seed = 0
    for c in name:
        seed = seed * 0x24 + char_list.index(c)
    return seed


def states_to_vec(state):
    g = GF(2)

    vec = []

    for s in state:
        for j in bin(s)[2:].zfill(32):
            vec.append(g(int(j)))
    vec = vector(g, vec)
    return vec

# contruct matrix
"""
# this is xorshift128
t = x[3]
s = x[0]
x[3] = x[2]
x[2] = x[1]
x[1] = x[0]
t = x[3] ^ (x[3] << 11) ^ ((x[3] ^ (x[3] << 11)) >> 8)
x[0] = t ^ x[0] ^ (x[0] >> 19)
"""
def get_mat():
    g = GF(2)
    mat = []

    # the 32 bits of state[0]
    for i in range(32):
        row = [g(0)] * 32 * 4
        row[0 * 32 + i] = g(1)

        if i >= 19:
            row[0 * 32 + i - 19] += g(1)

        row[3 * 32 + i] = g(1)
        if i <= 20:
            row[3 * 32 + i + 11] += g(1)
        if 8 <= i <= 28:
            row[3 * 32 + i + 3] += g(1)
        if 8 <= i:
            row[3 * 32 + i - 8] += g(1)

        mat.append(row)

    # the 32 bits of state[1]
    for i in range(32):
        row = [g(0)] * 32 * 4
        row[0 * 32 + i] = g(1)
        mat.append(row)

    # the 32 bits of state[2]
    for i in range(32):
        row = [g(0)] * 32 * 4
        row[1 * 32 + i] = g(1)
        mat.append(row)

    # the 32 bits of state[3]
    for i in range(32):
        row = [g(0)] * 32 * 4
        row[2 * 32 + i] = g(1)

        mat.append(row)

    mat = Matrix(g, mat)
    return mat

def get_state(seed):
    state = [seed]
    for _ in range(3):
        state.append((state[-1] * 0x6C078965 + 1) & 0xffffffff)
    state = state[::-1]
    return state

def check_state(state):
    """ check if a given initial state is valid
    """
    seed = state[3]
    return get_state(seed) == state


def vec_to_state(state_vec):
    res = []
    for i in range(4):
        res.append(int(''.join([str(j) for j in state_vec[i*32:i*32+32]]), 2))
    return res

def get_rand(state):
    return state[0] & 0x7fffff

def state_to_name(state):
    char_list = '0123456789abcdefghijklmnopqrstuvwxyz'
    num = state[3]
    name = ''
    for _ in range(7):
        name = char_list[num % 0x24] + name
        num = num // 0x24
    return name

def get_mbti(val: int):
    num = (val / (0x7FFFFF)) * 201

    if num < assign[0][0]:
        return assign[0][1]
    for idx, (aa, s) in enumerate(assign):
        if assign[idx][0] < num < assign[idx+1][0]:
            return assign[idx+1][1]
    return assign[-1][1]


assign = [
    (3,  'INFJ'),
    (12, 'INFP'),
    (28, 'ENFP'),
    (33, 'ENFJ'),
    (37, 'INTJ'),
    (44, 'INTP'),
    (50, 'ENTP'),
    (54, 'ENTJ'),
    (77, 'ISTJ'),
    (105, 'ISFJ'),
    (122, 'ESTJ'),
    (147, 'ESFJ'),
    (158, 'ISTP'),
    (176, 'ISFP'),
    (184, 'ESTP'),
    (201, 'ESFP'),
]

known_bits_data = get_known_bits(assign)

# note this is just for generating the 50 mbti outputs for demonstrating running this solve script
# the actual 50 mbtis output is in fact from reverse engineering the Unity.
flags = ['1','4m','on3','5t4r','und3r','c4e1um']

mat = get_mat()

for idx, name in enumerate(flags):

    stage = idx + 1
    print('stage', stage)

    ################## getting the target MBTI results to do the crypto part ##################
    seed = get_seed(name)
    state = get_state(seed)
    state_vec = states_to_vec(state)

    # generate the 50 answers that are the same as what we get from the binary
    target_mbtis = []
    for i in range(50):
        res = mat**(i+1) * state_vec
        state = (vec_to_state(res))
        num = get_rand(state)
        mbti = get_mbti(num)
        target_mbtis.append(mbti)
    ##################                        END                            ##################


    # then we start the real solve script here with the given target_mbtis
    linear_eq_mat = []
    linear_eq_vec = []

    # append equations due to known random number bits from the 50 given mbtis
    for idx, mbti in enumerate(target_mbtis):
        known_bits_seg = known_bits_data[mbti]
        mat_n = mat ** (idx+1)
        for bit_idx, bit in enumerate(known_bits_seg):
            linear_eq_mat.append(mat_n[9+bit_idx])    # top 9 bits were thrown away for the output random number, the known bits are from 10th (index 9)
            linear_eq_vec.append(bit)

    # append equations due to known initial seed bits (lower stage means more known 0 bits)
    # seed is at the 4th of the 4 32-bit numbers of the state
    known_bits_count = 32 - int(36**stage).bit_length()

    for i in range(known_bits_count):
        linear_eq_mat.append([0]*(96+i) + [1] + [0]*(31-i))
        linear_eq_vec.append(0)

    # as pointed out from author TWY, we can utilize the last 2 bits in consecutive 32-bit number in the states
    """
    for the LCG multiplier, 1812433253 mod 4 = 1

    for the last 2 bits, 
    state * multiplier + 1 = next state
    00 * 01 + 1 = 01
    01 * 01 + 1 = 10
    10 * 01 + 1 = 11
    11 * 01 + 1 = 00

    ab * 01 + 1 = cd
    which gives a + b + c == 0 and b + d == 1
    """
    for i in range(3):
        linear_eq_mat.append((2-i)*32*[0] + [0]*30 + [1] + [0] + [0]*30 + [1, 1] + [0]*32*i)
        linear_eq_vec.append(0)

        linear_eq_mat.append((2-i)*32*[0] + [0]*31 + [1] + [0]*31 + [1] + [0]*32*i)
        linear_eq_vec.append(1)

    if len(linear_eq_mat) <= 128:

        print(f'found no. of equations = {len(linear_eq_mat)}')

        brute_bits = 128 - len(linear_eq_mat)

        # 128 equations may not be enough, +2 for safety
        brute_bits += 2

        print(f'{brute_bits} bits to brute force...')


        # stage 5 solution at between 16800 to 16900
        # stage 6 solution at between 900 to 1000
        # brute force first few bits of the initial state
        # note that the seed (with some known bits) is at the last element (4th element) of the state
        for brute_num in range(2**brute_bits):

            test_bits = bin(brute_num)[2:].zfill(brute_bits)

            mat_test = linear_eq_mat[:]
            vec_test = linear_eq_vec[:]

            for row_idx, test_bit in enumerate(test_bits):
                mat_test.append([0]*row_idx + [1] + [0]*(127-row_idx))
                vec_test.append(test_bit)

            g = GF(2)
            mat_test = Matrix(g, mat_test)
            vec_test = vector(g, vec_test)
            try:
                state_vec = mat_test.solve_right(vec_test)
            except Exception as e:
                continue
            state = vec_to_state(state_vec)
            if not check_state(state):
                continue

            print(state_to_name(state))
            break

    else:

        g = GF(2)
        final_mat = Matrix(g, linear_eq_mat)
        final_vec = vector(g, linear_eq_vec)
        state_vec = (final_mat.solve_right(final_vec))

        state = vec_to_state(state_vec)
        assert check_state(state)

        print(state_to_name(state))
