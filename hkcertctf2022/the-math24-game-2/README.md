# The Math24 Game 2 雷生春堂

## What we learned from Game 1

- snap game
- HTTP Requests involved
    - `gameNew`
    - `gameAnswer`

## Whether the methodology from Game 1 applies to Game 2?

- mathematically not working
- the category of the challenge is misc, not web

## First try

Without other ideas, I decided to try parsing the images, recognizing it, and send back the results to the server.

- how an image is represented
- hash it ("rainbow table")

## The obstacle appears

While we thought we have completed the challenge, the script failed at the 101th game (IS IT 101th? or 102 or 100).

Going back to the snap game, I saw the card images changed: they became blurred, with noises, rotated and sometimes flipped. It was an additional card set not encountered before.

(TODO: insert samples here)

## Experiment 1 - Machine learning

## Experiment 2 - OCR

Tesseract

## Experiment 3 - Matching corner image pattern

## Ready to give up

Despite the hours I struggled on this challenge, I was ready to give up, so I went to bed.

The next day I woke up, I still wanted to complete it. And I started to think of other ways (aka more stupid ways) to complete it.

## Experiment 4 - Building a larger rainbow hash

- input the number of any unrecognized cards during the game, for the script to simultaneously save the hash
- the hashes count growed quickly meaning that there are hardly duplicates. The card set seemed to be huge.
- This was the first time I tried this method, while this had proved that the hash method did not work, I observed that I still got over 2300 coins with this approach at the end of the 15 minutes. I even spent some time debugging the program when the script encountered error upon the 101th game!

Why not speed up this manual recognition process to get to 2700 coins?

## Final experiment - "image recogniation" done in real time by human

I did two improvements:

1. Previously the manual recognition operated on a card-by-card basis. When a card was not recognized, it showed up on my screen, and I entered the number of that card. Given that the hash method was not working, it will be much faster to show up all the 4 cards on the screen, and I could enter the 4 numbers in one go.

2. While still not too convinced (aka lazy) to find and implement a complete 24 solver, I went on to add a few more formula on solving to increase the chance to find a 24 solution. (If it failed and I got close to 2700 coins, I could still improve the 24 solver by implementing a complete one)

- First 100 games require 1.5 to 2 minutes
- With 13 minutes left, we need to solve 170 more games, it means that on average one win is required per 13 * 60 / 170 = 4.5 seconds

Let's start:

(TODO: insert gif here)

During the contest, I got 2900 coins when there were 30 seconds left. I was so excited and I went to shop and crafted for the flag.

So it is a visual recognition and a typing speed test, on top of some HTTP request handling, image parsing and displaying, and a naive "game 24" solver.

## Post mortem?

I didn't believe it is the intended solution because the timing is tight, and it was like doing the recognition manually, utilizing my visual recognition and typing speed.

I was shocked when I heard that machine learning was the intended solution. It simply showed that I am still a novice ctf player.
