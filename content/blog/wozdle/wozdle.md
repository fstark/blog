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

## The UX

What I find a big part of the fun of developping for vintage computers is that Iwe operate within a set of hard constraints. The graphical rendering is often one of the most stringent one. In the case of the Apple 1, here is the list of constraints, which are not apparent when looking at a screenshot ("oh, this looks like an older Apple ][!"]):

* Screen is 40x25 characters
* There is no color
* There are 64 characters:
```
@ABCDEFGHIJKLMNO
PQRSTUVWXYZ[\]^_
 !"#$%&'()*+,-./
0123456789:;<=>?
```

Those are "normal" constraints, but the we get into the harsher ones:

* You can only write one character per screen-refresh (16ms)
* This character is always at the cursor position
* You cannot position the cursor on screen
* You cannot clear the screen

There is one fortunate positive:

* Carriage return and associated scrolling is as fast as writing a character

When you look at those constraints, you understand that the Apple1 screen really is a Teletype, one that shred the paper every 24 lines. What we are really doing is design Wordle for a teleptype.

{% blogimage "img/apple2-text-screen.png", "The upside is that you can use the grid that came page 16 of the original Apple2 manual" %}

We want, at any point in time, the display to contain *at least*:

* An indication of the game progress (how many guesses di you made)

* The history of the previous guesses

* The responses for each of those guesses (which characters were properly placed, which we not properly placed, which are not in the target word)

* The list of characters you have not tried yet.

* Nice to have: the list of character you already found

The last two are displayed as a keyboard fashion on the web-based wordle. This would be a nice touch to keep.

The core problem is that filling the screen with information takes 16 seconds. And as we cannot update what is already displayed, it is obvious that we need to have some sort of line-oriented approach.

Based on those constraints we iterated into the following design principles:

* Game play will be over 4 lines blocks

* As there is at most 6 turns, the previous guesses will always be visible on screen

* If there is any mistake made in entering, we will scroll out and redraw the whole screen, as there is no way to "undo" what we displayed.

* The guesses will be placed on the left of the screen, so they can be displayed quickly

* The right side will contain the "keyboard", with the status of each letter.

* We will only draw the keyboard for the current solution. If we need to refresh the screen, we will not draw the keyboard for any guesses but the last.

Displaying a "full" 4 lines guess takes 16ms times 40 times 4 to display, which is 2.5 seconds.

Displaying only what the user entered followed by the feedback and two empty lines costs 16ms * 22, which is .3 seconds, almost 10 times faster.

In order to have some "breathing room", we will add a space between each word letter. This means that the left side of the screen is going to use 10 characters, leaving 30 for the "keyboard". Each "key" of the keyboard needs a "keycap", some sort of status, and there is a need for a spearator. The longest keyboard row, the top one, is "QWERTYUIOP", and *exaclty* 10 character wide, which is a sign of the gods (10+30=40)

The rest of the UX is pretty simple, an intro screen (with a "press space to start" message, really used to seed the random number, and a win and loose screen, with a recap of the game)

All in all, I am *extremly* happy at the resulting UX. I find the game as enjoyable as the web version, maybe even more focused. In my opinion, there is nothing to add and nothing to remove.

This UX would also work pretty well on a teletype, the only change would be that there is no need to redraw the whole thing when the user makes a mistake, as the paper trail is still here.

## The code

The Apple1 is a 1MHz 6502. This is *extremely* powerful. A 6502 takes on average 4 cycles to execute an instruction, so we are looking at a computer that can chew 250 000 instructions per seconds. It probably id completely overkill for the machine, but will come handy for us.

### The dev

The first thing is to set up a development environment. I used MAME to code, because it contains everything that I need: I can assemble some sort of memeory image, start MAME, execute the code, have a 6502 debugger and a memory view. There are some missing elements but it is more than enough to develop a simple game if you are carefukl enough.

[description on how to setup the dev env]

### The 6502

The 6502 is a very simple processor, with an instruction set that fits on a page of paper. It has some incredible strenghts that more than compensate for its weaknesses. It is done to do simple compact programs, and does that task fantastically well.

However, you have to understand the 6502 to code for it. Approaching it from the side of "thinking in C, translating in assembly" will not bode well.


There are a few things to understand with the 6502. They all make sense at some point.

There are only 3 registers. A, X and Y. This is all. And there are many instructions that seem to be randomly working on a register and not another. *There is no way of incrementing A*! *What is going on?*

The stack is 256 bytes. This seems small. How do you store your local variables in that stack? How to you access them? The answer is: you don't. The stack is not for lcoal variables, and the ways to address the stack are very limited.

The answer here is what is called the "zero page" (nicknamed "ZP"). The first 256 bytes of memory are very easily addressed by the 6502, and, for all purposes, should be considered as your set of registers.

Yes. Don't think that the 6502 have 3 registers, thing it has 256 generic ones and 3 specialised.

And what is extra cool with the apple 1 is that all of the 256 ZP registers are yours.

How do you passe data to your subroutines? You don't. You store it into the ZP and the subroutine fetches it from there. Is it a problem to implement recursion? Absolutely, but I will take 256 registers against a slightly more complex way to do recursion any time of the day. At the end, if you consider that conceptually all variables are global, you'll have a much easier time with the 6502.

But what if I need more than 256 bytes of data? Well, you store it where ever you want in memory, an put a pointer to it into the ZP. But understand that the pointer has to be in the ZP. If you start to put pointers in other parts of the memory, your 6502 will have a hard time accessing them.

This duality ZP/rest of the memory is what most people struggle with when starting in 6502. The ZP is not only a "nice faster area to store things", it is the key organisation for all the data structures.

Now, we can step into the awesome: the 6502 addressing modes. This is where everything will start to make sense, including the lack of increment on the A register :-)

I am not doing a primer on all the addressing modes of the 6502, just the ones that are used in the code. By understanding the next section, you should know enought to follow the design and the algorithm in Wozdle.

* Implicit addressing. This is named when the data to be used is implicit to the instructions. For instance, ``SEC`` means "Set Carry Flag". It implicitly changes the flags registers to set the carry flag to 1.

* Accumulator. This is when an instruction operates on the Accumulator registers. Normally the accumulator name is specified (``ASL A`` for "Arithmetic Shift Left A"), but it looks like my assembler let me write ``ASL``, blurring the academic difference betweem implicit and accumlator addressing (in this case, it is implicitly the accumulator)

* Immediate. This is how to specify actual data for an instruction. Those datas are 8 bits, and written with a '#'. So, ``MOV A,#65`` would move 65 into A. The assembler has different ways to specify numbers, so all of those are identical: ``MOV A,#65``, ``MOV A, #$41``, ``MOV A,#"A"``, ``MOV A,#%01000001``, and store the ascii code of the letter "A" into the accumulator.

* Zero Page. This means that the thing we operate on is a zero page location. ``MOV A,65`` will move the content of address 65 into the A register. The fact that this is the "default" behavior should tell you a lot on the importance of the ZP. Maybe you can't ``INC A``, but you can ``INC 65``, reading from the memory location 65, incrementing and writing back, *in a single instruction*, without hurting the current value of your A register. In *2 bytes and 5 cycles*. How awesome is that?

* Zero Page, X. This adds the X register before accessing the ZP location. ``INC 65,X`` would add X to 65, and increment the value in the resulting memory location. In *2 bytes and 6 cycles*.

* Absolute, X. This will use a 16 bits address and add the content of the X register to the address value before using it. It is used when the operand is larger than 255. ``INC 5000,X`` will add X to 5000 and increment the value in the resulting location. In 3 bytes. And 7 cycles. And if you ask me, this is insanely fast. The CPU have to fetch an *extra* byte (hence an additional cycle), and to perform a 16 bits addition, which should also add an extra cycle. However, the 6502 is a little-endian CPU, so the instruction is stored this way: ``FE 88 13`` ($1388 is 5000). When we perform an addition, we start by the right most digit, in order to handle the carry properly. It is the same for CPUs. Being little endian, the cpu gets the ``$88`` before the ``$13``, so it can start the calculation one cycle earlier, and finish in 7 cycles instead of 8. If you don't find this *awesome*, you're in the wrong blog.

This is used in wodle to address some of the static areas in memory, for instance ``LDA CHARROM,X``: access the Xth byte of the "character ROM" use din display the large texts.

* Indirect Indexed. This will use the zero page to get an address, and then add the Y register to it. It is written ``ADC (65),Y``. This will load the content of memory addresses 65 and 66, add Y to it, and add the content of the memory pointed to it to the accumulator. For instance, if addresses 65 and 66 contained $8813 and the Y register 42, this would add the content of address location 5042 to A. In 2 bytes. And 5 or 6 cycles.

There are limitations, because registers are hardwired for specific operations. For instance, there is no Indirect Indexed with X. But there is an Indexed Indirect that we don't use in Wozdle but you may want to read about. Also not all instructions support all modes with all the registers. For instance ZP,Y is only supported by LDX and STX (a case where you can't really use X), but Absolute,Y would work (but take 3 bytes, and don't have *exactly the same semantics regarding to address overflow*). So ``LDA 65,X`` is a two bytes instruction, while ``LDA 65,Y`` is a slower 3 bytes one (because it really is ``LDA $41,X`` vs ``LDA $0041,Y``)

So, if you understand that your registers are the zero page, X is used to index within the zero page (``LDA $41,X``), X or Y used to index over constant memory addresses (``LDA $1388,X`` or ``LDA $1388,Y``) and Y used to index over indirect memory (``LDA ($41),Y``), you are all set.


(unsure of the interest of this)
And the logic of not having an increment to the register A? Well, it is much more useful to have increment for X and Y, and their indexing capabilities mean they are the ones used for loop control. And when you look at the increment opcodes, you will notice that they don't set the carry flag. Is this an oversight? Absolutely not. Overflow of increment of indexes are seldom used, and keeping the carry flag intact enables to keep the arithmetic operations untouched.

ADC 41,X
INX
ADC 41,X

And if you need to increment something, you can directly ``INC $41`` if you want. At the end, if it is part of a computation, just add 1.

## Zero page variables in Wozdle

By examining the usage of the ZP, one can learn a lot about the organisation of a 6502 program.





-> random
-> large letters
-> Astuce du 'zzzzz' en dernier mot ajoute a la liste de mots.
