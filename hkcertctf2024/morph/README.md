# Morph

> Binary sometimes mixed together, just like fried rice or bibimbap.

## Meta

Challenge author: harrier

Category: reverse

Difficulty: 3/5

Points: 300

Number of solves: 53

## Description

We are given a linux binary, which asks for a serial key, reading it to the `flag` variable as shown in the decompiled code.

The decompiled code from Ida shows that it does a series of `verify` operations, from 0 onwards. While Ida shows up to `verify_14` in the decompiled code, looking at the function list suggests that `verify` functions exist from 0 to 53, in a shuffled order inside the binary.

Perhaps the decompilation fails to shows all the nesting from my default setting. But let's assume it calls the functions in the same way, as suggested by a quick glance through the assembly codes.

_I learned from the write-up discussion that it is due to the `noreturn` attribute resulted from the xor'ed code._

```cpp
decompress((char *)verify_0, 86, 50);
  if ( verify_0(&flag) )
  {
    decompress((char *)verify_1, 86, 112);
    if ( verify_1(&flag) )
    {
      decompress((char *)verify_2, 86, 115);
      if ( verify_2(&flag) )
      {
        decompress((char *)&verify_3, 86, 53);
        if ( (unsigned __int8)((__int64 (__fastcall *)(std::string *))verify_3)(&flag) == 1 )
        {
          decompress((char *)verify_4, 86, 121);
          if ( verify_4(&flag) )
          {
// seems to have the same pattern until verify_53
```

## Studying the `verify_*` functions

Looking into the `verify_0` function, Ida doesn't show any meaningful decompiled code.

Since `verify_0` is also treated as a string (character pointer) in the function `decompress` function call, there is likely something going on there.

It turns out the the `decompress` function call is straightforward and looks like this:

```cpp
void __cdecl decompress(char *memory, int size, char k)
{
  int i; // [rsp+1Ch] [rbp-4h]

  for ( i = 0; i < size; ++i )
    memory[i] ^= k;
}
```

It is performing an xor operations with constant `k` to the 86 characters starting from `verify_*`.

Being new to such kind of setups, I hoped to verify whether the decompressed result looks like a function call in assembly call. With my brother's help, I was able to verify that the decompressed result starts with a function call.

`verify_0` is at position `0x5AE05` in the binary for `decompress((char *)verify_0, 86, 50);`.

Performing the xor shows the following bytes:

```python
b = open('morph', 'rb').read()
print(bytearray([x^50 for x in b[0x5ae05:0x5ae05+86]]).hex())

# f30f1efa554889e55348...
```

Putting this into the [https://shell-storm.org/online/Online-Assembler-and-Disassembler/](online disassembler), the disassembly code is as below and this is exactly the start of a function call!

```
0x0000000000000000:  F3 0F 1E FA    endbr64
0x0000000000000004:  55             push    rbp
0x0000000000000005:  48 89 E5       mov     rbp, rsp
0x0000000000000008:  53             push    rbx
```

Thus this program performs xor on its own code to restore the function code.

## Patching the binary

Soon after this discovery I realized I could try to patch the binary and re-open it in Ida to check the real function codes.

From the pattern of the function calls, it looks like all functions have the same length of 86 bytes but each with a different value for the xor operation.

To find the xor value, I copied the assembly code and locate the codes setting the xor value:

_Noteice how there are different forms in the assembly code while it takes only one byte for the xor operations.

`xor.txt`:
```
.text:000000000025B0C1                   mov     edx, 32h ; '2'  ; k
.text:000000000025B0F1                   mov     edx, 70h ; 'p'  ; k
.text:000000000025B121                   mov     edx, 73h ; 's'  ; k
.text:000000000025B151                   mov     edx, 35h ; '5'  ; k
.text:000000000025B181                   mov     edx, 79h ; 'y'  ; k
.text:000000000025B1B1                   mov     edx, 0FFFFFF96h ; k
.text:000000000025B1E1                   mov     edx, 54h ; 'T'  ; k
.text:000000000025B211                   mov     edx, 0FFFFFF8Ah ; k
.text:000000000025B241                   mov     edx, 6Ah ; 'j'  ; k
.text:000000000025B271                   mov     edx, 39h ; '9'  ; k
.text:000000000025B2A1                   mov     edx, 0FFFFFF90h ; k
.text:000000000025B2D1                   mov     edx, 0FFFFFFD6h ; k
.text:000000000025B301                   mov     edx, 2Bh ; '+'  ; k
.text:000000000025B331                   mov     edx, 0FFFFFFA3h ; k
.text:000000000025B361                   mov     edx, 7          ; k
.text:000000000025B391                   mov     edx, 0          ; k
```

I also extracted the order of the functions by basically manual typing `[43, 9, 30, 24, ...]`

```python
xor = open('./xor.txt', 'r').readlines()
def get_xor(i):
    # sorry for the random logic used to parse the xor value out
    line = xor[i]
    end = line.index(';')
    l = line[54:end].strip()
    if end - 54 > 5:
        if len(l) > 7:
            return int(l[-3:-1], 16)
    if l[-1] == 'h':
        return int(l[:-1], 16)
    return int(l)

start = 0x59de5
func_orders = [
    43, 9, 30, 24, 42, 35, 22, 10, 28, 44,
    20, 2, 5, 27, 1, 38, 52, 40, 32, 17,
    31, 7, 11, 25, 49, 36, 8, 47, 41, 15,
    39, 45, 51, 46, 53, 26, 50, 6, 23, 19,
    14, 29, 4, 48, 16, 13, 21, 33, 0, 12,
    37, 3, 34, 18,
]
assert len(func_orders) == 54

b = open('./morph', 'rb').read()
for l in range(0, 54):
    i = func_orders[l]
    x = get_xor(i)
    addr = start + 86 * l
    new_b = b[0:addr]
    for c in range(0, 86):
        new_b = new_b + (b[addr + c] ^ x).to_bytes(1)
    new_b = new_b + b[addr + 86:]
    b = new_b

with open('./patched', 'wb') as f:
    f.write(b)
```

## Revealing the real function codes

It works as expected to restore the functions. Ida shows the decompiled code nicely:

`verify_0` checks if the 49th xor 50th character is 88. And all other functions do the same thing.

```cpp
bool __cdecl verify_0(std::string *flag)
{
  unsigned __int8 v1; // bl

  v1 = *(_BYTE *)std::string::operator[](flag, 48LL);
  return (v1 ^ *(_BYTE *)std::string::operator[](flag, 49LL)) == 88;
}
```

## Getting the flag

After another round of manually entering all the xor results (too lazy to come up with anything for 54 numbers), I was able to obtain the flag:

```python
lst = [
    3, 8, 6, 23, 6, 70, 6, 79, 8, 64,
    95, 10, 57, 50, 93, 84, 85, 87, 31, 72,
    95, 9, 56, 60, 83, 84, 87, 108, 43, 28,
    88, 111, 43, 28, 89, 4, 106, 54, 92, 106,
    49, 94, 100, 11, 30, 30, 50, 89, 88, 27,
    67, 70, 65, 78,
]
flag = 'h'
for x in lst:
    flag = flag + chr(ord(flag[-1]) ^ x)
print(flag)
```

`hkcert24{s3lf_m0d1fy1ng_c0d3_th0_th15_i5_n0T_A_m4lw4r3}`
