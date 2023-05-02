# YARA Trainer Gym

## Description

This write-up is solely written for the sake of how much fun I enjoyed in this pokemon-themed CTF.

There is a yara_rules.yar and a website given. The website allows users to upload a file and click `FIGHT!`. When I tried to click `FIGHT!` without uploading any file, it shows I am defeated by each of the 8 rules. Clearly these rules refer to the 8 rules defined in the `yara_rules.yar`. So what I have to do is to upload a file that comply with all the 8 rules.

![Gym Fail](gym_fail.png)

## Rule 1
This refers to ELF header so I need to upload an ELF file, the easiest way is to write a C program and compile it.

## Rules 2, 4 & 6
All these 3 rules requires the ELF file to contain the required strings, which include
- `jessie`
- `james`
- `meowth`
- `i am too tired`
- `sleepy time`
- `aqvkpjmdofazwf{lqjm1310<`

There are several ways (listing only the ones I know) to put strings as consecutive bytes into a program binary:

1. String Variable Declaration

For string declaration like `char a[8] = "jessie";`, it only works for strings of at most 8 bytes. Because for any variables in the program, they are stored in the stack memory. To move the strings to the stack, it requires the 64-bit register to do the operation, it could only handle 8 bytes at a time. For example, for short strings like `AABB`, it first `MOV` `AABB` to `RAX` register, then moves `RAX` content to the stack memory. The whole string `AABB` still remains as consecutive bytes. But when we declare a 10-byte string `AABBCCDDEE`, it first `MOV` `AABBCCDD` to `RAX` and then `MOV` `EE` to `RDX`, then it moves `RAX` to the stack memory and also next the `RDX`. The `MOV` operation separates `AABBCCDD` and `EE` in the compiled binary and so the entire string does not appear as consecutive bytes.

2. PUTS function

`puts("rule 6: aqvkpjmdofazwf{lqjm1310<");`, the most straightforward way to include a string as consecutive bytes in the compiled binary. It will allocate consecutive bytes in the **binary** itself to store this constant string.

3. Constants

`const char rule4[] = "im so tired";`, the principle is the same as the `PUTS` function by not declaring it as a variable, getting stored in the binary directly.

```c
#include <stdio.h>
#include <stdint.h>

// RULE 4
const char rule_4[] = "im so tired || sleepy time";

int main(){

  // below 3 strings are < 8 bytes so it can be put here
  char rule2_1[8] = "jessie";
  char rule2_2[8] = "james";
  char rule2_3[8] = "meowth";

  puts("rule 6: aqvkpjmdofazwf{lqjm1310<");

  return 0;
}
```

## Rules 3 & 7
After compiling the above source to a binary file `prog`, these 2 rules are about ELF sections. By `readelf -S prog`, I know there are 31 sections in the compiled binary, I need to add 9 sections which one of them has to be with the name `poophaha`.

```
echo "wwww" > mydata
objcopy --add-section poophaha=mydata --set-section-flags poophaha=noload,readonly prog prog
objcopy --add-section .a=mydata --set-section-flags .a=noload,readonly prog prog
objcopy --add-section .b=mydata --set-section-flags .b=noload,readonly prog prog
objcopy --add-section .c=mydata --set-section-flags .c=noload,readonly prog prog
objcopy --add-section .d=mydata --set-section-flags .d=noload,readonly prog prog
objcopy --add-section .e=mydata --set-section-flags .e=noload,readonly prog prog
objcopy --add-section .f=mydata --set-section-flags .f=noload,readonly prog prog
objcopy --add-section .g=mydata --set-section-flags .g=noload,readonly prog prog
objcopy --add-section .h=mydata --set-section-flags .h=noload,readonly prog prog
```

## Rules 5 & 8
Rule 5 is about a large entropy, requiring the binary to contain bytes as random as possible. The formula of calculating entropy is like this:
for each distinct byte, we calculate `p = count(byte) / len(program)`, then sum all `-p * log2(p)`. I can append many random bytes at the end of `prog` to achieve this. Rule 8 is about file size between 1MB and 2MB. Therefore combining with rule 5, I added `4100 * 255` random bytes at the end of the file.

```python
import os
with open("prog", "ab") as f:
    f.write(os.urandom(4100*255))
```

There are other ways like including a long line in the c source to repeat thousands of array from 0 to 255, anything works.

## Final
I upload this file to fight the gym and the flag is shown on the page. :)