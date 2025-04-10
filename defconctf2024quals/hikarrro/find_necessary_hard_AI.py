from pwn import *
import networkx as nx
import numpy as np
import time
import pickle
context.log_level = 'DEBUG'


advanced_AI = {
    (44, 43, 18, 61): (44, 45),
    (45, 37, 52, 63): (45, 46),
    (46, 37, 52, 62) : (46, 38),
    (21, 20, 12, 15) : (12, 5),
    (28, 29, 21, 5) : (28, 20),
    (60, 26, 51, 56) : (51, 58),
    (20, 52, 37, 6) : (37, 19),
    (52, 19, 26, 48) : (26, 53),
    (45, 31, 58, 62) : (31, 46),

    (26, 20, 18, 1) : (26, 17) ,
    (19, 36, 21, 4) : (19, 20) ,
    (20, 28, 51, 5) : (20, 11) ,
    (50, 61, 12, 48) : (61, 51) ,
    (45, 11, 10, 62) : (11, 26) ,

    (21, 36, 1, 15) : (1, 37) ,
    (45, 37, 7, 63) : (37, 47) ,
    (26, 46, 7, 57) : (26, 34) ,
    (45, 17, 7, 62) : (17, 34) ,

}
#advanced_AI = {}

_A = './thinkingharder'
import chess as c
from chess import Piece
import random,sys,hashlib,struct,subprocess
NM = 10817184
#buf = None
def cc_to_board(cc):
    A = c.Board()
    A.clear()
    A.turn = c.WHITE
    B = Piece(c.KING, c.WHITE)
    A.set_piece_at(cc[0], B)
    B = Piece(c.KNIGHT, c.WHITE)
    A.set_piece_at(cc[1], B)
    B = Piece(c.BISHOP, c.WHITE)
    A.set_piece_at(cc[2], B)
    B = Piece(c.KING, c.BLACK)
    A.set_piece_at(cc[3], B)
    A.turn = c.WHITE
    return A

def board_to_cc(b):
    A=len(bin(b.knights)) - 3
    B=len(bin(b.bishops)) - 3
    C=len(bin(b.occupied_co[1] & b.kings)) - 3
    D=len(bin(b.occupied_co[0] & b.kings)) - 3
    return C, A, B, D

def bai(b):
    global moves
    global idx
    while True:
        print('Your move?')
        A = input()
        A = A.strip()
        B = A.split(' ')
        C = int(B[0])
        D = int(B[1])
        E = c.Move(C, D)
        if b.is_legal(E):
            break
    print('You moved:', C, D)
    return E

def wai(b):
    D = board_to_cc(b)
    for A in range(0, len(buf), 6):
        F = struct.unpack('4B', buf[A:A+4])
        if D == F:
            B, C = struct.unpack('2B', buf[A+4:A+6])
            break
    else:
        print('Thinking harder...')
        E = [_A]
        for A in D:
            E.append(str(A))
        G = subprocess.Popen(E, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        H = G.communicate()
        B, C = tuple([int(A) for A in H[0].strip().split()])
    I = c.Move(B, C)
    print('AI moved:', B, C)
    return I

def ist(b):
    if b.can_claim_draw() or b.is_stalemate() or b.is_insufficient_material():
        return True

def p(b,wai_f,bai_f):
    A = wai_f(b)
    b.push(A)
    print(b)
    if ist(b):
        return -1
    elif b.is_checkmate():
        return 1
    A = bai_f(b)
    b.push(A)
    print(b)
    if ist(b):
        return -1
    elif b.is_checkmate():
        return 1
    return 0

buf = open('xy_python.bin', 'rb').read()
easy_ai_map = {}
seeds = {}
for A in range(0, len(buf), 6):
    F = struct.unpack('4B', buf[A:A+4])
    B, C = struct.unpack('2B', buf[A+4:A+6])
    #if D == F:
    easy_ai_map[F] = (B, C)
    seeds[F] = A // 6

boards = []
boards_inv_map = {}
w_king = 44
b_king = 61
for bishop in range(64):
    if bishop in [w_king, b_king]:
        continue
    for knight in range(64):
        if knight in [bishop, w_king, b_king]:
            continue
        cc = (w_king, knight, bishop, b_king)
        F = cc_to_board(cc)
        if np.any(F.attackers(c.WHITE, b_king)):
            continue
        boards_inv_map[cc] = len(boards)
        boards.append((w_king, knight, bishop, b_king))

weird = set()
G = nx.DiGraph()
G.add_nodes_from(list(range(len(boards))))
G.add_node(1e8)

# board idx, next move is white
queue = list(range(len(boards)))

# store visited board where white is next move
w_visited = set()

# DFS
while queue:

    w_board_idx = queue.pop()
    w_visited.add(w_board_idx)
    w_cc = boards[w_board_idx]
    F = cc_to_board(w_cc)

    # handle easy AI only
    w_move = easy_ai_map.get(w_cc)

    # store situations we will need advanced AI
    if w_move is None:
        w_move = advanced_AI.get(w_cc)
        if w_move is None:
            weird.add(w_board_idx)
            continue

    # move white by AI
    F.push(c.Move(w_move[0], w_move[1]))
    if F.is_checkmate():
        G.add_edge(w_board_idx, 1e8)
        continue

    # go through all possible moves of black
    b_moves = list(F.generate_legal_moves())
    if not b_moves:
        raise Exception('what is this? %d' % w_board_idx, boards[w_board_idx])
    for b_move in b_moves:

        F_b = F.copy()
        F_b.push(c.Move(b_move.from_square, b_move.to_square))
        # back to white move, check visited, queue and add edge if necessary
        w_cc_after = board_to_cc(F_b)
        w_cc_after_idx = boards_inv_map.get(w_cc_after)

        if w_cc_after_idx is None:
            w_cc_after_idx = len(boards)
            boards.append(w_cc_after)
            boards_inv_map[w_cc_after] = w_cc_after_idx
            queue.append(w_cc_after_idx)
        else:
            if w_cc_after_idx not in queue and w_cc_after_idx not in w_visited:
                queue.append(w_cc_after_idx)
        
        G.add_edge(w_board_idx, w_cc_after_idx)

print('visited boards with white as next turn: %d' % len(w_visited))
print('no. of boards not handled by easy AI: %d' % len(weird))

# no cycles with steps > 1
print(set([len(c) for c in sorted(nx.strongly_connected_components(G), key=len, reverse=True)]))


# find which boards are in easy AI map
easy_board_idxs = []
for board_idx, board in enumerate(boards):
    if board in easy_ai_map:
        easy_board_idxs.append(board_idx)
print('len of easy board idx', len(easy_board_idxs))

G_rev = G.reverse()


seed_str_map = [r.strip() for r in open('seed_map.txt').readlines() if r.strip()]






for run_idx, idx in enumerate(sorted(list(weird))):
    break

    # find a valid path going to our target board that needs advanced AI
    found = False
    for board_idx in easy_board_idxs:
        for path in nx.all_simple_paths(G_rev, idx, board_idx):
            if path:
                path = path[::-1]
                found = True
                break
        if found:
            break
    if not found:
        print('!!!!!!!!! not found for board idx: %d' % idx, boards[idx])
        continue

    cc = boards[path[0]]
    seed = seed_str_map[seeds[cc]]
    F = cc_to_board(cc)

    io = remote('hikarrro-fklcapqlvr5cs.shellweplayaga.me', 7113)
    io.sendlineafter(b'Ticket please: ', b'ticket{BonziDialup4589n24:Q4n4TdKKlOqWVM5FrxxcxDFDtHrgt1YWYmKG--Fgh13cbSYz}')


    #io.sendlineafter(b'Seed?\n', b'1b.BF')
    io.sendlineafter(b'Seed?\n', seed.encode())

    

    for idx1, idx2 in zip(path[:-1], path[1:]):


        io.recvuntil(b'AI moved: ')
        m_from, m_to = io.recvline().decode().strip().split(' ')
        m_from, m_to = int(m_from), int(m_to)

        # for health check only
        F.push(c.Move(m_from, m_to))
        # print('white', (m_from, m_to))

        b_move = (boards[idx1][3], boards[idx2][3])
        # print('black', b_move)
        io.sendlineafter(b'Your move?\n', ('%d %d' % (b_move[0], b_move[1])).encode())

        F.push(c.Move(b_move[0], b_move[1]))
        # print(board_to_cc(F))
    
    # print(board_to_cc(F), boards[path[-1]])
    assert board_to_cc(F) == boards[path[-1]]
    io.recvuntil(b'AI moved: ')
    m_from, m_to = io.recvline().decode().strip().split(' ')
    m_from, m_to = int(m_from), int(m_to)
    #print('%02d advanced AI white' % run_idx, board_to_cc(F), ':', (m_from, m_to), ',')
    print(board_to_cc(F), ':', (m_from, m_to), ',')
    io.close()
    time.sleep(5)
    #break


io = remote('hikarrro-fklcapqlvr5cs.shellweplayaga.me', 7113)
io.sendlineafter(b'Ticket please: ', b'ticket{BonziDialup4589n24:Q4n4TdKKlOqWVM5FrxxcxDFDtHrgt1YWYmKG--Fgh13cbSYz}')


#io.sendlineafter(b'Seed?\n', b'1b.BF')
seed = seed_str_map[0]
seed = seed_str_map[4390566]
seed = seed_str_map[8077865]
io.sendlineafter(b'Seed?\n', seed.encode())


with open('graph.pickle', 'rb') as f:
    obj = pickle.load(f)
boards = obj['boards']
boards_inv_map = obj['boards_inv_map']
G = obj['G']

path_start = [0, 34252, 34254, 34256, 34257, 34259, 34261, 3348, 3349, 3350, 34265, 34267, 35728, 35257, 2367]
path_loop = [14233, 14211, 3350, 34265, 34267, 35729, 34274, 34277, 34282, 34781, 34784, 34792, 34794, 34797, 34949, 34816, 34830, 34833, 34834, 14214, 3369, 3350, 34265, 34267, 35729, 34274, 34275, 35430, 35433, 35449, 35450, 19806, 2250, 14218, 2367]
path_start = [0, 35731, 35733, 35735, 35736, 35738, 35740, 3348, 3349, 3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505]
path_loop = [25238, 5269, 5271, 4001, 3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505]


# states = [(0, 47, 9, 12), (0, 47, 9, 21), (8, 47, 9, 21), (8, 47, 9, 28), (8, 53, 9, 28), (8, 53, 9, 37), (8, 36, 9, 37), (8, 36, 9, 45), (17, 36, 9, 45), (17, 36, 9, 44), (26, 36, 9, 44), (26, 36, 9, 43), (26, 21, 9, 43), (26, 21, 9, 51), (34, 21, 9, 51), (34, 21, 9, 44), (34, 31, 9, 44), (34, 31, 9, 52), (35, 31, 9, 52), (35, 31, 9, 59), (35, 31, 36, 59), (35, 31, 36, 60), (35, 31, 43, 60), (35, 31, 43, 53), (36, 31, 43, 53), (36, 31, 43, 54), (36, 31, 52, 54), (36, 31, 52, 53), (36, 31, 45, 53), (36, 31, 45, 62), (44, 31, 45, 62), (44, 31, 45, 61), (44, 31, 38, 61), (44, 31, 38, 60), (44, 37, 38, 60), (44, 37, 38, 61), (44, 37, 52, 61), (44, 37, 52, 62), (45, 37, 52, 62), (45, 37, 52, 63), (46, 37, 52, 63), (46, 37, 52, 62), (38, 37, 52, 62), (38, 37, 52, 53), (29, 37, 52, 53), (29, 37, 52, 60), (36, 37, 52, 60), (36, 37, 52, 51), (35, 37, 52, 51), (35, 37, 52, 50), (35, 37, 34, 50), (35, 37, 34, 57), (35, 43, 34, 57), (35, 43, 34, 50), (35, 43, 27, 50), (35, 43, 27, 59), (35, 33, 27, 59), (35, 33, 27, 51), (35, 33, 36, 51), (35, 33, 36, 52), (35, 43, 36, 52), (35, 43, 36, 51), (35, 37, 36, 51), (35, 37, 36, 59), (42, 37, 36, 59), (42, 37, 36, 60), (43, 37, 36, 60), (43, 37, 36, 53), (43, 31, 36, 53), (43, 31, 36, 61), (44, 31, 36, 61), (44, 31, 36, 60), (44, 31, 45, 60), (44, 31, 45, 61), (44, 31, 38, 61), (44, 31, 38, 60), (44, 37, 38, 60), (44, 37, 38, 61)]
# state_z = state[::2]
# moves = []
# for s1, s2 in zip(state_z[:-1], state_z[1:]):
#     moves.append(s1[3], s2[3])


moves = [(12, 21), (21, 28), (28, 37), (37, 45), (45, 44), (44, 43), (43, 51), (51, 44), (44, 52), (52, 59), (59, 60), (60, 53), (53, 54), (54, 53), (53, 62), (62, 61), (61, 60), (60, 61), (61, 62), (62, 63), (63, 62), (62, 53), (53, 60), (60, 51), (51, 50), (50, 57), (57, 50), (50, 59), (59, 51), (51, 52), (52, 51), (51, 59), (59, 60), (60, 53), (53, 61), (61, 60), (60, 61), (61, 60), (60, 61), (61, 62), (62, 63), (63, 62), (62, 53), (53, 60), (60, 51), (51, 50), (50, 57), (57, 50), (50, 59), (59, 51), (51, 52), (52, 51), (51, 59), (59, 60), (60, 53), (53, 61), (61, 60), (60, 61), (61, 60), (60, 61), (61, 62), (62, 63), (63, 62), (62, 53), (53, 60), (60, 51), (51, 50), (50, 57), (57, 50), (50, 59), (59, 51), (51, 52), (52, 51), (51, 59), (59, 60), (60, 53), (53, 61), (61, 60)]

# path_complete = path_start + path_loop * 5
# for idx, (node1, node2) in enumerate(zip(path_complete[:-1], path_complete[1:])):
#     b_move = boards[node1][3], boards[node2][3]
for b_move in moves:
    print('idx', idx)
    print(io.recvuntil(b'Your m'))
    #io.sendlineafter(b'Your move?\n', ('%d %d' % (b_move[0], b_move[1])).encode())
    io.sendlineafter(b've?\n', ('%d %d' % (b_move[0], b_move[1])).encode())
for _ in range(20):
    print(io.recvline())
io.close()