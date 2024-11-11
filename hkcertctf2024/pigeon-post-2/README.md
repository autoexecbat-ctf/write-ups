# Pigeon Post (2)

## Description

We are given the `chall.py` which runs a server to accept communications between `Alice` and `Byron`. The communication is secured through `Diffie Hellman key exchange protocol`.

## Initial Study

As a quick sanity check, I checked whether the given `p` is a safe prime, and it is. With reading the communication codes, there will be no easy way to leak the shared secret.

## Solving

We observed that `Alice` and `Byron` send messages depending on what they received, and react differently. We also understand `AES` under `CTR` mode generates ciphertext which is of the same length of plaintext.

Since we are given a sample `nonce + ciphertext` of the message `done!` from `Alice`, passing it directly to `Byron` gives `f'what is the flag? I have the secret {self.secret}'`. Note that this secret is a random 8-byte token, not the flag.

Continuing the communication, we got like below

| Receiver | Incoming Message                                     | Outgoing Message                                     | Message Length |
|----------|------------------------------------------------------|------------------------------------------------------|----------------|
| Byron    | done!                                                | what is the flag? I have the secret 1234567812345678 | 52             |
| Alice    | what is the flag? I have the secret 1234567812345678 | the flag is hkcert24{.............}                  | 67             |

We know the flag is of length 45 characters in between the curly brackets.

We can then make use of the `XOR` properties of `AES CTR mode` to test which flag character is correct, by making it passing the flag regex format check `hkcert24{.*}` with the ending `}`

Invalid sample is:

| Receiver | Incoming Message                                     | Outgoing Message                                     | Message Length |
|----------|------------------------------------------------------|------------------------------------------------------|----------------|
| Byron    | the flag is hkcert24{a                               | too bad...                                           | 9              |
| Alice    | too bad...                                           | what happened?                                       | 14             |

Valid sample is:

| Receiver | Incoming Message                                     | Outgoing Message                                     | Message Length |
|----------|------------------------------------------------------|------------------------------------------------------|----------------|
| Byron    | the flag is hkcert24{}                               | nice flag!                                           | 9              |
| Alice    | nice flag!                                           | :)                                                   | 2              |

And we can brute force each character of the flag, like this. When we hit the correct ending curly bracket, we xor the byte in the encrypted text, with the tested character, and with `}` to get the correct character in the flag.

| Receiver | Tested Flag                    | Try XOR last char to make it "}" | Outgoing Message  | Message Length | Remark                                   |
|----------|--------------------------------|----------------------------------|-------------------|----------------|------------------------------------------|
| Byron    | the flag is hkcert24{a         | the flag is hkcert24{,           | too bad...        | 9              | Keep brute forcing the first character   |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |
| Byron    | the flag is hkcert24{b         | the flag is hkcert24{/           | too bad...        | 9              |                                          |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |
| Byron    | the flag is hkcert24{0         | the flag is hkcert24{}           | nice flag!        | 9              | Until we got the correct format          |
| Alice    | nice flag!                     | nice flag!                       | :)                | 2              |                                          |
| Byron    | the flag is hkcert24{0a        | the flag is hkcert24{0r          | too bad...        | 9              | test the next char                       |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |
| Byron    | the flag is hkcert24{0b        | the flag is hkcert24{0q          | too bad...        | 9              |                                          |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |
| Byron    | the flag is hkcert24{0n        | the flag is hkcert24{0}          | nice flag!        | 9              | getting the 2nd char                     |
| Alice    | nice flag!                     | nice flag!                       | :)                | 2              |                                          |
| Byron    | the flag is hkcert24{0na       | the flag is hkcert24{0n/         | too bad...        | 9              | starting the 3rd                         |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |
| Byron    | the flag is hkcert24{0n3       | the flag is hkcert24{0n}         | nice flag!        | 9              | and continue for the entire flag         |
| Alice    | nice flag!                     | nice flag!                       | :)                | 2              |                                          |
| Byron    | the flag is hkcert24{0n3a      | the flag is hkcert24{0n3C        | too bad...        | 9              |                                          |
| Alice    | too bad...                     | too bad...                       | what happened?    | 14             |                                          |

This is a straightforward challenge and then I got the flag.