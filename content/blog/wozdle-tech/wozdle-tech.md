---
title: Implementing Wozdle (Wozdle 3/3)
description: "Making Wordle for the Apple1 3/3 : Implementation"
date: 2023-10-22
order: 1
eleventyExcludeFromCollections: true
tags:
  - 6502
  - apple1
  - wozdle
  - coding
---

## The code

The Apple1 is a 1MHz 6502. This is *extremely* powerful. A 6502 takes on average 4 cycles to execute an instruction, so we are looking at a computer that can chew 250 000 instructions per seconds. It probably is completely overkill for the machine, but will come handy for us.

### The dev

The first thing is to set up a development environment. I used MAME to code, because it contains everything that I need: I can assemble some sort of memeory image, start MAME, execute the code, have a 6502 debugger and a memory view. There are some missing elements but it is more than enough to develop a simple game if you are carefull enough.

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

This is used in wozdle to address some of the static areas in memory, for instance ``LDA CHARROM,X``: access the Xth byte of the "character ROM" use din display the large texts.

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

(PICTURE OF THE ZERO PAGE IN THE EMULATOR)

Let's now dig into a few intereting pieces of code

### Printing a message

### Choosing a target word

At startup, we need to choose one of the 2309 possible answer words. However, there is no random generation baked anywhere in the Apple 1. Moder computers have on-cpu random number generators and a lot of randomness in the peripherals. This is called "sources of entropy", and you can generate random numbers by mixing all of them. Older computers didn't have that, but generally had a way to get the current time, which was used to seed a pseudo-random generator.

The Apple 1 has nothing of this. The most reliable source of entropy we have is the user, and this is why Wozdle asks the user to press the space bar at startup. After displaying this message, we make sure that there is no pending key:


```Assembly
        ;   Display user message
    JSR MSGINLINE
    .byte $d, $d, "     -- press space for new game -- ", 0

        ;   Eats any key already pressed
    LDA KBD           

        ;   Wait for space while incrementing random
LOOP1:
                        ;   Increment ANSINX to create entrpy
                        ;   based on player speed
    INC ANSINX
    BNE CONT
    INC ANSINX+1
CONT:
    LDA KBDCR           ;   Key pressed?
    BPL LOOP1           ;   No
    LDA KBD             ;   Key pressed
    AND #$7f            ;   Last 7 bits
    CMP #" "            ;   Space?
    BNE LOOP1           ;   Nope
```

First we use a ``LDA KBD`` to remove any potentially pressed key (or the user could have the algorithm always generate the same word by pressing ``SPACE`` during the display of the message).

```ANSINX``` is the index of the target answer in the list of answers. It is a number between 0 and 2308. We increment it as fast as we can while waiting for a key press.

The core of the loop is about 15 cycles and the CPU is 1MHz, so we count 66 666 times per seconds, a number very fitting for the Apple1 whose original retail price was $666.66.

We reach 2309 in around a 3 hundredth of a second, so the user have very little control on the exact number generated.

As the number is 16 bits, it wraps, so we get a fairly random number between 0 and 65536 (probably in the lower range, if the user pressed the key less than a second after the message). Of course, we could augment the randomness by asking for several keys, but there is a balance between technical perfection and usability.

We then add 2309 from the generated number until we overflow. This ensure we have a number between 0 and 2309, and is really quick (at most 28 iterations):

```
MODULO:
    CLC
MODULOOP:
    LDA ANSINX
    ADC #<ANSCOUNT
    STA ANSINX
    LDA ANSINX+1
    ADC #>ANSCOUNT
    STA ANSINX+1
    BCC MODULOOP
```

Note the way an multi-bytes addition is performed on the 6502: here we are adding the constant ANSCOUNT to the value stored in the Zero Page two bytes, starting at ANSINX. First, we use ``CLC`` to clear the carry flag, then we load the value at ANSINX, which is the lower byte of the number. We add (with carry) the lower byte of ANSCOUNT (# means immediate, aka constant, and < means lower byte). We then store the result back into ANSINX. This operation did set the carry flag if the result overflowed the byte. Using ADC on ANSINX+1 and the upper byte of ANSCOUNT, propagating the carry, will yield the right answer. If the higher byte did not overflow, we do a new iteration (BCC means Branch if Carry Clear).



-> large letters
-> Astuce du 'zzzzz' en dernier mot ajoute a la liste de mots.
