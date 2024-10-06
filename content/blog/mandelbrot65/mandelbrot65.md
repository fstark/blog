---
title: 6502 assembly Mandelbrot for Apple1
description: Designing and coding a 6502 assemble version of Mandelbrot for the Apple1
date: 2024-10-03
order: 1
eleventyExcludeFromCollections: false
tags:
  - coding
  - Apple1
  - 6502
---

{% blogimage "img/mandelbrot65.jpg", "Mandelbrot explorer on the Apple1" %}

## Why?

My friend SiliconInsider developed a 32K ROM/RAM expansion for my favorite computer, the Apple I. We spent some time filling it with utilities and demos, but ended up with two different implementations of Mastermind/Codebreaker. Since we only needed one, we removed the duplicate, which left us with some free space. So, we thought, why not include a Mandelbrot rendering? We wanted to use a standard BASIC version, but unfortunately, it required AppleSoft BASIC (likely due to its need for floating-point arithmetic), which isn’t included in this ROM.

I searched for an assembly version but couldn’t find one, so I decided to write it myself. How hard could it be? (Spoiler: quite hard!)

## A link to the past

When I was a kid, I wrote a few very slow Mandelbrot programs on various machines, along with several sluggish versions of the Game of Life. I knew some people learned assembly specifically to speed these up, and I always wanted to do the same, but it seemed like an incredibly difficult task at the time. Now, over 40 years later, it begs the question: is my older self better than my younger self? Implementing this feels like a kind of rite of passage.

I have a budget of around 2K bytes of code and can use up to 8KB of memory. Let’s go!

## A bit on the Apple1

I have another blog post in the works where I plan to dive into the limitations of the Apple I and how they push you to be more creative. Long story short, you can only write a character at the end of the screen—no direct screen access. And you can only write a character every 16ms. Think of it like a teletype. This actually simplifies the design of the Mandelbrot: just compute the next character as fast as possible and display it. Ideally, in less than 16ms *(spoiler: we'll do it in 5.5ms)*.

Pseudo code of Mandelbrot for apple1:

```c
/*
    x0, y0, dx and dy contains the coordinates
    of the top left and the horizontal and vertical steps,
    in Mandelbrot space (respectively -2.093,-1.125 and 0.073,0.094)
*/
cy = y0;
for (int line=0;line!=24;line++)
{
    cx = x0;
    for (int column=0;column!=40;column++)
        if (line!=23 and column!=39) // Don't write the last character to avoid scrolling
        {
            count = compute_iterations(cx,cy);
            character = character_from_iteration(count);
            display(character);
            cx += dx;
        }
    cy += dy;
}
```

This is as simple as i gets, and the core loop is basically this. The devil is in the ``compute_iterations()``.

## A bit of Mandelbrot

The Mandelbrot calculation is both very complex and very simple. I mean, it’s quite simple, but it uses complex numbers.

To compute the Mandelbrot set for the coordinate ``c``, you start with ``z = 0`` and perform the following operation in a loop: ``z = z^2 + c``. If the value "diverges," the point is outside the Mandelbrot set. If it doesn't diverge, the point is within the Mandelbrot set.

{% blogimage "img/stupid-meme.jpg", "Probably not the best illustration" %}

Determining if a series diverges in general is not trivial. However, in the case of the Mandelbrot set, if z becomes "large enough" (specifically, if its absolute value exceeds 2), you can conclude that the series diverge.

This means that the Mandelbrot set is black and white. A point is either "inside it", or "outside it".

{% blogimage "img/mandel-bw.jpg", "The real set is a bit boring" %}

To get a nicer image, we display how many iteration counts it took to detect the divergence. Checking that the value does not "diverge" is much harder in theory, but pretty simple in practice: if we didn't "diverge" after a fixed number of iterations, we consider the point to be **in** the Mandelbrot set.

Saying "``z=z^2+c``", with ``z`` and ``c`` being complex numbers may not mean much to people not familiar with such concepts. But it is much simpler than it sounds. A complex number have two parts, a "real" one and an "imaginary" one. Think of them as the "real" one being on the horizontal axis, and the "imaginary" one being on the vertical axis. The numbers we know and love all lie on the horizontal axis. There is an imaginary number ``i`` that is just like ``1``, but on the vertical axis. It has the fascinating property that ``i^2=-1``. Armed with that, we can do the Mandelbrot calculation:

The number ``z`` have a real part, ``zx`` and an imaginary part, ``zy``. We write this "``z = zx+i.zy``".
The number ``c`` is the same, with ``cx`` and ``cy``. We write this "``c = cx+i.cy``".

We can now rewrite the Mandlbrot iteration forumla as "``znext = z^2 + c``" (the next value of ``z`` is the square of the current value of ``z`` plus ``c``).

``znextx + iznexty = (zx + izy)^2 + cx + i.cy``

Using the classic identifiy "``(a + b)^2 = a^2 + 2ab + b^2``", we get:

``znextx + iznexty = zx^2 + 2i.zx.zy + (i.zy)^2 + cx + i.cy``

Knowing that ``i^2 = -1``, we get:

``znextx+iznexty = zx^2 + 2i.zx.zy - zy^2 + cx+i.cy``

Putting all the ``i`` together:

``znextx + iznexty = (zx^2 - zy^2 + cx) + i.(2zx.zy + cy)``

We then get the value of ``znextx`` and ``znexty``:

``znextx = zx^2 - zy^2 + cx``
``znexty = 2zx.zy + cy``  (please take a note at the ``2`` in ``2zx.zy``, it will come back to save us later)

That's great. We just have to do that in 6502. Slight issue: we only deal with 8 bits values, and we don't have a multiplication...

## A bit of 6502

The 6502 is an 8 bits CPU. A great one. If you haven't done 6502 assembly, I do recommend it. It is very elegant, and not as difficult as it seems, unless you want to hack every cycles out of your code.

However, we don't have a multiplication operation. Implementing one will be quite slow and limited.

Say we want to multiply 10011101 (157) by 00101110 (46). We would do exactly like in base 10, but with 0s and 1s:

```
          10011101 ( 157)
*         00101110 (  46)
          --------
          00000000
        1 0011101
       10 011101
      100 11101
     0000 0000
    10011 101
   000000 00
  0000000 0
  ------- --------
= 0011100 00110110 (7222)
```

We need to do 16 bits additions, one for every bit set in the first number, and quite a few bits shifting. It will be quite slow, and result will be 16 bits. This precision may not be sufficient for our needs, but the principle would work.

{% blogimage "img/multiplication-is-adding.jpg", "We will not use Woody's method" %}

Is there a better way? Well, we could pre-compute a multiplication table for 8bits, but that would be 64K of data, the full address space of the 6502. Maybe a 4bitsx4bits table? That would be more manageable, and we would do a pure hexadecimal multipliation:

```
     9D ( 157)
     2E (  46)
     --
+  8 96
+ 13 A
  -- --
  1C 36
```

To multiply two 8 bits number, we have to do 4 multiplications, a bunch of additions, and some 4 bits shifts.

To make matters worse, we are going to need to multiply numbers larger than 8 bits...

## Another bit of math (to square things up)

Earlier, we used the ``( a +b)^2`` identity. But there is the little sister, the ``(a - b)^2`` identity.

``(a - b)^2 = a^2 - 2ab + b^2``

This is equivalent to:

``2ab = a^2 - b^2 - (a - b)^2``

This is just extraordinary: we can compute ``2ab`` *with only squaring operations*!

{% blogimage "img/mind-blown.gif", "It is insane that this works." %}

We can pre-compute a table of squares and use it for instant results!
What is even more fantastic, is that this computes ``*2* ab``, and we need to compute ``2zx.zy``. Life is beautiful again.

We now have our full plan. Instead of computing:

``znextx = zx^2-zy^2+cx``
``znexty = 2zx.zy+cy``

we will compute:

``znextx = zx^2-zy^2+cx``
``znexty = zx^2+zy^2-(zx-zy)^2+cy``

## A bit of bit counting for our numbers

Before getting to the squaring operation, we need to decide on the representation of our numbers.

As said before, Mandelbrot iterations "diverges" when they get "too big". It turns out that numbers between -4 and 4 are good enough. However, we may have internal operations that go over that (think about 3+3-3, which should be 3 but need an intermediary value of 6). Numbers between -8 and +8 should work in *most* of the cases.

For my sanity I decided to implement fixed points numbers. In decimal, it is like if we decided to store 314 instead of 3.14 and have all of our numbers multiplied by 100.

xxx insert picture of mecanical calculator xxx

Now, the question is how much *precision* do we need? As much as possible, but to answer that question, let's first solve our squaring implementation. We need the square of every number. Well, of every positive number. There is only 8KB of RAM available, so let's use 4K for the square table. Each entry takes two bytes. That 2048 entries. We can have only 2048 positive mnumbers(*). That's 11 bits. We need 3 bits for the integer value (0 to 7), so we have 8 bits left for the precision. We'll "multiply" all numbers by 256.

## A bit of 6502 bit twiddling

It took me a while and a full rewrite to implement numbers properly. At start, I wanted to go to a sign+magnitude representation, where the number is stored positive, and a single bit tells us if the number is positivie or negative. I assumed it would help me doing things like negating numbers or taking absolute values. I neglected the fact that it makes additions and substractions nightmares, because *this is not how the 6502 works*.

The 6502 is a 2-complement machine (like basically everything else). This means that, for instance, that ``-2`` is ``254``. This may not seem natural, but is in fact something we use all the time, for instance, when counting minutes: 10 minutes before the hour is 50 minutes after. In French, we'd say "I'll meet you at minus 20" or "I'll mee you at 40" interchangeably. The 6502 does the same.

The numbers in Mandelbrot65 are 4.8 fixed point numbers. This means the can represent numbers between -8 and +8-precision, with precision being 1/256. They are stored shifted left by 1, and are stored in 16 bits, so they are extended to 7 bits for the integer part. At the end, numbers look like this:

``iiii iiif ffff fff0``

I don't really care about the first 3 'i' (they are 0 for positive, and 1 for negative). There is an opportunity for more precision, there.

For the square table, I will use the memory between ``0x1000`` (``0001 0000 0000 0000``) and ``0x1fff`` (``0001 1111 1111 1111``).

So a positive number like ``0000 iiif ffff fff0`` will have its square stored at ``0001 iiif ffff fff0`` (least significant byte) and ``0001 iiif ffff fff1`` (most significant byte)

Here is the SQUARE assembly function:

```asm6502
;-----------------------------------------------------------------------------
; Input:
;   A,X: number
; Output
;   A,X: AX^2
;   Carry if overflow
;-----------------------------------------------------------------------------
SQUARE:
.(
	JSR ISNUMBER		; Not a number or overflow ?
	BCS DONE
	JSR ABS				; Absolute value
	ORA #$10			; Set square table address bit (0x1000)
	STX PTR
	STA PTR+1
	LDY #0
	LDA (PTR),Y			; Get LSB of the square
	TAX
	INY
	LDA (PTR),Y			; Get MSB of the square
DONE:
	RTS
.)
```

The code is massively straightforward.

In general, numbers are kept in the A and X registers (A for MSB, X for LSB). If the number is invalid, we return with the Carry flag set.

Else, we compute the absolute value, set the 12th bit to 1 (so it looks like an address between 0x1000 and 0x1ffe), and use that to get the result from the square table.

How is the ABS computed?

Trivially:

```asm6502
;-----------------------------------------------------------------------------
; Input:
;   A,X: valid number
; Output
;   A,X: abs(AX)
;-----------------------------------------------------------------------------
ABS:
.(
	ORA #0
	BMI NEG					; Neg if negative
DONE:
	RTS
.)

;-----------------------------------------------------------------------------
; Input:
;   A,X: valid number
; Output
;   A,X: -AX
;-----------------------------------------------------------------------------
NEG:
.(
	PHA
	TXA
	EOR #$FF				; Complement of X
	CLC
	ADC #1					; +1
	TAX
	PLA
	EOR #$FF				; Complement of A
	ADC #0
	RTS
.)
```

ABS test the bit 7 of the MSB, if sets, it negates the number.

Negation is done by two complement (inverting the bits, and adding 1).

At the end, the Mandelbrot calculation, performed in the routine ``MANDEL1`` looks like:

```asm6502
	; STUFF

	; zy = 2zx.zy + y
	; zy = zx2-(zx-zy)^2+zy2+y
	; zy = -(-zy+zx)^2+zx2+zy2+y

	; -zy
	MLOADAX(ZY)
	JSR NEG

	; -zy+zx
	CLC
	PHA
	TXA
	ADC ZX
	TAX
	PLA
	ADC ZX+1

	; (-zy+zx)^2
	JSR SQUARE
	BCS DONE

	; -(-zy+zx)^2
	JSR NEG

	; -(-zy+zx)^2+zx2
	CLC
	PHA
	TXA
	ADC ZX2
	TAX
	PLA
	ADC ZX2+1

	; MORE STUFF
```

(``MLOADAX`` is a macro that loads a number in the A and X registers)

Absolutely straightforward.

## The overall code structure

The code is really straightford and can be looked at in the [github repository](https://github.com/fstark/mandelbrot65)

The assembly code is fully documented [and can be accessed here](https://github.com/fstark/mandelbrot65/blob/main/mandelbrot65.asm).

``DRAWSET`` displays the Mandelbrot set on the screen. While long, it is quite straightforward. It calls ``ITER`` to compute and store in the ZP page variable ``IT`` the iteration count at the current position (stored unsurprisingly in the zero page variables ``X`` and ``Y``)

The function ``CHARFROMIT`` is called and gets a character to display on screen, depending on the iteration. It uses the PALLETE table to get the character to display. At typicial palette looks like:

``..,''~~==+++:::;;;[[[//<<***??&&OO00XX# ``

Characters at the beginning are close to black, and the more iterations it took to diverge, the lighter the character. The center of the Mandelbrot set is black however, increasing the contrast of the border.

The maximum number of iterations depends on the zoom level, are stored at the address ``MAXITER`` and varies between 19 and 39.

## Automatic zoom

To make the display more enjoyable, we auto-zoom 4 seconds after having displayed the image. The are 5 zoom levels, each roughly twice as zoomed as the previous one.

The Mandelbrot set is much more interesting close to the border of the set.
To determine where to zoom, there are iteration trigger values. For instance, any point of the original zoom where it took between 15 and 19 iterations to diverge may be choosen as the center of the next zoom. Those zoom-level dependant values are stored in the ``ZOOMTRIGGERMIN`` and ``ZOOMTRIGGERMAX`` tables.

Randomly choosing a point is an interesting challenge in itself. We use a pseudo-random generator, that is seeded by the wait at the begining, when the user is asked to ``PRESS ANY KEY``.

{% blogimage "img/press-any-key.jpg", "'Please Generate Some Entropy' would have been more correct, but slightly more confising for the user..." %}

Picking a random value is pretty simple. We don't need a lot of entropy, so 8 bits are good enough. Rotating the seed left and XOR'ing it with ``00011101`` if the high bit was ``1`` is enough to get an acceptable random value (lifted from [the Commodore 64](https://www.codebase64.org/doku.php?id=base:small_fast_8-bit_prng)). Any other algorithm would work equally well, or better.


```asm6502
;----------------------------------
; Return a random number in A
; Input:
;   ZP:SEED seed
; Output:
;   A random number
;   ZP:SEED updated
;----------------------------------
RANDOM:
.(
	LDA SEED
	ASL
	BCC SKIP
	EOR #$1d
SKIP:
	STA SEED
	RTS
.)
```

To pick a random location that fits a specific criteria with uniform probability without using extra storage in a single pass, I use the [Reservoir Sampling Algorithm](https://en.wikipedia.org/wiki/Reservoir_sampling), which is surprinsingly simple. The idea is to keep a "reservoir" of one element, and replace it with the new element with a probability of 1/n, where n is the number of elements seen so far. The implementation is as follow:

```asm6502
;----------------------------------
; Sets Z flag 1/A times
; Input:
;   A: FREQ
; Output:
;   Z: 1/FREQ times
;----------------------------------
RNDCHOICE:
.(
	TAX				; X = FREQ
	JSR RANDOM
	TAY				; Y = RANDOM
	TXA				; A = FREQ
LOOP:
	DEX				; Decrement FREQ
	BNE SKIP		; Modulo FREQ
	TAX				; (we reset to FREQ if we are at 0)
SKIP:
	DEY				; Decrement random
	BNE LOOP		; Loop count = orginal random number
	TXA				; 1/FREQ times, we will end up with 1 in X
	CMP #1
DONE:
	RTS
.)
```

Yes, it is a loop, it is costly, and could also be done by substracting FREQ from the random number until it is negative, but keep in mind that it is only used when we have a zoom candidate. There aren't than many of them.
