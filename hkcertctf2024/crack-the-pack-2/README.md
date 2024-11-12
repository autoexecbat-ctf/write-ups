# Crack the Pack (II): Knees and Toes

> It is heard that a snake has hidden some wonderful tool in some obscure corners of a library. Do you know how it works?

## Meta

Challenge author: TWY

Category: misc, crypto

Difficulty: 4/5

Points: 375

Number of solves: 9

## Description

This is the second challenge in the "Crack the Pack" series. While the two challenges are independent of each other, they are similar in nature. Solving the first one allowed me to understand this second one more easily.

In this challenge, we are given two files: a python flag encrypter script and the encrypted output in form of hexadecimal digits.

### Python script

```python
from lzma import compress
from tqdm import tqdm
import random
print("Flag Encrypter")
print("==============")
while True:
    raw_flag = input("Enter the Flag: ").encode()
    if b"\0" in raw_flag:
        print("Only non-null characters are allowed!\n")
        continue
    else:
        raw_flag += b"\0"
        while len(raw_flag) % 6 != 0:
            raw_flag += b"\0"
        flag = b""
        # some integrity marks
        for i in range(0, len(raw_flag), 6):
            flag += raw_flag[i:i+6] + b"\xff\xff"
        while len(flag) < 960 or len(flag) % 8 != 0:
            if len(flag) % 8 >= 6:
                flag += b"\xff"
            else:
                flag += bytes([random.randrange(1, 255)])
        block = bytes([random.randrange(256) for _ in range(8)])
        processed = [block.hex()]
        last = block
        # preserve the links to the previous elements
        for i in tqdm(range(0, len(flag), 8)):
            block = compress(last + flag[i:i+8], preset=9)[-28:-20]
            processed.append(block.hex())
            last = block
        processed.sort(key = lambda _: random.random())
        print("Result:", "".join(processed))
```

### Output

_Only showing the beginning digits_

```
3c977d3e7c4516cd39da90976982fa2d61...
```

## Studying what the encrypter does

The python script does the followings:

1. Pad the flag length to multiple of 6 with null character
2. For each chunk of 6 characters, insert two `\xff` bytes, and pad the whole flag with more `\xff` bytes until reaching a length of 960 which will be a multiple of 8
3. With an initial random 8-byte block, `compress` the block with the subsequent 8 bytes of the flag, where the resulting bytes in offset `[:28:-20]` are used as the encrypted result chunk, as well as the next round's block
4. Similar to "Crack the Pack (I): Head and Shoulders", the encrypted blocks are shuffled to create the final output. The initial random 8-byte is also included in the output.

To illustrate the process:

```

                                  +------------------------+
                                  | Initial random 8 bytes |  = output_0
                                  +------------------------+

Compress and take [-28:-20] in hex
+---+--+--+--+--+--+--+---+---+---+---+---+---+---+---+----+
|  Initial random 8 bytes | first 6 bytes of flag + \xffff | = output_1
+---+--+--+--+--+--+--+---+---+---+---+---+---+---+---+----+

Compress and take [-28:-20]
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+
|  output_1     | next 6 bytes of flag + \xffff | = output_2
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+

Compress and take [-28:-20]
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+
|  output_2     | next 6 bytes of flag + \xffff | = output_3
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+

and so on... until

Compress and take [-28:-20]
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+
|  output_119   | last 6 bytes of flag + \xffff | = output_120
+-+-+-+-+-+-+-+-+---+---+---+---+---+---+---+---+

Encrypted result is created by shuffling all 121 outputs.
```

## Identifying the initial random 8 bytes

Similar to the first challenge in the series, I can find out the initial random 8 bytes from the known flag pattern of `hkcert24{`, because both `output_0` and `output_1` should exist in the output.

A quick check shows that it is `551e6df8737b672b`.

## Studying the output bytes

To be able to solve the challenge, I needed to understand what `[-28:-20]` gives us from the `lzma.compress` function.

From the python documentation, it is creating an xz compressed archive.

I then studied the output of the compressed result `output_1`, according to the xz file format. It took me some time reading and interpreting the specification from https://tukaani.org/xz/xz-file-format.txt.

Since "Crack the Pack (I)" involved calculating the CRC32 hash as in the PNG, when I read the xz file format, I guessed it would be the CRC64 check and it indeed is a CRC64 as I verified the `output_1` against the specification for the location of the header, footer, block, and index.

The CRC64 performs hashing on the uncompressed raw data, which is the 16 bytes shown in the above diagram.

## Implementing the CRC64 hash

A natural instinct is to perform a bruteforce search similar to "Crack the Pack (I)". And the first thing to do is to verify the CRC64 hash for implementing it.

I was not aware of the difficulty of finding the right function to verify the CRC64 hash in Python. From the Python source it seems to be referring to the underlying C code, which I didn't drill further to study how I could obtain just the CRC64 hash from the built-in `lzma` module.

I tried different implementations of the CRC64 available online to realize that there are different forms of the CRC64 hashes. I tried 5 different CRC64 functions before finally getting the right version from https://github.com/hex-in/libscrc, where CRC64/XZ is implemented. Apparently there are different forms of the polynomials for CRC64.

## The bruteforcing hell

Once I started bruteforcing, I realized that a full 6-character bruteforce doesn't run fast. Therefore I assumed that only the flag only contains the characters `_0-9a-z`.

With this character set, bruteforcing 5 characters can complete in a reasonable time. 

The first one is easy because of the known bytes `24{`.

And then the bruteforce went like this:

- `hkcert`: bruteforce from flag pattern `24{`
- `hkcert24{tw0`: `two` should be a complete word, thus `_` is likely the next character
- `hkcert24{tw0_crc32`: for proper grammar `crc32` should have an `s`
- `hkcert24{tw0_crc32s_n4m3`: first I tried `name_`, `named` and `names` although they don't sound quite right. And then I searched for words that start with `name` and found `l` as a likely character.
- `hkcert24{tw0_crc32s_n4m3ly_zl1`: surely it refers to the library `zlib` 
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_`: with an underscore I struggled for a bit to figure out the next word. And then a google search of "crc32 zlib vs" hinted me for the other package `binascii`.
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_b1n45c`: `i` could be represented as `i` or `1` in leetspeak.
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_b1n45ci1_bu7`: it is likely a `but` however `_` does not give me any results. After a series of other tries, I decided to add upper cases and symbols to it. After an hour I got the result.
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_b1n45ci1_bu7_n0_CR`: it should be either `CRC` or `CRT`. I have no idea because this is labelled as crypto category and I am not familiar with it nor the mechanism of `CRC64`.
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_b1n45ci1_bu7_n0_CRC64_lu`: another point for being stuck. The most likely word I could think of was `luck`, or maybe some words beginning with `lun`, or some other characters. While I was about to give up i.e. running a full bruteforce, I searched again on the words beginning with `lu` and I noticed the `lull`. Let's try `lul`!
- `hkcert24{tw0_crc32s_n4m3ly_zl1b_4nd_b1n45ci1_bu7_n0_CRC64_lul}`

It took me like 2 hours for the whole bruteforce.