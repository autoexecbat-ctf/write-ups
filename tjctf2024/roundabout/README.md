# Roundabout
## Introduction
This challenge used [age encryption](https://github.com/FiloSottile/age) to encrypt the flag using a password. There are 4 files given:
1. `secret.txt`: encrypted flag
2. `amontillado.txt`: a passage which some sampled words in it form the 50-letter password
3. `hint.txt`: the graph structure connecting every neighbouring characters in the password, with some random added edges to prevent easy password recovery.
4. `enc.py`: the source code to generate the files and encrypt the flag

The age encryption is difficult to break, and the hint suggests that we need to recover the password in order to decrypt the `secret.txt`.

## Stage 1: Get the list of possible words
Using `networkx` library, it is easy to check which word could exist in the password.

## Stage 2: Easy words recovery
First we examine the characters of the password, given by the 50 nodes. Each character in the password has a unique node id so the same character in the password won't be represented by the same node in the graph, a.k.a. if the first and last letters are `r`, they are different nodes in the graph.

The sorted 50 characters is `aaacddddeeeeeefffggiiiiillmnnnnnnooppqrrrrrsstttuu`, we see the rare characters `q` in english words. We can try to recover the word containing `q` via the edges, which is `requesting`. there are 2 possible options to the node id of the beginning `re` but the rest of it, `questing`, is recovered.

Then we also check the edges connected to each node. We found there are only 3 edges connecting the `c` node. After first removing the edges connecting the known node of `requesting`, we found the `c` word is `recoiling`. All node ids of `recoiling` are known.

There are only 31 characters left in the password, we don't see any easy word recovery anymore.

## Stage 3: Get the remaining possible words
We can first screen the words again after removing the edges connecting to the known nodes of the words `requesting` and `recoiling`. There are only 42 words left.

Notice there are 4 `d`'s in the remaining characters.
I didn't adopt this `d` part when I was solving the challenge, but the overall idea is the same even if this step is omitted, the drawback is on the exhaustion time only.
With that many `d`'s, first I found out there are only 16 words with `d`, one of them consisting of 2`d`'s: `understand`. We can exhaust the combination of these `d` words, and exhaust the words without `d` together to find valid words combination to the password.

## Stage 4: Done
We get the words are `friend`, `off`, `piled`, `recoiling`, `requesting`, `understand`, `rampant`. The password is `requestingpiledunderstandrampantrecoilingfriendoff`.

## Final Words
It happened to me I have been doing more graph challs recently, including this one and `Hikarrro` from `DEF CON CTF Qualifier 2024`.