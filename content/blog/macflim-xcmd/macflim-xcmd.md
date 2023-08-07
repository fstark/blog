---
title: Using Macflim with HyperCard
description: Annoncement of MacFlim XCMD
date: 2023-08-07
order: 1
tags:
  - macflim
  - mac
---

A couple of month ago, a macflim user reached to me to ask for a way to use macflim from within HyperCard.

## So, what is an HyperCard?

HyperCard is a program written by Bill Atkinson in the mid 80s, that would let end-users create multimedia programs (called "stacks"). It was revolutionary at the time, and for many still is. Unfortunately, it did not support network access, and was not an open format. If it had been, we may be browsing the world-wide-stack today...

uh?

{% image "img/hypercard-home.png", "Hypercard Home" %}


Hypercard was used to create all sort of interactive programs and games. A notable HyperCard software was the original version of the video game Myst.

## Why MacFlim?

While it was possible to create stack with Apple Quicktime, such technology was not available for low end macintoshes, and in general not B&W friendly. So, facing with the huge demand of a single user, it was a logical step for me to spend a hundred or so hours to implement this feature. If everything goers according to plan, I can bank to probably a couple of users at the end of 2024...

## MacFlim changes

Long story short, there have been quite a few changes in macflim to support hypercard:

### Play anywhere

First, the ability to play anywhere on the screen. As stacks are generally self-contained, and limited to 512x342, it is expected that anything that happen in the stack happens within the stack window. So there is an obvious need to get 512x342 flims to cover exactly the window, which can be almost anywher.

There is a limitation in MacFlim, that a flim has to be displayed at an even address, meaning an x coordinate multiple of 16. Strangely, the HyperCard window have the exact same constraint... Great mind thinks alike, Mt Atkinson!

### Don't clear the background

Another need is for having an option where macflim doesn't clear the whole screen to black. It isn't a hard thing to do, but just a little bit of added complexity...

### Downsize me

As card often have several elements, it seems logical that people would want to play flims smaller than 512x342. There are undocumented options to ``flimmaker`` to generate flims of different size (The different sizes were added to support Macintosh XL and Macintosh Portables in full screen. The stealth option has been used to test for a future project, playing flims [on some different hardware](https://oldcomputers.net/trs200.html))

### I have no mouse and I must stream

Now that we established that we want to play small flims in the current stack to keep the interactive feeling of HyperCard, there is the issue of the mouse cursor. MacFlim directly blits onto the screen, which creates artifacts with the cursor, so I remove the cursor before playing a flim.

There is now a new option to enable the mouse during playing. This has been implemented by re-coding the mouse display in a way that is compatible with flim playing, and maintains the illusion that everything is fine. But, in reality, the mac mouse is hidden, and replaced by a body snatcher.

### Don't start from black

As flims used to start on a black background, it was easy and logical to start films from a black image. It also gives a nice "buildup" that gives the feeling to the spectator that something sophisticated is going on.

However, in an interactive setting, if macflim is used to play some animations, it would be expected that the card shows the initial image, and the flim doesn't replace it with black when it starts.

So, there is now an option to specify that a flim will start by blitting the initial image on screen, and perfom playback from there. It creates a much better illusion.

### Cinemagraphs

Cinemagraps are little movie clips that are mostly static images with some animations, and have the property of seamless looping.

{% image "public/Models.gif", "A cinemagraph" %}


, the ability not to black out the whole screen, the ability to keep a mouse cursor on top of a playing flim, the ability to start a flim from an initial image (all flims used to start from black) and the ability to end up a flim on the exact image it started with.


```

```
