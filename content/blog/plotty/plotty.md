---
title: Midjourney on a 40 year old laptop
description: Drawing with the PB-700 internal plotter
date: 2023-08-08
order: 1
eleventyExcludeFromCollections: false
tags:
  - coding
  - pb-700
---

{% blogimage "img/lots-of-drawings.jpg", "The power of MidJourney on your trusty Casio PB-700" %}

## The Story

The Casio PB-700 is a fascinating little device from 1983. It has a sleek 120x32 pixels screen, and a whoping 4Kb of RAM, extensible to 16K, using 3 modules made of unobtainium.

It has a companion printer, the FA-10, which is actually a 4 colors pen-plotter, found in a few machines of the era (like in the [Sharp PC-1500](https://en.wikipedia.org/wiki/Sharp_PC-1500), in a smaller version, or [as an accessory to the TRS-80](https://colorcomputerarchive.com/repo/Documents/Manuals/Hardware/CGP-115%20(Tandy).pdf), or [some versions of the Sharp MZ-700](https://original.sharpmz.org/mz-700/useplot.htm))

Unfortunately, mine isn't fully working, and I only managed to get one color, so PloTTY is a monochrome program.

Anyway, this thing is the cutest, in particular with its incredibly tiny associated tape recorder, the CM-1 (under the paper in the intro picture).

It is a shame that there are no real impressive demos of what that machine and plotter can do, and I needed to find something fun, interesting, modern and useless to do.

However, I can't draw, but I can code. And coding is done to make computer do what we can't, right?

*What if I made a program where I type what I want to draw and the PB-700 just draws it?*

So, connecting the PB-700 to midjourney was the obvious idea. A linux box will do the midjourney request, some image manipulation and serve the result to the PB-700.

Simple.

## How do we communicate?

There are a few hurdles to overcome. For instance, there is there is no serial port, and no outside communication possible with the PB-700. *Or is it?*

{% blogimage "img/port-salut.jpg", "The only I/O ports of the PB-700/FA-10 combo" %}

Well there are cassette ports. So, *technically*, we can communicate. We'll just need our Linux box to emulate a tape recorder. Problem solved.

## High-level view of the process

* The PB-700 is connected to the Linux box with both the IN and OUT audio lines.

* The user type ``CHAIN`` on the PB-700 to load and execute the basic program on tape.

* The linux server send the initial BASIC program and wait for an answer from the PB-700.

* The PB-700 prompt the user for the image he wants, and writes its to the tape. It then executes another ``CHAIN``, waiting for the next BASIC program to execute.

* The linux server gets audio data as a wav file and use the ``casutil`` tools to extract the information sent.

* This information is transformed into a midjourney prompt, for generating an image.

* The resulting image is traced and a BASIC program that draws that image is generated and sent to the PB-700.

* The PB-700 gets the basic program and plot the image.

* As the BASIC programs ends up with another ``CHAIN`` command, the whole process is repeated

Easy, peasy.

Well, this is conceptually quite simple, but the implementation is riddled with unexpected roadblocks. Let's see them in order.

## On the PB-700 side

There no assembly language on the PB-700, everything needs to be done in basic, no way to access to the underlying hardware (in modern-speak, the PB-700 have *never been jailbreaked*). Any signal sent to the cassette port needs to be done from within BASIC.

Fortunately, our needs are pretty limited: we need to send a short amount of data, and get back a large amount.

Writing data to the cassette port can be done using the ``PUT`` basic command, that writes variable to the cassette. It is slow. First, because the cassette encoding is slow (300 bauds), but mostly because it writes a header, some metadata, another header, the data you want to write, and closes the communication with a trailer. Writing 20 bytes of data to the cassette takes easily 20 seconds.

As we need to read large amount of data, I'm gonna directly load a BASIC program that draws the result. Fortunately, the PB-700 BASIC have the ``CHAIN`` commands, that loads a program from tape and directly executes it. This is how our midjourney program will get a different program for each drawing. Or sets of programs, as a drawing may require more than one.

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

## On the linux side

### The ``plotty.sh`` server

On the linux box, we need some server software that just executes a succession of commands. Let's pretend that ``bash`` is perfect for that, and you can look at [the full server code here](https://github.com/fstark/PloTTY/blob/main/plotty.sh) to see the source code in its glory. The rest of this walktrhough is every steps of this server's implementation.

### Sending BASIC to the PB-700

[Casutil](http://www.mvcsys.de/doc/casioutil.html) is a set of utilities to manipulate sound files for Casio pocket calulator, including the PB-700. It also contains utilities to encode and decode basic programs.

So, the first order of business on the server is to send the basic program:

```sh
echo "-- Generating plotty.bas binary file"
casutil/linux/bas850 -b -t7 pb-700/plotty.bas plotty.bin >> log.txt
echo "-- Creating plotty.wav"
casutil/linux/wave850 -b plotty.bin plotty.wav >> log.txt
echo "-- Sending plotty.wav to PB-700"
play plotty.wav
```

This converts the BASIC source code into a tokenzed form suitable for the PB-700 (tokenized programs are smaller, so we gain a bit of time there), the generates a ``.wav`` file and plays it on the audio output. Hopefully the PB-700 is ready exacuting ``CHAIN`` and will load and execute plotty.bas.

The communication is a 300 baud one, with a header. The ``.bin`` is 224 bytes, and the total communication time is 12.712s

### Waiting for a response

The ``casutil`` commands work on 8 bits ``.wav`` files, so I need to use the ``record`` command to get the sound from the PB-700. Unfortunately, there is no way to make it stops when it gets a silent. Hence, I had to create my own command that waits for sound, and records until the line gets silent.

A small [python command ``listen.py``](https://github.com/fstark/PloTTY/blob/main/pb-700/listen.py) had to be created for that, using the python ``pyaudio``, ``audioop`` and ``wave`` modules. Thanks ChatGPT for writing half of the code there. Unfotunately, I wasn't able to make it output 8 bits wav, so a quick ``sox`` solved that issue:

```python
# Listen and decode answer
echo "-- Plotty.wav sent, waiting for reply"
python pb-700/listen.py
sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
casutil/linux/wav2raw -b out.wav out.bin
```

### Decoding the response

The PB-700 response is stored into a binary file. As there is no way to properly decode its content, a quick ``xxd`` was used to find the offset of the content and another python command ``extract-data.py`` was created to extract the user prompt.

```python
def extract_ascii_string(filename):
    with open(filename, 'rb') as file:
        # Set the starting offset to 0x29
        file.seek(0x29)

        # Read bytes until the next occurrence of 0x0d
        ascii_bytes = bytearray()
        byte = file.read(1)
        while byte and byte != b'\x0d':
            ascii_bytes.append(byte[0])
            byte = file.read(1)

        # Convert the extracted bytes into an ASCII string
        ascii_string = ascii_bytes.decode('ascii')

    return ascii_string

print(extract_ascii_string("out.bin"))
```

We loop until the data contains *something*, because sometimes audio interferences may get the ``listen.py`` command to record garbage.

### Storing the prompt

As there is no way to ask MidJourney for a single image, there are always 4 variations created. The user can specify which variation he is interested in, and is encoded in the format "PROMPT/VARIATION" (to have a single variable sent from the PB-700 and keep the binary decoding simple). Nothing that a quick ``sed`` can't fix:

```sh
VARIATION=`echo $PROMPT | sed -e 's/.*\/\([^\/\]*\)/\1/g'`
PROMPT=`echo $PROMPT | sed -e 's/\\/[0-9]*$//g'`
```

### Calling MidJourney

Now we "just" have to call the midjourney API to get an image for that prompt. This is the role of the ``midjourney/sendrequest.sh`` shell script.

It would be pretty simple if midjourney had an API. But it is 2023, and not even multi-billion valuation startups are able to implement simple JSON APIs.

```sh
#!/bin/bash

WINDOW_ID=`xdotool search --name "#general | Midjourney Discord"`

xdotool windowactivate $WINDOW_ID
xdotool mousemove --window $WINDOW_ID 400 1450
xdotool click 1
xdotool type --delay 10 "/imagine"
sleep 1
xdotool type --delay 10 " "
sleep 1
xdotool type --delay 10 "$1 black and white line art constant thickness simple children coloring book"
sleep 1
xdotool type "$(echo -ne '\r')"
```

{% blogimage "img/final.jpg", "Midjourney created this penguin on the pb-700" %}
