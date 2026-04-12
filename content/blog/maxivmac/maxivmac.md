---
title: Maxivmac -- An AI adventure in the world of vintage emulators
description: How I stopped worrying and learned to love the bomb
date: 2026-03-30
order: 1
eleventyExcludeFromCollections: false
tags:
  - macintosh
  - coding
  - ai
---

## My life with AI

As soon as OpenAI released the first version of ChatGPT, I've been fascinated by the possibility. The fact that I could write something like ``// This function returns the square of its argument`` and have it write the proper function was absolutely wild. The notion that this thing was just intuiting algorithms without any shame was such a source of joy. Instead of discovering the algorithmic truth of math, I could grab it from the collective knowledge.

// image showing "// return woman salary based on man salary

Caption: The fact that it returned the salary in a float is not even the most disgusting thing about the way this AI was trained.

I played a lot with this, it was my personal "do a barrel roll" (with link to google)

I knew the future of coding was changing, and I had to change with it.

So, as soon as there was an integration into vscode (as completion), I switched my coding habits to ease the completion engine. Forced myself to try to write comments instead of functions, to get the best out of the AI help. Was I more efficient? Probably not, but not having to remember all the details did free up my mind while coding, and arguably allwed me to write slightly better code. A bit of online chatgpt for analysis, a bit of chatgpt completion

The the Agent mode was released, and, with it, vibe coding in all its glory. I did a few vibe coded projects (I define vibe coded when my *only* interaction with the code is via the agent). It generated the crappiest most spaggethi code of all time, but in many cases actaully worked. Somewhat. Until I asked for a change, which broke some other part. Adding unit test vould help, it the same sense that jumping from a higher building can help someone stay alive longer. The AI sometimes hallucinated the test results without running them ("all test passes!" ), changed them to match the current state ("removed non-passing tests"), or simply ignored them ("3 test fails, that not a lot"). The AI found itself in conceptual minimas, oscillating between two shitty solutions, balancing from one to another while adding hundred of lines of code at each tentative to fix things.

[maybe a ai-play on the "do not believe its lies?" images]

The only way to finish a project was dig into the code, understand it and precisely guide the AI for the fix. Which is not that different from how I used to code, except that I had to fix more bugs.

That was the status quo, until Claude Sonnet 4.5. At this point, I felt the AI "surface" was good enough that you can drive it in local minimas that weren't a disaster. I start to use it more and more, to perform code updates. I refreshed macflim with it, and the result is undoubtely better than what I could accomplish in the same amount of time. The AI was a helpful companion, not particularly bright, and with that strange memory loss condition.

[image from memento]

Then came Opus 4.6.

[find the right image]

If Sonnet 4.5 was my coding janitor, Opus 4.6 is my junior architect. It actually pretend to understand codebases in a way that makes practically no difference from what an architect would do. It does what you ask it to do. It never complains. It has no ego. It will enthusastically dig into hundred of thousands of lines of code using dozen of parallele greps to understand something that would have made any human resign.

It is freaking awesome.

In my line of work, I manage people that manage people that manage people that manage teams working on large legacy heavily used applications. Say between 1 and 15 millions of lines of code each. Since the advent of chatgpt, I knew it would come a day where AI could help the modernization of those monoliths. Opus 4.6 is *almost* it (despite what consultants tells you, not you cannot migrate an app from a tech to another in a single command. Yet).

So, I needed to train myself on a code moderniation example on my spare time. I chose minivmac.

[something about "I choose you". Maybe uncle Sam, or seomthing else]

## The Mini vMac emulator

Mini vMac has a tremedous qualities. It exists. Its scope is small. It is multi-platform. It works.

I think that is about it.

Compiling it is a nightmare.

[insert meme]

I forked it a few years ago to add the capacity to read hfs partitions in addition to file images. It was hell.

I wanted to get "into it" to be able to contribute back. I wasn't even able to make sense of it.

The source code is a very early 1990:

```
src % ls
ACTVCODE.h	GLOBGLUE.c	KBRDEMDV.h	OSGLUXWN.c	SCRNTRNS.h	STRCNPOL.h
ADBEMDEV.c	GLOBGLUE.h	M68KITAB.c	PBUFSTDC.h	SCSIEMDV.c	STRCNPTB.h
ADBEMDEV.h	HPMCHACK.h	M68KITAB.h	PMUEMDEV.c	SCSIEMDV.h	STRCNSPA.h
ADBSHARE.h	ICONAPPM.r	MINEM68K.c	PMUEMDEV.h	SGLUALSA.h	STRCNSRL.h
ALTKEYSM.h	ICONAPPO.icns	MINEM68K.h	PROGMAIN.c	SGLUDDSP.h	SYSDEPNS.h
ASCEMDEV.c	ICONAPPW.ico	MOUSEMDV.c	PROGMAIN.h	SNDEMDEV.c	VIA2EMDV.c
ASCEMDEV.h	ICONDSKM.r	MOUSEMDV.h	ROMEMDEV.c	SNDEMDEV.h	VIA2EMDV.h
BPFILTER.h	ICONDSKO.icns	MYOSGLUE.h	ROMEMDEV.h	SONYEMDV.c	VIAEMDEV.c
COMOSGLU.h	ICONDSKW.ico	OSGLUCCO.m	RTCEMDEV.c	SONYEMDV.h	VIAEMDEV.h
CONTROLM.h	ICONROMM.r	OSGLUGTK.c	RTCEMDEV.h	STRCNCAT.h	VIDEMDEV.c
DATE2SEC.h	ICONROMO.icns	OSGLUMAC.c	SCCEMDEV.c	STRCNCZE.h	VIDEMDEV.h
DISAM68K.c	ICONROMW.ico	OSGLUNDS.c	SCCEMDEV.h	STRCNDUT.h	main.r
DISAM68K.h	INTLCHAR.h	OSGLUOSX.c	SCRNEMDV.c	STRCNENG.h
ENDIANAC.h	IWMEMDEV.c	OSGLUSD2.c	SCRNEMDV.h	STRCNFRE.h
FPCPEMDV.h	IWMEMDEV.h	OSGLUSDL.c	SCRNHACK.h	STRCNGER.h
FPMATHEM.h	KBRDEMDV.c	OSGLUWIN.c	SCRNMAPR.h	STRCNITA.h
```

It is not too big.

```
src % cloc .                  
      86 text files.
      86 unique files.                              
       6 files ignored.

github.com/AlDanial/cloc v 2.06  T=0.26 s (333.9 files/s, 336554.2 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
C                               29           7642           4535          48497
C/C++ Header                    52           2819           2912          14660
Objective-C                      1            788            266           3939
R                                4             35             32            564
-------------------------------------------------------------------------------
SUM:                            86          11284           7745          67660
-------------------------------------------------------------------------------
```

So, what could be wrong?

```
src % grep '^#' * | wc -l
   11284
```

Sure, this is unfair, I am counting all the ``#include``:

```
src % grep '^#' * | grep -v include | wc -l
   10959
```

On 67660 lines of code. *16%* are pre-processor directives. The code looks like:

```
insert code example
```

The build system is byzantine. Let me explain it to you.

First, you compile a C-based setup tool.

Second, using this tool, you specify what emulator you want. You can specify everything, from the model, the screen resolution, the available memory and many many many other options.

*All those are compile-time #defines*

Running this setup tool withh generate a shell script.

You then run the setup tool. It will generate a bunch of include files that themselves contains a bunch of ``#defines`` and a ``Makefile``.

You then can ``make`` the emulator.

The resulting binary will *only* do what you specified. Any option you want to change, from resolution, to memory, to speed, to startup fullscreen or anything, you have to fully recompile the emulator.

On the flip side, you can build a version for the Nintendo DS, or for a m68k macintosh itself.

For all matter of purposes, this code is dead. I tried to hack on it and abandonned after a few hours.

[at some point the idiocracy image with the pile of garbage]

## Claude to the rescue

With the release of Opus 4.6, it seems to be the time where it makes sense to see if fred+claude can suceed where fred alone failed.

It is a very important milestone to me, because it means that me+ai can do more than what I could do alone. I consider coding as an art, and I've been striving for 43 years to be the best possible at it. This is extremely significant for me. 

Here are the things I did:

First, I knew what my objectives were, and what good would looks like:

* Single binary for all emulated mac
* All features built-in
* Single portable front end (minivmac has different front-ends, but they are all looking the same because the UI is custom-baked into the emulator itself)
* C++ (not a lot of C++, but some for "a better C approach")
* Rely on the fact that comppilers actually generate good code now
* Replace code by standard when possible

I aksed Claude to create an overall plan, and it came with the following steps:

### Passing under CMake

"Replace the 3-stage pipeline (compile `setup_t` → generate `setup.sh` → generate config headers + Xcode project) with a single CMakeLists.txt."

### Type System & Macro Cleanup

"Replace the custom type system and visibility macros with standard C++."

### File Rename & Directory Structure

"Make the source tree navigable"

### Device Interface & Machine Object

"The architectural pivot that enables everything downstream"

### Multi-Model Support & Runtime Configuration

"A single binary now emulates any supported Mac model via `--model` flag."

### Platform Consolidation

"Reduced to a single SDL backend"

### Testing Infrastructure

"Regressions are caught automatically. Contributors can verify changes without manual boot-testing"

### (then some new features built on top)

That is a solid plan with two major flaws:

Testing infrastructure must be the first thing. It has to. If there is a single lesson here is that the testing infra is the most valuable investment. Sure, writing testing code is boring, *but Claude will do it for you*.

The second flaw is slightly less evident to see. After all that, the code is still almost as bad as it started, there is no way one can build new features. We'll look a bit on why the code is crap later.

## Testing





Code written by a drunk yoda:

```
if (0 != (LeftMask
    & (((((uibr)1) << (1 << vMacScreenDepth)) - 1)
        << ((j ^ FlipCheckBits) << vMacScreenDepth))))
```


```
#if vMacScreenDepth > ln2uiblockbitsn
			j0h =  (LeftMin >> (vMacScreenDepth - ln2uiblockbitsn));
#elif ln2uiblockbitsn > vMacScreenDepth
			for (j = 0; j < (1 << (ln2uiblockbitsn - vMacScreenDepth));
				++j)
			{
				if (0 != (LeftMask
					& (((((uibr)1) << (1 << vMacScreenDepth)) - 1)
						<< ((j ^ FlipCheckBits) << vMacScreenDepth))))
				{
					goto Label_1c;
				}
			}
Label_1c:
			j0h =  (LeftMin << (ln2uiblockbitsn - vMacScreenDepth)) + j;
#else
			j0h =  LeftMin;
#endif
```

```
#if ! WantAbnormalReports
#define ReportAbnormalID(id, s)
#else
#if dbglog_HAVE
#define ReportAbnormalID DoReportAbnormalID
#else
#define ReportAbnormalID(id, s) DoReportAbnormalID(id)
#endif
EXPORTPROC DoReportAbnormalID(ui4r id
#if dbglog_HAVE
	, char *s
#endif
	);
#endif /* WantAbnormalReports */
```

```c
#if ForceFlagsEval
LOCALPROC NeedDefaultLazyAllFlags(void) { ... }
#else
#define NeedDefaultLazyAllFlags NeedDefaultLazyAllFlags0
#endif
```
