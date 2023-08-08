---
title: Reparing a Jailbar SE/30
description: Repair of an SE/30 suffering from jailbars
date: 2023-08-08
order: 1
draft: false
tags:
  - repair
  - mac
---

I came across an SE/30 for sale at a remarkably low price due to its non-functional state. Since I already own a few of these, I decided to purchase it and attempt to repair and restore it.

## External Examination

The machine boots up easily, with no beep, and the exhibits a typical flaw of aging SE/30, the jailbar pattern:

{% blogimage "img/jailbar-mac.jpg", "A typical jailbar Macintosh" %}

Looking closer, one can see that there is a vertical line missing every 8 pixels:

{% blogimage "img/single-bar-closeup.jpg", "Jailbar closeup" %}

That indicates an issue at the VRAM level. What is in the VRAM is not output properly to the video hardware.

Note that connecting a hard drive lets the machine boot to the Finder, so there isn't too much damage.

Time to open the machine!

## Inside examination

The interior of this mac is suprisingly clean.

{% blogimage "img/super-clean-mac.jpg", "An extremely clean mac" %}

Either it has seldom be used, or the previous owner cleaned-up the interior, maybe while looking up for the fault.

The fan is a little noisy, something that happens on those old machines. One can easily replace it with a modern alternative.

The motherboard looks clean.

{% blogimage "img/se30-motherboard.jpg", "The (fuzzy) motherboard" %}

Old Macintoshes from the 90s have leaky caps, that slowly cover the motherboards with a corrosive juice. Having no sound is a tell-tale indication that the caps have leaked (the sound caps are the 4 round ones the top-right -- replacing them generally bring the sound back).

So, while the motherboard looks clean, it is slowly getting corroded. Caps *needs* to be changed as soon as possible.

{% blogimage "img/vram-circuitry.jpg", "The video RAM circuitry" %}

The two 41264 on the top left (UC6 and UC7) are the video RAM chips, the vertial row in the middle are some support chips (buffers, etc). Keep a note of the C7 capacitor.

## Time to get the oscilloscope out!

It is difficult to work on a Mac powered on, due to the very short lenght of the cables. A little known trick is to use an ATX-connector between the analog and the logic board: 

{% blogimage "img/atx-connector-hack.jpg", "The life-saving ATX-connector hack" %}

Every VRAM chip is 4 bits. Let's check their outputs with an oscilloscope.

<a href="public/NECED001-12A-1.pdf" target="_blank">I used the RAM chip documentation to get the correct pins</a>

{% blogimage "img/normal-oscilloscope.jpg", "Completely normal oscilloscope signal" %}

The 8 outputs were similar to this, so the issue is after the VRAM (the signal correspond to the 0-1-0-1-0-1 pattern of the backgroud).

## Finding the right broken bit

Let's find which bit is ignored downstream.

We now short evey output bits, one after the other. A shorted bit is a zero bit, which, in the Macintosh world, is white (the Macintosh conceptually draws black text on white background). 

Eveytime I short a bit, there should be a vertical white line appearing on the screen, like below:

{% blogimage "img/forcing-bits.jpg", "Shorting a leg, to force a bit to 0" %}

{% blogimage "img/additional-white.jpg", "An additional vertical white line appears" %}

However, there is one bit that doesn't change when I short it:

{% blogimage "img/forcing-bits-2.jpg", "And we find the guily bit!" %}

{% blogimage "img/single-bar.jpg", "Still a single black line" %}

So, we now know exactly which pin is getting nowhere.

## Finding where the bit gets lost

Using the doc linked above and the schematics

{% blogimage "img/schematics.jpg", "The schematics of the video RAM part" %}

We can see that SO1 on UC6 is disconnected. It should have gone to UE8. Manually checking the trace, we find no connectivity. Testing the other 7 bits, we can find connectivity. 

The obvious conclusion is that the trace is broken between those two points:

{% blogimage "img/the-broken-trace.jpg", "The broken trace" %}

Making the connection "by hand" fixes the problem:

{% blogvideo "img/forcing.mp4", "Making the connection by hand" %}

## Fixing the issue

So, we need to manually re-create the connection between those two points, by adding a "bodge" wire.

{% blogimage "img/first-bodge.jpg", "My first bodge wire!" %}

This is my first bodge ever. No too displeased!

Just need to solder it in place.

{% blogimage "img/bodge-wire-soldered.jpg", "Soldered path between the two ICs" %}

Took a couple of time to solder, and I hope it'll stay for a long time...

## Checking

Just powering up the machine, and miracle:

{% blogimage "img/victory.jpg", "Victory!" %}

Wasn't that diffuclt, really.

## Conclusion

So, we had a broken trace between UC6 and UE8. Note how close UE8 is from the C7 capacitor. Those capacitors are know to be leaky. Also, there is no sound. It is obvious that the C7 capacitory has leaked, and the corrosive liquid have eaten into a trace, probably located under the UE8 chip.

If you love you Macs, you change their Caps!