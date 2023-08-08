---
title: Flims in HyperCard!
description: Annoncement of MacFlim XCMD
date: 2023-08-07
order: 1
draft: true
eleventyExcludeFromCollections: true
tags:
  - macflim
  - mac
---

A couple of months ago, a macflim user reached to me to ask for a way to use macflim from within HyperCard.

## So, what is an HyperCard?

[HyperCard](https://en.wikipedia.org/wiki/HyperCard) is a program written by Bill Atkinson in the mid 80s, that would let end-users create multimedia programs (called "stacks"). It was revolutionary at the time, and in many ways still is. Unfortunately, it did not support network access, and was not an open format. If it had been, we could be all browsing the world-wide-stack today...

{% image "img/hypercard-home.png", "Hypercard Home" %}

Hypercard was used to create all sort of interactive programs and games. A notable HyperCard software was the original version of the [video game Myst](https://en.wikipedia.org/wiki/Myst).

## Why MacFlim?

While it was possible to create stacks with Apple Quicktime, such technology was not available for low end macintoshes, and in general not Black & White friendly. So, facing with the huge demand of a single user, it was a logical step for me to spend a hundred or so hours to implement this feature. If everything goers according to plan, I can bank to probably a couple of users at the end of 2024...

## MacFlim changes

Long story short, there have been quite a few changes in macflim to support hypercard:

### Play anywhere on the screen

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

[Cinemagraphs](https://www.reddit.com/r/Cinemagraphs/) are little movie clips that are mostly static images with some animations, and have the property of seamless looping.

{% image "public/Models.gif", "A cinemagraph" %}

If we want to be able to continue playing from the begining, without any intervening "refresh", the flim needs to end pixel-precise with the same image it started on, because macflim only encodes differences between successive images. So, cinemagraphs are another reason why we can't start from black.

``flimmaker`` now has an option to append the first frame at the end of the flim until the encoding stabilize to a pixel-perfect representation.

## Work

### XCMD

An hypercard extension is named an XCMD. I created a new THINK C project that included some files from MacFlim to generate this extension.

### Player

The Macintosh player code needed some refactoring to access it from the MacFlim application and fro the HyperCard XCMD. Also a few deep changes were perfomed to get the new mous cursor, the "play anywhere", and the initial screen management. The complexity of the code of course increased slightly.

### Encoder

Weirdly, the most painful change in MacFlim one was getting a flim to end up as it started, because it implied refactoring the code of ``flimmaker`` to be able to apply the exact same transformations in two contextes (when getting images form the source vide, and when looping over the last image).

At the end, the code of both the player and the encoder is slightly better and more versatile. However, it now have to support more use cases, which, as always, makes maintenance more complex.

## Result

blabla what is the command blabla an image of some code blabla an animated git of a stack with a flim.

You can download the version 2.1 of MacFlim, with that simple HyperCard support.

## How to install

bla bla














