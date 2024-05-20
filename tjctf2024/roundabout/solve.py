import networkx as nx
import re
from collections import defaultdict
from pyrage import passphrase
from itertools import permutations, combinations, combinations_with_replacement
from collections import Counter
import time

def get_graph(exclude_nodes=[]):
    global nodes_raw, edges_raw
    g = nx.Graph()
    g.add_nodes_from(nodes_raw)

    edges = []
    for edge in edges_raw:
        a,b = edge
        if a in exclude_nodes or b in exclude_nodes:
            continue
        edges.append((a, b))
    g.add_edges_from(edges)
    return g


def search_word(w, g):
    global char_dict
    global char_dict_inv

    if len(w) == 1:
        if w in char_dict_inv:
            return [[node_id] for node_id in char_dict_inv[w]]
        else:
            return []

    res = []

    gg = nx.Graph()
    gg.add_nodes_from(list(g.nodes))

    for c1, c2 in zip(w[:-1], w[1:]):

        for n1 in char_dict_inv[c1]:
            for n2 in char_dict_inv[c2]:
                if (n1,n2) in g.edges or (n2,n1) in g.edges:
                    gg.add_edge(n1,n2)

    for source in char_dict_inv[w[0]]:
        for target in char_dict_inv[w[-1]]:
            for path in nx.all_simple_paths(gg, source, target):
                s = ''.join([char_dict[n] for n in path])
                if s == w:
                    res.append(path)
    return res

text = open("amontillado.txt").read()
words = list(set(re.sub("[^a-z]", " ", text.lower()).split()))


char_dict = {}
char_dict_inv = defaultdict(list)
nodes_raw = []
edges_raw = []
for l in open('hint.txt').readlines():
    if '--' not in l:
        a, b = l.strip().replace('[', '').replace('];', '').split()
        node_id = int(a)
        node_char = b
        nodes_raw.append(node_id)
        char_dict[node_id] = b
        char_dict_inv[b].append(node_id)
    else:
        a,b = l.replace(';', '').strip().split(' -- ')
        a,b = int(a), int(b)
        edges_raw.append((a,b))
print('No. of nodes:', len(nodes_raw), 'No. of edges:', len(edges_raw))

g_raw = get_graph()

############# 1. check the "q" words #############
print()
print('1. check the possible "q" words....')
for w in words:
    if 'q' not in w:
        continue
    path = search_word(w, g_raw)
    if path:
        print(w, path)

# "questing" node ids
requesting = [718937935, 602055180, 155400157, 266182232, 123660377, 533711733, 317854830, 869203381]

# exclude edges connecting to "requesting""
g = get_graph(exclude_nodes=requesting)

############# 2. check the "c" words #############
print()
print('2. check the possible "c" words....')
for w in words:
    if 'c' not in w:
        continue
    path = search_word(w, g)
    if path:
        print(w, path)

recoiling = [70221986, 418922342, 877433739, 410141951, 23641462, 605272908, 1042372035, 158077666, 837003197]

g = get_graph(exclude_nodes=requesting + recoiling)


############# 3. filter the entire word list #############
print()
print("3. filter the entire word list")
words_filter = []
for w in words:
    if search_word(w, g):
        words_filter.append(w)
print('No. of Remaining possible words in the password:', len(words_filter))

# show no. of words for each word length
word_count_dict = defaultdict(int)
words_dict = defaultdict(list)
for w in words_filter:
    word_count_dict[len(w)] += 1
    words_dict[len(w)].append(w)
print('no. of words with specific length')
print([{i:word_count_dict[i]} for i in sorted(word_count_dict)])

############# 4. Get combination of word lengths that could make the 31-letter long password #############
print()
print("4. Get combination of word lengths that could make the 31-letter long password")
cands = defaultdict(list)
valid_w_lens = word_count_dict.keys()

# it's too unlikely for the remaining 31-letter passwords to be composed of more than 13 words
for n_words in range(1, 13):

    for word_lens in combinations_with_replacement(valid_w_lens, n_words):

        valid = True

        for i in valid_w_lens:
            if word_lens.count(i) > word_count_dict[i]:   # technically sampled words could be repeated
                valid = False
                break

        if not valid:
            continue

        l = sum(word_lens)

        if l != 31:
            continue

        cands[l].append(word_lens)

print('No. of possible word length combination', len(cands[31]))


# remaining required character list, after removing "requesting" and "recoiling"
target_chars = [char_dict[k] for k in g_raw.nodes]
target_chars = sorted(target_chars)

for c in 'requesting' + 'recoiling':
    target_chars.remove(c)

target_chars = ''.join(target_chars)
print('the remaining required 31-character list', target_chars)

############# 5. Note so many "d"s #############
print()
print('5. start working with the character "d"')
d_words = []
non_d_words = []
for w in words_filter:
    if 'd' in w:
        d_words.append(w)
    else:
        non_d_words.append(w)

print("No. of words with 'd': %d, No. of words without 'd': %d" % (len(d_words), len(non_d_words)))
print('"d" words: ', ', '.join(d_words + ['understand']))
print('non-"d" words: ', ', '.join(non_d_words))

# this has 2 "d"s, separate it when doing combinations
d_words.remove('understand')

# get the words without d, grouped by word length, for combinations use
word_count_dict_non_d = defaultdict(int)
words_dict_non_d = defaultdict(list)
for w in non_d_words:
    word_count_dict_non_d[len(w)] += 1
    words_dict_non_d[len(w)].append(w)
print('no. of non-d words with specific length')
print([{i:word_count_dict_non_d[i]} for i in sorted(word_count_dict_non_d)])


############# 6. exhaust the combination for having 4 "d"s, and exhaust the remaining words #############
# find which combinations give the required 50 characters
print()
print("6. Starting looping word combinations.....")
st = time.time()
final_cands = []

for d_cands in list(combinations(d_words, 4)) + list(combinations(d_words, 2)):
    # it has to contain 4 "d"s
    if len(d_cands) == 2:
        d_list = list(d_cands) + ['understand']
    else:
        d_list = list(d_cands)

    # from the 31 remaining character, remove these "d" words.
    # it's invalid combination if any of the characters from these words don't exist
    remain_chars = list(target_chars)
    try:
        for w in d_list:
            for c in w:
                remain_chars.remove(c)
        remain_chars = ''.join(remain_chars)
    except:
        continue

    for lengths in cands[31]:
        ll = list(lengths)
        try:
            for w in d_list:
                ll.remove(len(w))
        except:
            continue

        c = Counter(ll)
        keys = list(c.keys())
        # if we required 3 words with length 4, and 2 words with length 5,
        # len(keys) would be 2 ---- need to loop the combination of 3 words of length 4, AND the combination of 2 words of length 5

        if len(keys) == 1:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):

                chars_sorted = ''.join(sorted(''.join(w1)))

                if chars_sorted != remain_chars:
                    continue

                cand = d_list + list(w1)
                final_cands.append(cand)
                print(cand)

        elif len(keys) == 2:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):
                for w2 in combinations(words_dict_non_d[keys[1]], c[keys[1]]):

                    chars_sorted = ''.join(sorted(''.join(w1 + w2)))

                    if chars_sorted != remain_chars:
                        continue

                    cand = d_list + list(w1 + w2)
                    final_cands.append(cand)
                    print(cand)

        elif len(keys) == 3:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):
                for w2 in combinations(words_dict_non_d[keys[1]], c[keys[1]]):
                    for w3 in combinations(words_dict_non_d[keys[2]], c[keys[2]]):

                        chars_sorted = ''.join(sorted(''.join(w1 + w2 + w3)))

                        if chars_sorted != remain_chars:
                            continue

                        cand = d_list + list(w1 + w2 + w3)
                        final_cands.append(cand)
                        print(cand)

        elif len(keys) == 4:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):
                for w2 in combinations(words_dict_non_d[keys[1]], c[keys[1]]):
                    for w3 in combinations(words_dict_non_d[keys[2]], c[keys[2]]):
                        for w4 in combinations(words_dict_non_d[keys[3]], c[keys[3]]):

                            chars_sorted = ''.join(sorted(''.join(w1 + w2 + w3 + w4)))

                            if chars_sorted != remain_chars:
                                continue

                            cand = d_list + list(w1 + w2 + w3 + w4)
                            final_cands.append(cand)
                            print(cand)

        elif len(keys) == 5:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):
                for w2 in combinations(words_dict_non_d[keys[1]], c[keys[1]]):
                    for w3 in combinations(words_dict_non_d[keys[2]], c[keys[2]]):
                        for w4 in combinations(words_dict_non_d[keys[3]], c[keys[3]]):
                            for w5 in combinations(words_dict_non_d[keys[4]], c[keys[4]]):

                                chars_sorted = ''.join(sorted(''.join(w1 + w2 + w3 + w4 + w5)))

                                if chars_sorted != remain_chars:
                                    continue

                                cand = d_list + list(w1 + w2 + w3 + w4 + w5)
                                final_cands.append(cand)
                                print(cand)

        elif len(keys) == 6:

            for w1 in combinations(words_dict_non_d[keys[0]], c[keys[0]]):
                for w2 in combinations(words_dict_non_d[keys[1]], c[keys[1]]):
                    for w3 in combinations(words_dict_non_d[keys[2]], c[keys[2]]):
                        for w4 in combinations(words_dict_non_d[keys[3]], c[keys[3]]):
                            for w5 in combinations(words_dict_non_d[keys[4]], c[keys[4]]):
                                for w6 in combinations(words_dict_non_d[keys[5]], c[keys[5]]):

                                    chars_sorted = ''.join(sorted(''.join(w1 + w2 + w3 + w4 + w5 + w6)))

                                    if chars_sorted != remain_chars:
                                        continue

                                    cand = d_list + list(w1 + w2 + w3 + w4 + w5 + w6)
                                    final_cands.append(cand)
                                    print(cand)

        else:
            raise Exception("not handled")

print('processing time: %.1f secs' % (time.time() - st))


############# 7. check which paths of the words could give the distinct 50 node ids #############
# note: although the words are the same combination, the node path could be different
pw_words_final_cands = []
paths = {}
print()
print('7. Finding combinations that give the 50 distinct node ids, note that the node path could be different although the word combination is the same')
print('...Processing...')

for pw_words in final_cands:

    all_words = pw_words + ['requesting', 'recoiling']

    for w in all_words:
        if w in paths:
            continue
        paths[w] = search_word(w, g_raw)

    for p0 in paths[all_words[0]]:
        for p1 in paths[all_words[1]]:
            for p2 in paths[all_words[2]]:
                for p3 in paths[all_words[3]]:
                    for p4 in paths[all_words[4]]:
                        for p5 in paths[all_words[5]]:
                            for p6 in paths[all_words[6]]:

                                all_nodes = p0 + p1 + p2 + p3 + p4 + p5 + p6

                                if len(set(all_nodes)) != 50:
                                    continue

                                print(all_words)
                                pw_words_final_cands.append([(w, path) for w, path in zip(all_words, [p0,p1,p2,p3,p4,p5,p6])])



############# 8. loop permutation of word list, check which one has correct edge, and try to decrypt #############
print()
print('8. Decrypting...')
for pw_words in pw_words_final_cands:

    for pw_words_order in permutations(pw_words):

        pw, paths = zip(*pw_words_order)

        valid = True

        for n1, n2 in zip(paths[:-1], paths[1:]):

            if (n1[-1], n2[0]) not in g_raw.edges and (n2[0], n1[-1]) not in g_raw.edges:
                valid = False
                break

        if not valid:
            continue

        password = ''.join(pw)
        print('Trying: %s' % password)
        try:
            dec = passphrase.decrypt(open('secret.txt', 'rb').read(), password)
            print(dec)
            print('-- Success')
        except:
            print('-- Failed')
        print('--------------------------------------------------------------------------')