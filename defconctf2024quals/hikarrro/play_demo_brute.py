import networkx as nx
import numpy as np
import time
import pickle

_A = './thinkingharder'
import chess as c
from chess import Piece
import random,sys,hashlib,struct,subprocess
NM = 10817184
#buf = None

buf = open('xy_python.bin', 'rb').read()
easy_ai_map = {}
seeds = {}
for A in range(0, len(buf), 6):
    F = struct.unpack('4B', buf[A:A+4])
    B, C = struct.unpack('2B', buf[A+4:A+6])
    easy_ai_map[F] = (B, C)
    seeds[F] = A // 6

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
    A = len(bin(b.knights)) - 3
    B = len(bin(b.bishops)) - 3
    C = len(bin(b.occupied_co[1] & b.kings)) - 3
    D = len(bin(b.occupied_co[0] & b.kings)) - 3
    return C, A, B, D

def bai(b):
    global idxx
    global moves
    while True:
        print('Your move?')
        #A = input()
        # A = A.strip()
        # B = A.split(' ')
        B = moves[idxx]
        print('black move', idxx, B)
        idxx = idxx + 1
        C = int(B[0])
        D = int(B[1])
        E = c.Move(C, D)
        if b.is_legal(E):
            break
        raise
    print('You moved:', C, D)
    return E

def wai(b):
    D = board_to_cc(b)
    if easy_ai_map.get(D):
        B, C = easy_ai_map.get(D)
    # for A in range(0, len(buf), 6):
    #     F = struct.unpack('4B', buf[A:A+4])
    #     if D == F:
    #         B, C = struct.unpack('2B', buf[A+4:A+6])
    #         break
    else:
        B, C = advanced_AI.get(D)
        # print('Thinking harder...')
        # E = [_A]
        # for A in D:
        #     E.append(str(A))
        # G = subprocess.Popen(E, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # H = G.communicate()
        # B, C = tuple([int(A) for A in H[0].strip().split()])
    I = c.Move(B, C)
    print('AI moved:', B, C)
    return I

def ist(b):
    print('claim draw', b.can_claim_draw())
    print('fifty', b.is_fifty_moves(), b.can_claim_fifty_moves())
    print('threefold', b.can_claim_threefold_repetition())
    if b.can_claim_draw() or b.is_stalemate() or b.is_insufficient_material():
        return True

def p(b,wai_f,bai_f):
    global b_visited
    A = wai_f(b)
    b.push(A)
    b_visited.append(board_to_cc(b))
    print(b)
    if ist(b):
        print('after white')
        return -1
    elif b.is_checkmate():
        return 1
    A = bai_f(b)
    b.push(A)
    b_visited.append(board_to_cc(b))
    print(b)
    if ist(b):
        print('after black')
        print(b_visited)
        return -1
    elif b.is_checkmate():
        return 1
    return 0

def main(seed):
    J = 'Invalid'
    global buf
    global seed_str_map
    global seeds
    global initial

    A = open(__file__, 'rb').read()

    B = hashlib.md5()
    B.update(A)
    K = B.hexdigest()[:4]

    A = open(_A, 'rb').read()
    B = hashlib.md5()
    B.update(A)
    L = B.hexdigest()[:4]

    print('Welcome to hikarrru v'+K+L+'!')

    print('Seed?')
    #C = input()
    
    #C = seed_str_map[4390566]
    C = seed_str_map[3250]
    C = seed_str_map[10108261]
    C = seed_str_map[3337543]
    C = seed_str_map[6941676]
    C = seed_str_map[4905027]
    C = seed_str_map[7971119]
    C = seed_str_map[9834257]
    C = seed_str_map[seed]
    #C = seed_str_map[seeds[initial]]

    C = C.strip()
    if len(C) < 1 or len(C) > 20:
        print(J)
        return -1

    M = C.encode()
    N = hashlib.sha256(M)
    O = N.hexdigest()
    P = int(O,16)
    E = P % 25000001
    if E >= NM:
        print(J)
        return -1
    #buf = open('xy_python.bin', 'rb').read()
    G = struct.unpack('6B', buf[E*6:E*6+6])
    Q = G[:4], G[4:]
    A = Q[0]
    F = cc_to_board(A)
    while True:
        print('===============')
        print(F)
        H = p(F, wai, bai)
        if H != 0:
            if H != 1:
                print("Congratulations, you didn't loose...")
                I = board_to_cc(F)
                if I[3] == 61 and I[0] == 44:
                    print('This is the flag:', open('/flag', 'rb').read())
                    raise Exception('succeeded')
                    return 0
                else:
                    print(I)
                    print('But Our Flag is in Another Castle!')
                    return 0
            else:
                print('Chess is hard!')
                return 0

def search_board(target):
    next_target = 50
    w_visited = set()
    b_visited = set()
    global boards
    global valids
    # queue = [
    #     boards[2367],
        #(44,45,38,61),
#         (44,45,29,61),
#         (44,45,20,61),
#         (44,45,11,61),
#         (44,45, 2,61),
    # ]
    # queue = [boards[vv] for vv in valids]
    # queue = [ (45, 48, 36, 60)]
    queue = [target]
#     queue = [(48, 35, 22, 28)]
    G = nx.DiGraph()
    G.add_nodes_from(queue)
    while queue:
        current = queue.pop()
        w_visited.add(current)
        board = cc_to_board(current)
#         if current in seeded:
#             print(current)
#             print('found')
#             return
        rr = board.attackers(c.WHITE, current[3])
        attack_b = True if np.any(rr) else False
        #board.turn = c.BLACK
        #b_moves = list(ff.generate_legal_moves())
        
        
        # for 1 item process here, we reverse the black and then the white, and put it back into the white queue
        # everytime the queue contains board which white has to move next
        
        # reversing the black moves, we don't want to use the generate_legal_moves function
        for b_offset in [-9, -8, -7, -1, 1, 7, 8, 9]:
            b_from = current[3] + b_offset
            if b_from < 0 or b_from > 63:
                continue
            if current[3] % 8 == 7 and b_offset in [-7, 1, 9]:
                continue
            if current[3] % 8 == 0 and b_offset in [-9, -1, 7]:
                continue
            cc_before_b = list(current[:3]) + [b_from]
            cc_before_b = tuple(cc_before_b)
            if cc_before_b in b_visited:
                continue
            b_visited.add(cc_before_b)
            if b_from in current[:3]:
                continue
            
            board_before_b = cc_to_board(cc_before_b)
            white_attackers = board_before_b.attackers(c.WHITE, b_from)
            white_attack_pieces = [idx for idx, i in enumerate(white_attackers)]
            if len(white_attack_pieces) > 1:
                continue
            if len(white_attack_pieces) == 1:
                white_attack_piece = white_attack_pieces[0]
                white_attack = True
            else:
                white_attack = False
            
            board_before_b.turn = c.WHITE
            w_moves = list(board_before_b.generate_legal_moves())
            for w_move in w_moves:
                piece_idx = cc_before_b[:3].index(w_move.from_square)
                cc_before_w = list(cc_before_b)
                cc_before_w[piece_idx] = w_move.to_square
                cc_before_w = tuple(cc_before_w)
                if cc_before_w in w_visited:
                    continue
                w_visited.add(cc_before_w)
                if cc_before_w in boards:
                    continue
                if w_move.to_square == b_from:
                    continue
                if white_attack:
                    if w_move.from_square != white_attack_piece:
                        continue
                
                board_before_w = cc_to_board(cc_before_w)
                white_attackers = board_before_w.attackers(c.WHITE, cc_before_w[3])
                if np.any(white_attackers):
                    continue
                w_ai_move = easy_ai_map.get(cc_before_w)
                if w_ai_move is None:
                    continue
                if w_ai_move == (w_move.to_square, w_move.from_square):
                    #print('steps', cc_before_b, cc_before_w)
                    G.add_node(cc_before_w)
                    G.add_edge(cc_before_w, current)
                    queue.append((cc_before_w))
                
            #print(b_move.from_square, b_move.to_square)
#         print(queue)
        #if len(queue) > 10:
        if len(G.nodes) > next_target:
            #print(len(G.nodes))
            next_target += 50
            if next_target > 5000:
                return G
#         if len(G.nodes) > len(valids) + 500*1 + 100*0:
#             return G
#             break
    return G

if __name__=='__main__':
    with open('graph.pickle', 'rb') as f:
        obj = pickle.load(f)

    boards = obj['boards']
    boards_inv_map = obj['boards_inv_map']
    G = obj['G']
    moves = []

    seed_str_map = [r.strip() for r in open('seed_map.txt').readlines() if r.strip()]
    components = sorted(nx.strongly_connected_components(G), key=len, reverse=True)[0]
    valids = []
    for board_idx in sorted(nx.strongly_connected_components(G), key=len, reverse=True)[0]:
        if boards[board_idx][3] == 61 and boards[board_idx][0] == 44:
            valids.append(board_idx)
    #len(valids)

    # valids = []
    # for iddx, goal in enumerate(sorted(list(components))):
    #     if validate(boards[goal]):
    #         valids.append(goal)

    # for idx in valids:
    #     paths_from_goal = {}
    #     for aa in valids:
    #         for k in nx.all_simple_paths(G, 1505, aa):
    #             if len(k) == 9:
    #                 print(k)
    #             paths_from_1505[len(k)] = k
    #             break

    for board_idx in valids:
        cc = boards[board_idx]
        q = search_board(cc)
        initial = nx.dag_longest_path(q)
        seed = seeds[initial[0]]



        path_loops = []
        target = board_idx
        for goal in components:
            for k in nx.all_simple_paths(G, target, goal):
                path1 = k
                break
            for k in nx.all_simple_paths(G, goal, target):
                path2 = k
                break
            if not set(path1[1:-1]).intersection(set(path2[1:-1])):
                #print(goal, len(path1) + len(path2))
                path_loop = path1 + path2[1:-1]
                path_loops.append(path_loop)
                #raise

                idxx = 0
                b_visited = []
                moves = []
                for cc1, cc2 in zip(initial[:-1], initial[1:]):
                    moves.append((cc1[3], cc2[3]))
                path_complete = path_loop * 3
                for idx, (node1, node2) in enumerate(zip(path_complete[:-1], path_complete[1:])):
                    b_move = boards[node1][3], boards[node2][3]
                    moves.append(b_move)
                print(seed, initial, moves)
                main(seed)
                time.sleep(2)
    raise Exception('done')
    
"""
    #path_start = [0, 35731, 35733, 35735, 35736, 35738, 35740, 3348, 3349, 3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505]
    #path_loop = [25238, 5269, 5271, 4001, 3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505]
    #path_loop = [25238, 5269, 5271, 4001, 3350, 3353, 3355, 5588, 3362, 3365, 3370, 3869, 3872, 3876, 4586, 1510, 20866, 20725, 20731, 4405, 4389] + [3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505]
    #path_start = [29214, 29218, 20070, 3911, 3939, 3942, 3351, 3350, 3353, 3355, 5588, 3362, 3365, 3370, 3869, 3872, 3876, 4586, 1510, 20866, 20725, 20731, 4405, 4389, 3350, 3353, 3355, 5588, 3362, 3365, 3370, 3869, 3872, 3879, 4433, 4435, 4474, 4476, 4488, 4492, 1964, 17291, 1972, 3326, 3327, 3347, 3348]
    #path_loop = []

    # all here are unseen in the graph, except the last one which is idx 1972, guaranteed to enter the loop at 1972, but why it detects threefold at 3350?
    initial = [
        (0, 53, 59, 51),
        (0, 53, 41, 44),
        (0, 63, 41, 37),
        (9, 63, 41, 45),
        (18, 63, 41, 36),
        (26, 63, 41, 44),
        (26, 63, 50, 51),
        (26, 63, 36, 58),
        (26, 53, 36, 51),
        (35, 53, 36, 60),
        (44, 53, 36, 61),   # 1972
    ]
    initial = [
        #(0, 2, 31, 30),
        (0, 2, 59, 37),
        (9, 2, 59, 36),
        (18, 2, 59, 43),
        (18, 2, 38, 51),
        (18, 2, 29, 59),
        (18, 17, 29, 51),
        (18, 32, 29, 52),
        (18, 32, 36, 53),
        (18, 42, 36, 61),
        (27, 42, 36, 60),
        (27, 48, 36, 51),
        (35, 48, 36, 60),
        (44, 48, 36, 61),
    ]
    initial = [
        (63, 58, 59, 60),
        (63, 58, 45, 53),
        (63, 58, 27, 61),
        (55, 58, 27, 60),
        (46, 58, 27, 59),
        (46, 48, 27, 51),
        (45, 48, 27, 59),
        (45, 48, 36, 60),
    ]
    for cc1, cc2 in zip(initial[:-1], initial[1:]):
        moves.append((cc1[3], cc2[3]))




    #path_start = [1, 35726, 2342, 5665, 2367, 16333, 3969, 3350, 3353, 3355, 5588, 3362, 3364, 5192, 5272, 5275, 5277, 1505] + [25238, 5269, 5271, 4001, 3350, 3353, 3355, 5587, 4942, 4968, 2076]
    #initial = boards[path_start[0]]
    path_loop = [1972,3326,3327,3347,3348,3349,3350,3353,3355,5588,3362,3365,3370,3869,3872,3879,4433,4435,4474,4476,4488,4492,1964,17291]


    #path_loop = [1968,  17294,  2383,  3287,  2367,  16333,  3969,  3350,  3353,  3355,  5588,  3362,  3365,  3370,  3869,  3872,  3879,  4433,  4435,  4474,  4479,  4480]
    path_loop = [4480, 1968,  17294,  2383,  3287,  2367,  16333,  3969,  3350,  3353,  3355,  5588,  3362,  3365,  3370,  3869,  3872,  3879,  4433,  4435,  4474,  4479]

    #path_complete = path_start + path_loop# * 5
    path_complete = path_loop * 3
    for idx, (node1, node2) in enumerate(zip(path_complete[:-1], path_complete[1:])):
        b_move = boards[node1][3], boards[node2][3]
        moves.append(b_move)
    print(len(moves), moves)#, path_start)
"""