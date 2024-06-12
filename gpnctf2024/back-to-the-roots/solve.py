import networkx as nx
from itertools import permutations
from Crypto.Util.number import long_to_bytes

ct = open('output').read().strip()
print('length of bits: %d, length of chars: %d' % (len(ct), len(ct) // 8))

res = ''.join(['011xxxxx' for i in range(len(ct)//8)])

def find_pattern(s, pattern):
    # this function is solely for the correct key length 33
    matched = []
    for pattern_id, p in pattern.items():
        valid = True
        for a,b in zip(s, p):
            if b == 'x':
                continue
            if a != b:
                valid = False
                break
        if valid:
            matched.append(pattern_id)
    assert len(matched) == 1
    return matched[0]

valid_keylengths = []

for keylen in range(21, 36):
    # if keylen != 33:
    #     continue
    substrs = []
    all_valid = True
    all_offsets = []
    for i in range(keylen):
        substr = res[i::keylen]
        substrs.append(substr)
        found = False
        
        for j in range(len(ct)-keylen):
            valid = True
            ss = ct[j:j+len(substr)]
            for k in range(len(ss)):
                if substr[k] == 'x':
                    continue
                if substr[k] != ss[k]:
                    valid = False
                    break
            if valid:
                all_offsets.append(j)
                found = True
                #break
        if not found:
            all_valid = False
            break
    if not all_valid:
        continue
    if 0 not in all_offsets:
        # the first offset chunks from ct must match a pattern
        continue
    # there must be at least {keylength} matched indices
    if len(all_offsets) < keylen:
        continue

    print('keylen', keylen)
    print('len(matched indices)', len(all_offsets))
    print(sorted(list(set(all_offsets))))
    valid_keylengths.append((keylen, sorted(list(set(all_offsets)))))

assert len(valid_keylengths) == 1 and valid_keylengths[0][0] == 33
keylen, all_offsets = valid_keylengths[0]


# get the 8 patterns
keylen = 33
pattern = {}
for i in range(8):
    pattern[i] = res[i::keylen][:43]  # we handle the 44-th character later

# precompute the pattern id for each starting offset of ct

pattern_map = {}
for idx in all_offsets:
    pattern_map[idx] = find_pattern(ct[idx:idx+43], pattern)

graph = nx.DiGraph()
graph.add_nodes_from(all_offsets)
# 1432 is the ending goal to reach
# a path should exist from 0, 43, 87, ... till 1432 representing every column chunk
graph.add_node(1432)

for k in all_offsets:

    if k + 43 in all_offsets + [1432]:

        graph.add_edge(k, k + 43)

    if k + 44 in all_offsets + [1432]:

        pattern_id = find_pattern(ct[k:k+44], pattern)
        if pattern_id in [5, 6, 7]:
            if ct[k + 43] != {5: '0', 6: '1', 7: '1'}[pattern_id]:
                continue

        graph.add_edge(k, k + 44)


required_pattern_count = {
    0: 5,
    1: 4,
    2: 4,
    3: 4,
    4: 4,
    5: 4,
    6: 4,
    7: 4,
}
required_pattern_count_44 = {
    0: 2,
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 1,
    6: 1,
    7: 1,
}

real_paths = []

for idx, path in enumerate(nx.all_simple_paths(graph, 0, 1432)):

    if idx % 100000 == 0:
        print('processing:', idx)

    # tuple of (offset of ct, pattern ID, length of chunk)
    path_info = [(node_1, pattern_map[node_1], node_2 - node_1) for node_1, node_2 in zip(path[:-1], path[1:])]
    _, patterns, _ = zip(*path_info)

    # check no. of chunks for each pattern ID
    valid = True
    for pattern_id, count in required_pattern_count.items():
        if patterns.count(pattern_id) != count:
            valid = False
            break
    if not valid:
        continue

    # check no. of length-44 chunks
    patterns = []
    for node, pattern_id, length in path_info:
        if length != 44:
            continue
        patterns.append(pattern_id)

    valid = True
    for pattern_id, count in required_pattern_count_44.items():
        if patterns.count(pattern_id) != count:
            valid = False
            break
    if not valid:
        continue

    real_paths.append(path)

print('remaining candidates: %d' % len(real_paths))
# correct path = [0, 43, 86, 129, 173, 217, 261, 304, 348, 391, 434, 477, 520, 564, 607, 651, 694, 737, 781, 824, 867, 910, 953, 997, 1040, 1084, 1128, 1171, 1215, 1259, 1302, 1346, 1389, 1432]

# brute force the permutations
for path in real_paths:

    path_info = [(node_1, pattern_map[node_1], node_2 - node_1) for node_1, node_2 in zip(path[:-1], path[1:])]

    idx_44_0 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 0]
    idx_44_1 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 1]
    idx_44_2 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 2]
    idx_44_3 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 3]
    idx_44_4 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 4]
    idx_44_5 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 5][0]
    idx_44_6 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 6][0]
    idx_44_7 = [node for node, pattern_id, length in path_info if length == 44 and pattern_id == 7][0]
    idx_43_0 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 0]
    idx_43_1 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 1]
    idx_43_2 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 2]
    idx_43_3 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 3]
    idx_43_4 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 4]
    idx_43_5 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 5]
    idx_43_6 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 6]
    idx_43_7 = [node for node, pattern_id, length in path_info if length == 43 and pattern_id == 7]

    for i44_0_0, i44_0_1 in permutations(idx_44_0):
        for i44_1_0, i44_1_1 in permutations(idx_44_1):
            for i44_2_0, i44_2_1 in permutations(idx_44_2):
                for i44_3_0, i44_3_1 in permutations(idx_44_3):
                    for i44_4_0, i44_4_1 in permutations(idx_44_4):
                        for i43_0_0, i43_0_1, i43_0_2 in permutations(idx_43_0):
                            for i43_1_0, i43_1_1 in permutations(idx_43_1):
                                for i43_2_0, i43_2_1 in permutations(idx_43_2):
                                    for i43_3_0, i43_3_1 in permutations(idx_43_3):
                                        for i43_4_0, i43_4_1 in permutations(idx_43_4):
                                            for i43_5_0, i43_5_1, i43_5_2 in permutations(idx_43_5):
                                                for i43_6_0, i43_6_1, i43_6_2 in permutations(idx_43_6):
                                                    for i43_7_0, i43_7_1, i43_7_2 in permutations(idx_43_7):
                                                        chunks = [
                                                            ct[i44_0_0 : i44_0_0 + 44],
                                                            ct[i44_1_0 : i44_1_0 + 44],
                                                            ct[i44_2_0 : i44_2_0 + 44],
                                                            ct[i44_3_0 : i44_3_0 + 44],
                                                            ct[i44_4_0 : i44_4_0 + 44],
                                                            ct[idx_44_5 : idx_44_5 + 44],
                                                            ct[idx_44_6 : idx_44_6 + 44],
                                                            ct[idx_44_7 : idx_44_7 + 44],
                                                            ct[i44_0_1 : i44_0_1 + 44],
                                                            ct[i44_1_1 : i44_1_1 + 44],
                                                            ct[i44_2_1 : i44_2_1 + 44],
                                                            ct[i44_3_1 : i44_3_1 + 44],
                                                            ct[i44_4_1 : i44_4_1 + 44],
                                                            ct[i43_5_0 : i43_5_0 + 43] + ' ',   # just a placeholder for using zip
                                                            ct[i43_6_0 : i43_6_0 + 43] + ' ',
                                                            ct[i43_7_0 : i43_7_0 + 43] + ' ',
                                                            ct[i43_0_0 : i43_0_0 + 43] + ' ',
                                                            ct[i43_1_0 : i43_1_0 + 43] + ' ',
                                                            ct[i43_2_0 : i43_2_0 + 43] + ' ',
                                                            ct[i43_3_0 : i43_3_0 + 43] + ' ',
                                                            ct[i43_4_0 : i43_4_0 + 43] + ' ',
                                                            ct[i43_5_1 : i43_5_1 + 43] + ' ',
                                                            ct[i43_6_1 : i43_6_1 + 43] + ' ',
                                                            ct[i43_7_1 : i43_7_1 + 43] + ' ',
                                                            ct[i43_0_1 : i43_0_1 + 43] + ' ',
                                                            ct[i43_1_1 : i43_1_1 + 43] + ' ',
                                                            ct[i43_2_1 : i43_2_1 + 43] + ' ',
                                                            ct[i43_3_1 : i43_3_1 + 43] + ' ',
                                                            ct[i43_4_1 : i43_4_1 + 43] + ' ',
                                                            ct[i43_5_2 : i43_5_2 + 43] + ' ',
                                                            ct[i43_6_2 : i43_6_2 + 43] + ' ',
                                                            ct[i43_7_2 : i43_7_2 + 43] + ' ',
                                                            ct[i43_0_2 : i43_0_2 + 43] + ' ',
                                                        ]
                                                        pt = ''.join([''.join(bits) for bits in zip(*chunks)])
                                                        pt_int = int(''.join(pt).strip(), 2)
                                                        flag = long_to_bytes(pt_int)
                                                        if all([97 <= c <= 97+25 for c in flag]):
                                                            print(flag)