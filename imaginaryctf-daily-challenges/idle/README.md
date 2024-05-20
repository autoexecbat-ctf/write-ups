# Idle

## Introduction
This is an educational pwn challenge from ImaginaryCTF Daily Challenges. The intended solution is to use `ret2dlresolve`. Yet I didn't know about this, so I leaked `libc` by using the `syscall` function at near the start bytes of `alarm` function

## Exploit
Using `ROP`, read the last byte into the `alarm` function in the `GOT` table. Modify its last byte so that it is the `syscall` instruction.

Then we can trigger the `syscall` to call the `write` instruction to leak the address of the `alarm` function in libc, thus getting the `libc` base and also the `libc` version.

It is then trivial to call `system('/bin/sh')`.