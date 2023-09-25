# Packtom

## Description

There is no code given, only the remote server which tells me
- `abc = Q(a+b+c)    ... (1)`
- `a` is the byte-to-long representation of the flag
- `b` and `c` are integers
- `Q` is given

It is actually easier than I thought, and luckily I got the first blood. After re-writing this solution I feel it's even much more easier as I did redundant work when I was solving it.

## Solving

I tried getting 100 results of Q, hoping to get some factors of `a` by using their gcd. However none of them share a common factor. I then suppose `Q` will never share any factors with `a`. so, `a+b+c` has to be factor of `a`, i.e.

`b + c = ka      ... (2)`, for some integer `k`

then we get from `(1)` and `(2)`,

`bc = Q(k+1)     ... (3)`

now how about factorizing Q, I discovered all 100 results of Q consist of only 2 prime factors, one is large, one is small.

from `(3)`, I assume the large one is `b`, the smaller one is `c'`, where `c = c'(k+1)   ... (4)`

by `(2)` and `(4)`,

`b + c'(k + 1) = ka   ... (5)`

Rearranging the equation, our flag, `a = c' + (b + c') / k`. Since `a` has to be an integer, `b + c'` has to be a multiple of `k`. We do factorization on `b + c'`, there is a couple of large factors that it took me like 30 minutes to solve by ECM in sage. At least it was solvable for this example I have. After factorizing `b + c'`, it is easy to find `k` by enumerate all factors of `b + c'` to solve for the flag.

## My Actual Solving Case

- `Q = 2255148506409374822213560880031843887908030817513786398376996781988010870941028037367400309771969276769251129106323247547072532397135585134885834602794363781815723482255779581484831336523413887641269533153809755367689256220533942066839`
- `b = 780307091687952537333086277975382446619346746509004707892003949512526794457957150226913916124491840441778140801132231079258365489548900621417005753817120614177170098097916748606288774882489481201115536031544285450364767352851`
- `c' = 2890078189`
- factors of `b + c'`: `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 62383, 107881, 239671, 7210811, 25412885466071, 197233956417571, 6339463947863, 4282412129873459, 959892357646349880838483691, 12075985995084301839526511465663891, 2076839734844266912272768540864372860263947013558103421481411227595045386376937203]` (The last 3 factors took me like 30 minutes)
- by enumerating the factors of `b + c'`, I found `k = 19867603614704910809253304388159084637451471934004430560354338465393387541378899490473115401420268548664347567360` 