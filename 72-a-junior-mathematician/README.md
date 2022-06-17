# Challenge 72 - A Junior Mathematician

The question includes 2 files: `chall.py` and `prog.frac`. The description of the question also stated that running the script with the correct flag would print the output `(:`.

## Initial Exploration

We first tried to run the script with some random inputs. It always shows the exact same `):`. Looking at the code, the flow is as follows:

```python
flag = [1] + list(input().encode())
assert len(flag) < 100
primes = gen_primes(len(flag))
n = reduce(mul, [p**k for p, k in zip(primes, flag)])

with open('prog.frac') as f:
    prog = f.read().strip().split('\n')

f = F(prog, n)

while not f.terminated:
    f.step()
```

The user inputs a flag, then the program converts it to a list of ASCII for each character with a `1` in front of the list. Same number of primes are generated and the input number is calculated as 3<sup>f0</sup> * 5<sup>f1</sup> * 7<sup>f2</sup> * 11<sup>f3</sup> * ... * 547<sup>f99</sup>. This number is then processed by class `F` with the list of fractions in `prog.frac`.

## Class `F`, the Main Part

The basic flow is like this:

1. Set `n` to be the input number
2. Loop through the fractions one by one
3. Check if `n * fraction` is an integer. If not, go back to Step 2 to continue to the next fraction.
4. `n` is multiplied by the `fraction`
5. Check if `n & -n == n`. If yes, print `chr((n-1).bit_length() & 0x7f)`.
6. Go back to the first fraction and loop again

The program terminates only when the check at Step 3 is never evaluated as `true` for all of the fractions.

At this point, in `prog.frac`, we know there are a lot of numbers that look like primes and it seems to suggest a pattern. We have no idea when and how the program terminates, nor why the same `):` gets printed out every time with the above class `F` with whatever random inputs.

## Of the Printed Characters

First, by Step 5, we only know it  prints a character out if `n` is a power of `2`, and the printed character has the ASCII code of `power mod 128`. The 3 important characters `():`  are of ASCII code `40`, `41` and `58` respectively. And thus it is trivial the required `n` is 2<sup>40</sup>, 2<sup>41</sup> and 2<sup>58</sup>. These numbers are the numerator of the last 3 fractions in prog.frac.

But we do not want `)`, i.e. the fraction 2<sup>41</sup>/13553. To get the correct flag means we need to make sure it doesn't get printed out, i.e. the number cannot be a multiple of 13553. Then we realize there are so many 13553s as numerator in a section of `prog.frac` which probably why `)` is always printed. At the same time, I want to get 2<sup>40</sup>/13537 to print `(`.

## Examine all fractions to understand the patterns

We decided to understand all the fractions in `prog.frac` to help understand the program flow. At the same time, we wrote a code snippet to verify all the fractions to confirm the understandings.

### Part 1: Line 1 to 700

This is trivial as the first fraction `563/25 = primes[101+i] / primes[i+1] ^ 2` where `i` is from 0 to 699:
```
563 / (5 * 5)
569 / (7 * 7)
571 / (11 * 11)
...
6151 / (5297 * 5297)
```

### Part 2: Line 701 to 1501, or WTF is `6163/3`?

There looks like a pattern of "cancelling effect" of consecutive fractions. But the occasionally large number confused me and took me a while to realize they are actually excessively multiplied by another prime.

The denominator of the first fraction `3` in `6163/3` also looks strange. All other fractions are in the format `primes[101+i] / (primes[100+i] * k)`, where `k` is 1 or another prime, where `i` is from 700 to 1500.

We further checked that there are 260 fractions with `k` not equaling to 1, and all of the 260 strange primes are unique: `[7, 11, 13, 29, 31, ...]`

```
6163 / 3
6173 / 6163
6197 / (6173 * 1669)
6199 / (6197 * 3181)
6203 / 6199
6211 / 6203
...
13537 / 13523
```

### Part 3: Line 1502 to 2301

This is where we have a lot of the unhappy `13553`. The format is simply `13553 / primes[i-700]`, `i` is from 1501 to 2300.

```
13553 / 6163
13553 / 6173
13553 / 6197
...
13553 / 13523
```

### Part 4: Line 2302 to 5302

We see alternating pattern here with 1/5, 1/7, 1/11, etc. We still see the unhappy 13553 as numerator, but the denominator was then found to be `13537 * prime`. _13537_! The happy number we want!

```
13553 / (13537 * 5)
1 / 5
13553 / (13537 * 7)
1 / 7
...
13553 / (13537 * 13523)
1 / 13523
```

### Checking Code

We wrote code to find the odd bits out:

```python
divisors = []
for i, f in enumerate(fractions):
    if i < 701:
        if f.numerator == primes[i+101] and f.denominator == primes[i+1] ** 2:
            continue
    elif i < 1501:
        if f.numerator == primes[i+101] and f.denominator == primes[i+100]:
            continue
        divisors.append(f.denominator / primes[i+100])
        continue
    elif i < 2301:
        if f.numerator == 13553 and f.denominator == primes[i-700]:
            continue
    else:
        if i % 2 == 1:
            if f.numerator == 13553 and f.denominator == primes[int((i+1)/2)-1150] * 13537:
                continue
        else:
            if f.numerator == 1 and f.denominator == primes[int((i+1)/2)-1150]:
                continue
        
    print('wrong', i, f)
```

It prints
```
wrong 700 6163/3
wrong 5501 1/281474976710656
wrong 5502 13567/1099511627776
wrong 5503 1/1024
wrong 5504 1/2
wrong 5505 1099511627776/13537
wrong 5506 2199023255552/13553
wrong 5507 288230376151711744/13567
```

## Running the program

After we figured these out, we did the actual process.

### Part 1:

The beginning `n` is 3<sup>f0</sup> * 5<sup>f1</sup> * 7<sup>f2</sup> * 11<sup>f3</sup> * ... * 547<sup>f99</sup>.

Observing the first 99 fractions, it keeps multiplying 563/5<sup>2</sup> until there are 5<sup>{0, 1}</sup> left. It then keeps multiplying 569/7<sup>2</sup> until there are 7<sup>{0, 1}</sup> left, etc.

The final number after 99 lines = 3 * 5<sup>{0, 1}</sup> * 7<sup>{0, 1}</sup> * ... * 547<sup>{0, 1}</sup> * 563<sup>k<sub>0</sub></sup> * 569<sup>k<sub>1</sub></sup>  ... * 1231<sup>k<sub>99</sub></sup> where k<sub>i</sub> are any non-negative integers.

It is repeated for the next 100 lines, and we realized reading the first 100 lines is better than 99, because the first numerator of the fraction 563 is not the next prime of 547 (line 99), there is 557 in the middle which is never used here.

so, `n` = 3 * 5<sup>{0, 1}</sup> * 7<sup>{0, 1}</sup> * ... * 547<sup>{0, 1}</sup> * 563<sup>{0, 1}</sup> * ... * 1231<sup>{0, 1}</sup> * 1237<sup>k<sub>0</sub></sup> * ... * 1997<sup>k<sub>99</sub></sup>

Finally till the end of part 1, `n` = 3 * 5<sup>{0, 1}</sup> * 7<sup>{0, 1}</sup> * ... * 5297<sup>{0, 1}</sup> * 5303<sup>k<sub>0</sub></sup> * ... * 6151<sup>k<sub>99</sub></sup>

### Part 2:

We started to have an idea of the actual flow of program, before these explorations we thought the successful division may happen at random lines and jump from here to there, upward or downward in the entire `prog.frac`. Now it seems to suggest the flow is one-way, i.e. from Line 1 to the last line but never the other way round.

The magic number 3 in `6163/3` is solved here. The fixed initial factor of 3 gets cancelled, with a new prime 6163 multplied to `n`.

The next fraction `6173/6163` has a cancelling effect to the previous prime 6163. And all the subsequent fractions have the same pattern, **except** the 260 fractions with the strange prime. It sounds like a big light bulb to solve this challenge.

In order to successfully multiply the strange fraction, let say the first one: `6197 / 10302737`, a.k.a. `6197 / (6173 * 1669)`, `n` needs to have the factor 1669, otherwise 6173 cannot be cancelled and in Part 3, `13553 / 6173` will create the unhappy 13553.

So we simply assumed we needed to make all these fractions get multiplied successfully to n, so that all primes from 6163 to 13523 gets cancelled and on line 1501 there is the happy 13537. It implies all the 260 primes `[7, 11, 13, 29, 31, ...]` needs to exist in n after Part 1, i.e. these should have odd power in the original input number of the real flag.

We only focused on the first 100 primes here so our conclusion was: for the input number of the real flag, all the powers of the primes (which is talking about the first 100 primes only) have to be odd if they are in the list of 260 primes.

After Part 2, all the 260 primes are cancelled out, now `n` = 5<sup>{0, 1}</sup> * 17<sup>{0, 1}</sup> * 19<sup>{0, 1}</sup> * 23<sup>{0, 1}</sup> * ... * 5297<sup>{0, 1}</sup> * 5303<sup>k<sub>0</sub></sup> * 5309<sup>k<sub>1</sub></sup> * ... * 6151<sup>k<sub>99</sub></sup> * **13537**

### Part 3:

It checks if n has any prime factor from 6163 to 13523, if there is, it will multiply the unhappy 13553.

By making sure the 260 primes don't mess things up, `n` can remain unchanged in the whole Part 3.

### Part 4:

There is only a single 13537 factor in n and we need to make sure it doesn't get cancelled out.

Considering the pattern of fractions: `[13553 / (5 * 13537), 1 / 5]`. It helps to reassure that `5` cannot exist in `n`, or the successful division of `13553 / (5 * 13537)` will remove the happy 13537 and create the unhappy 13553.

So all the primes which are not in the 260 primes should not exist in `n`. This implies 5, 17, etc. should have an even power in the input number of the flag.
The input number of real flag = 3 * 5<sup>e</sup> * 7<sup>o</sup> * 11<sup>o</sup> * 13<sup>o</sup> * 17<sup>e</sup> * 19<sup>e</sup> * ... * 547<sup>e</sup>, `e` means an even number and `o` means odd.

## Getting Stuck and Final Success

Now we were stuck because we focused only on the first 100 primes. Knowing whether the power of each prime <= 547 is even or odd look not much useful.

After a while we realized the power of larger primes help to create further constraint. Looking at the fraction `563/25` and `1237 / 563`<sup>2</sup>, 563 is not in the 260 primes so it should be of even power.

To get even power of 563, from the first fraction, it requires 5 to be of power of 4k.

And the next related fraction is `1237 / (563 * 563)`. 1237 is also not included in the 260 primes. Its power is even, further requiring 5 to be a multiple of 8k. (since, by bit representation 000, reversed is still 000).

For another example, take the next one: 7 is odd => 2k+1, 569 is odd, making power of 7 as 4k+3. 1249 is even, so power of 7 is 8k+3. (bit representation `110` -> reverse to become `011`).

All the even/odd settings of all the primes help to give the required power of each prime. I exhausted all 8 possible combinations of even/odd settings for the first 3 related primes to prove the formula to output the final number, which is concatenating the bits of these primes in reverse order.

Then I realize each prime has a total of 7 such power which acts like a 7-bit number, e.g. 5 -> 563 -> 1237 -> 1999 -> 2767 -> 3593 -> 4441. It matches the range of ASCII code.

So this gives the flag.
```python
for i in range(1, 100):
    res = ''.join([str((p in divisors)*1) for p in primes[i:i+601:100][::-1]])
    print(chr(int(res, 2)), end='')
```

## Postscript

Finally, I revisit 2 questions:

### Prime factor series 5303<sup>k</sup> * 5309<sup>k</sup> * ... * 6151<sup>k</sup>

They are all zero because the flag won't have any ASCII larger than 127 to create these factors in Part 1. All these prime factors must not appear in `n` throughout the process so they can be safe to ignore and are all zeros.

### For the final few fractions

- 1/(2<sup>48</sup>)
- 13567/(2<sup>40</sup>)
- 1/(2<sup>10</sup>)
- 1/2
- 2<sup>40</sup>/13537
- 2<sup>41</sup>/13553
- 2<sup>58</sup>/13567

#### If it's a real flag

After part 4, `n` = 13537. It goes through 2<sup>40</sup>/13537 to print `(`, then 13567/(2<sup>40</sup>) and finally 2<sup>58</sup>/13567 to print `:`. It can then exit when the 2<sup>58</sup> keeps getting divided by 2<sup>k</sup> in the final lines to get n=1.

#### If it's a wrong flag

In Part 2, one fraction would be failed to get divided, let say 6199 / (3181 * 6197) for example. The number n failed to multiply 6199, the next fraction will get failed dividing 6199 and so as all subsequent fractions failing in Part 2. From 6163 to 13523 there will be one and only one prime factor in n.

In Part 3, this factor will be removed in n but multiplied by 13553. In Part 4, all other prime factors in n will be removed. So n = 13553.

Finally it goes through 2<sup>41</sup>/13553 (`)`), 13567/(2<sup>40</sup>), 1/2 and 2<sup>58</sup>/13567 (`:`) to print `):`

# Postmoterm

This is mentioned by the author of the challenge mystiz in the discussion thread after the competition. In hindsight, our approach sounds like deriving the question from the _first principle_ by observing the patterns, while the more intended way is _probably_ a less convoluted one. Maybe we should have better Google-fu ;)
