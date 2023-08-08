---
title: Midjourney on a 40 year old laptop
description: Drawing with the PB-700 internal plotter
date: 2023-08-08
order: 1
eleventyExcludeFromCollections: true
tags:
  - coding
  - pb-700
---

{% blogimage "img/lots-of-drawings.jpg", "The power of MidJourney on your trusty Casio PB-700" %}

## The Story

The Casio PB-700 is a fascinating little device from 1983. It has a sleek 120x32 pixels screen, and a whoping 4Kb of RAM, extensible to 16, using 3 modules made of unobtainium.

It has a companion printer, the FA-10, which is actually a 4 colors pen-plotter, found in a few machines of the era (like in the [Sharp PC-1500](https://en.wikipedia.org/wiki/Sharp_PC-1500), in a smaller version, or [as an accessory to the TRS-80](https://colorcomputerarchive.com/repo/Documents/Manuals/Hardware/CGP-115%20(Tandy).pdf), or the [Sharp MZ-700](https://original.sharpmz.org/mz-700/useplot.htm))

Unfortunately, mine isn't fully working, and I only managed to get one color, so PloTTY is a monochrome program.

Anyway, this thing is the cutest, in particular with its incredibly tiny associated tape recorder, the CM-1 (under the paper in the intro picture).

It is a shame that there are no real impressive demos of what that machine can do, and I needed to find something fun, interesting, modern and useless to do.

However, I can't draw, but I can code. And coding is done to make computer do what we can't, right?

*What if I made a program where I type what I want to draw and the PB-700 just draws it?*

So, connecting the PB-700 to midjourney was the obvious idea. A linux box will do the midjourney request, some image manipulation and serve the result to the PB-700.

Simple.

## How do we communicate?

There are a few hurdles to overcome. For instance, there is there is no serial port, and no outside communication possible. *Or is it?*

{% blogimage "img/port-salut.jpg", "The only I/O ports of the PB-700/FA-10 combo" %}

Well there are cassette ports. So, *technically*, we can communicate. We'll just need our Linux box to emulate a tape recorder. Problem solved.

## High-level view of the process

The PB-700 is connected to the Linux box with both the IN and OUT audio lines.

The user type ``CHAIN`` on the PB-700 to load and execute the basic program on tape.



A second problem is that there no assembly language on the PB-700, everything needs to be done in basic, no way to access to the underlying hardware (in modern-speak, the PB-700 have *never been jailbreaked*). Any signal sent to the cassette port needs to be done from within BASIC.

Fortunately, our needs are pretty limited: we need to send a short amount of data, and get back a large amount.

Writing data to the cassette port can be done using the ``PUT`` basic command, that writes variable to the cassette. It is slow. First, because the cassette encoding is slow (300 bauds), but mostly because it writes a header, some metadata, another header, the data you want to write, and closes the communication with a trailer. Writing 20 bytes of data to the cassette takes easily 20 seconds.

As we need to read large amount of data, I'm gonna directly load a BASIC program that draws the result. Fortunately, the PB-700 BASIC have the ``CHAIN`` commands, that loads a program from tape and directly executes it. This is how our midjourney program will get a different program for each drawing.

Here is the full source code of midjourney for PB-700:

```basic
1 DIM F$(1)*79
2 CLS
3 PRINT "PloTTY by Fred Stark";
4 PRINT "- Midjouney Prompt -";
5 INPUT "> ",F$(1)
6 INPUT "Variation (1-4): ",V$
7 F$(1) = F$(1)+"/"+V$
8 PRINT "Sending..."
9 PUT F$(1)
10 PRINT "Waiting for image..."
11 CHAIN
```

On the linux box, we need some server software that just executes a succession of commands. Bash is perfect for that, and you can look at [the full server code here](https://github.com/fstark/PloTTY/blob/main/plotty.sh).


{% blogimage "img/final.jpg", "Midjourney created this penguin on the pb-700" %}
