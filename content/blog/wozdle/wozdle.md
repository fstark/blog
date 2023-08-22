---
title: Making Wordle for the Apple1
description: Making Wordle for the Apple1
date: 2023-08-22
order: 1
eleventyExcludeFromCollections: true
tags:
  - 6502
  - apple1
  - wozdle
---

I must admit I wasn't such a fan of the Apple1. But now that I have one, it is my favorite computer.

Started probably 6 months ago, when SiliconInsider started to build a handful and I could get one, so I was intrigued, because I thought maybe we could do some nasty software hack (short answer: unfotunately not, maybe more on that in a future blog post).

It is as close to the original as possible, using the same components, often from the same time period. For all matter, I *have an Apple 1*, it was just built 47 years later. It may not be exactly true, but it is close enough for me.

Frankly, the look of the machine is sick.

Silicon is building a ROM for it, so we started scouring the internets for software, but, to be honest, I found the result to be quite underwhelming. There is the 30th anniversary demo, that displays Woz, Jobs, but not much more in term of "interesting" software. The total machine language games and demos is totalling 150Kb...

So, I decided to create something to showcase the machine. A game. A *known* game, that could be used to demo the machine.

I thought a bit, and I picked to create Wozdle, a perfect Wordle clone for the Apple 1.

It took around two days to code, and I am pretty proud of the result.

But there were 3 challenges to overcome.

## The size

The original Apple1 had 4K of RAM, extensible to 8K (mine), or ever 48K. Software was loaded by either inserting the cassette card and using a cassette player (extremely unreliable), or by having the software on an EEPROM (like the Integer BASIC ROM) and executing it "in place" (meaning that the code is not copied into the RAM for execution).

I decided for that second solution, because the goal is for it to be present in Silicon's card. And instant loading is an interesting feature...

The card will give 32Kb of addressable ROM (with optional page-switching, but I'd rather work with the simplest ROM), so that should be plenty of space, right?

Let me describe the rules of Wordle for you: the computer choses a 5 letter word from a list of 2309 words (called *answers*).Then, the user enters a word, and the computers displays which letters are correctly or incorrectly placed, a clear inspiration from the old Mastermind game.

However, the user cannot enter any combination of 5 letters, he has to enter a valid word. And this is where Wordle gets it perfect: the list of acceptable user words (the *vocabulary*) is larger (12947 words). This enables wordle to know all the 5 letter words, but only choosing from the simplest ones, limiting user frustration.

But that 12947 5 letters words. That's already 64Kb.

Or is it?

### Encoding words

Let's try some compression. It is all about using something we know in our data to encoding information more efficiently.

We can exploit the fact that a byte can store 256 letters, but we only have 26 of them. So we know that 3/8th of the bits are just zeros. If we code the letter on 5 bits, we can code a word on 25 bits.

So, from now on, our words are numbers. 'a' = 1, 'b' = 2, expressed in base 32. This means that 'apple' is 1, 16, 16, 12, 5. In base 25, we do (((1*32+16)*32+16)*32+12)*32+5. Of course, I chose 32, so the computation is much easy to do in binary:

       1     16    16    12    5     1,16,16,12,5           (base 32)
     00001 10000 10000 01100 00101  0b110000100000110000101 (base2)
0000 0001 1000 0100 0001 1000 0101  (idem)
  0   1    8    4     1    8    5   0x184185                (base 16 -- hexadecimal)

In decimal, Apple is 1589637. Note that choosing 'a'=1 and not 'a'=0, gives 'aaaaa' the value 108421. This was chosen to enable a slight optimisation in the 6502 assembly code.

If I encoded the set of words as a bunch of numbers, I would use 323675 bits, or a little over 40K.

### Encoding the 12947 word vocabulary

However, I don't care about order, so I can store this list in any order. So, what about sorting it?

This is a common trick. At this moment, it is easier to store the difference between consecutive elements. For instance, 'apple' is between 'appel' and 'apply', respectively 1589420 and 1589433. Instead of storing 1589637 for 'apple', if I keep the words sorted, I can just say it is 217 after 'appel'. And I can say that by adding 13 to 'apple', we get the next word.

If we apply to the list for words, we get:

words: aahed aalii aargh aarti abaca abaci aback abacs abaft abaka abamp aband abase abash abask abate abaya

numbers: 1089700 1093929 1100008 1100425 1115233 1115241 1115243 1115251 1115348 1115489 1115568 1115588 1115749 1115752 1115755 1115781 1115937...

difference: 7299 4229 6079 417 14808 8 2 8 97 141 79 20 161 3 3 26 156...

It is obvious that the difference is smaller to encode. Let's look at it in hexadecimal, on 3 bytes:

```
00 1C 83
00 10 85
00 17 BF
00 01 A1
00 39 D8
00 00 08
00 00 02
00 00 08
00 00 61
00 00 8D
00 00 4F
00 00 14
00 00 A1
00 00 03
00 00 03
00 00 1A
00 00 9C
...
```

We easily see that all first bytes are zero, most seconds bytes are zero, and in may cases, a single byte is enough to encoded the difference. (There are 126 delta that needs 3 bytes for encoding), the largest one being between 'wytes' (24957107) and 'xebec' (25331875), totalling 374768.

At that point, the encoding is quite easy, and can be inspired from UTF-8:

'0aaaaaaa' => aaaaaaa (0-127)
'10aaaaaa' 'bbbbbbbb' => aaaaaabbbbbbbb (128-16384)
'11aaaaaa' 'bbbbbbbb' 'cccccccc' => aaaaaabbbbbbbbcccccccc (16385-4194304)


Reading the first byte, if it start with a zero, the 7 rightmost bits are the number.
If the second bit is a zero, then the rightmost 6 bits and the next bytes are the number.
Else, the rightmost 6 bits and the two next bytes are the number.

With these two compressions, the 12947 words of the vocabulary are encoded in 17903 bytes. So the project is possible!


### Encoding the 2309 words answer list

Encoding the answer list could have been done with the same process. However, there are less answers, so the differences would be larger, requiring almost always 2 bytes, which would make the list a 4.5Kb data structure.

However, we know that the list of answers is a subset of the 12947 words vocabulary, so a simple 1618 bytes bitmap does the trick. I researched a couple of different optimisations, like adding a bit in the vocabulary encoding, but it is not worth it (this particular one had a cost of 1848 bytes, due to all offsets larger than 63 needing at least 2 bytes)

While not extremely efficient for traversal those two data structures are the core of the Wozdle implementation.

#










REST OF STUFF FOR LATER

b) The UX

c) The code

-> dev env
-> random
-> large letters
-> Astuce du 'zzzzz' en dernier mot ajoute a la liste de mots.
