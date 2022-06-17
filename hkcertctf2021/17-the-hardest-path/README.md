# Challenge 17 - The Hardest Path

The question's attachment contains two files: `lost.py` and `chall.py`. Both are hosted on the server, with `chall.py` as the entry point.

## Part 1: Pre-challenge

The server prompts for input with a input text. From the provided source files, the challenge comes from the method `work()`, before the real program starts to run.

```python
def work():
    challenge = os.urandom(8)
    print(f'🔧 {base64.b64encode(challenge).decode()}')
    response = base64.b64decode(input('🔩 '))
    h = hashlib.sha256(challenge + response).digest()
    return h.startswith(b'\x00\x00\x00')
```

```python
if __name__ == '__main__':
    if work():
        data = input('🥺 ')
        attempt(data)
    else:
        print('😡')
```

It creates a challenge from 8 random bytes, and requires a response which will together produce a SHA256 hash starting with 3 zero bytes.

To produce the response (with no time limit constraints), we copied this and wrote a program to try by brute force, randomly trying from "crtA1000000" to "crtA9999999", where `s` is the provided 8 bytes.

```python
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
```

## Part 2: Real challenge

After passing the challenge, it asks for another input `data` again. It is used to call `attempt(data)`, which is:

```python
def attempt(data):
    from lost import _328518a497015157

    try:
        _328518a497015157(data)
        flag = os.environ.get('FLAG', 'hkcert21{***REDACTED***}')
        print(flag)
    except:
        print('no good!')
```

Inputting some random `data` will give `no good!` due to some exceptions raised. Hmmm.

The function `_328518a497015157` comes from `lost.py`. Searching for the entry function gives:

```python
_328518a497015157 = _f42fb5e137443877(
    False,
    "_ef5d07da6a407ff3",
    "_3f49b6a9053121fb",
    "_60de30732830eab8",
    "_3ff69bef8add0e90"
    )
```

There are many similar variables defined this way. The other ones either point to `_29aa7a86665899ed`, or look like this one, calling the same function `_f42fb5e137443877` with some arguments (boolean and 4 other hashes, where the hashes are indeed other references defined in the same manner).

One thing that caught our attentions was the `False` in seemingly all of these definitions:

```python
_dd377fdddbc1ca82 = _f42fb5e137443877(False, "_9fa5ecfdfe2f8d02", "_8628b28b6b898f79", "_dab58a4eeaf5c5dc", "_a8a089d281aa1f40")
_a72dc063ab16951b = _29aa7a86665899ed
_fdd8ed43b529e980 = _f42fb5e137443877(False, "_7ad2b07b48eb7969", "_b3dd8196acf6e67a", "_cf33197e075e5b3e", "_e09fe52a1f7140f8")
_e47e70a70c396bad = _29aa7a86665899ed
_d14eff864727fb64 = _29aa7a86665899ed
_0a9b78d1bf594507 = _f42fb5e137443877(False, "_9b33eb0ed052e9a5", "_d3c8b4864b10745c", "_6ec5d4283aa44cec", "_ff672abf7ebed75c")
_5a2af0de8a2731dd = _29aa7a86665899ed
_5f9b6d9b80a8e9ca = _f42fb5e137443877(False, "_a12c9e129437f3da", "_a62193aa778ee5c7", "_9d112eb1531855ee", "_0869ae9abf8f7746")
_42c334e0319195ae = _29aa7a86665899ed
_13bd7af107157299 = _29aa7a86665899ed
```

Therefore we searched for `True` and found only one entry. There must be something special with it.
```python
_8b0eb6f195ae182a = _f42fb5e137443877(True, "_92ccf583b1b065ea", "_d3084505a4a12123", "_e335a503c47e5243", "_ebff1548ca6e8dbd")
```

Looking back at the top of `lost.py` for the meaning of the function `_f42fb5e137443877`:

```python
mystery = 'NEWS'

def _29aa7a86665899ed(_050ca071ab51aece): raise Exception('😵‍💫💫🧱')

def _f42fb5e137443877(_a78810bb76cc7d70, *_ab1bbf35017f4f42):
    def _e6aea2db2242b19f(_41d28eb8c27952c3):
        if len(_41d28eb8c27952c3) == 0:
            if not _a78810bb76cc7d70: raise Exception('🤷🏁😕')
            return
        _03d38fa3a589db14, _41d28eb8c27952c3 = _41d28eb8c27952c3[0], _41d28eb8c27952c3[1:]
        return globals()[_ab1bbf35017f4f42[mystery.index(_03d38fa3a589db14)]](_41d28eb8c27952c3) if _03d38fa3a589db14 in mystery else _e6aea2db2242b19f(_41d28eb8c27952c3)

    return _e6aea2db2242b19f
```

Let's try to rewrite the function `_f42fb5e137443877` by hand:

```python
def f(some_boolean, *four_functions):
    def some_method(x):
        if len(x) == 0:
            if not some_boolean: raise Exception()
            return
        a, x = x[0], x[1:]
        return globals()[four_functions[mystery.index(a)]](x) if a in mystery else some_method(x)
    return some_method
```

This function returns a function `some_method`, which accepts our input `data` initially, and at each step it calls one of the `four_functions` as pointed by the each of the character from the string `x` in `mystery` (`'NEWS'`).

The behavior seems to suggest going to one of the four functions. Coupled with `mystery` defined as `NEWS` gives a not-so-subtle hint that it is like walking through a maze grid, using the directions north, east, west or south as the instruction.

The function that raises the exception `_29aa7a866665899ed` further confirms this. Those act like bombs in the maze. Once the bomb is hit, an exception is raised, causing the flag not to be printed.

And the only `True` from the function discovered earlier clearly corresponds to the goal as it will simply `return` when the input instructions are all parsed, thus avoiding any further exceptions being raised.

The challenge can be now rephrased as:

> Given a maze, provide an input string consisting of a series of directions of either `N`, `E`, `W` or `S`, in order to walk through the maze from the start point `_328518a497015157` to the goal `_8b0eb6f195ae182a`, avoiding all the bombs denoted by `_29aa7a86665899ed`.

Aha, this is why it is called "the hardest path"!

### Solving

To solve for this, the most straightforward approach is to do breadth-first search (BFS) to find the shortest path.

We re-created the maze as CSV-like data, and wrote another Python script to perform the BFS.

Data `map.csv` looks like:

```
_4bb2a1371293bd5a,False,_d9aaf7e9f84e9234,_00535df39faa03d5,_3ad958f380966c16,_4e0a87b74c7dbc69
_0d4cf4aa713884fb,False,_3a6fa775b54b74fe,_4ce19e25d33f09f1,_1d373d3c7374ab6b,_8ddcb8dce977f325
_2f00e51306a05b87,_29aa7a86665899ed
_2ad8b08f455fb7bf,_29aa7a86665899ed
  (...that goes on for around 40000 lines)
```

And the Python script is as follows: (we used the row index to represent each squares in the grid, thus the starting point is `27267` and the goal is `10421`):

```python
import csv

# each square is represented by its row index in the map.csv data
# illustration: [start, visit N, visit E, visit W, visitS, ...]
# full_list:    [  130,       8,      13,    111,      30, ...], # visited nodes
# back_index:    [  -1,       0,       0,      0,       0, ...], # index of full_list
# back_direction: [ '',     'N',     'E',    'W',     'S', ...],
full_list = [27267]
visited = set([27267]) # just a set representation of full_list
back_index = [-1]
back_direction = ['']
current_index = 0 # current node being explored, as index in full_list
d = ['N', 'E', 'W', 'S']

current = 27267 # starting point
answer = 10421 # the goal

result = [] # maze data, to be read from map.csv
mapping = dict() # a helper mapping to map from the hash to row index

with open('map.csv') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for row in r:
        result.append(row)
for i in range(0, len(result)):
    mapping[result[i][0]] = i

while True:
    current = full_list[current_index]
    for i in range(4):
        try_node = mapping[result[full_list[current_index]][2 + i]]
        if try_node == answer:
            s = d[i]
            next_index = current_index
            while next_index != 0:
                s = back_direction[next_index] + s
                next_index = back_index[next_index]
            print(s)
            exit()
        if try_node in visited:
            continue
        if len(result[try_node]) == 2:
            continue
        full_list.append(try_node)
        back_index.append(current_index)
        back_direction.append(d[i])
        visited.add(try_node)
    current_index += 1
```

After providing the correct path, the flag was shown. Solved!
