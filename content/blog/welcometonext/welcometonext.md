---
title: Welcome to NeXT
description: Beginers guide to the black Hardware
date: 2023-12-26
order: 1
eleventyExcludeFromCollections: false
tags:
  - next
---

## Background

The NeXTcube is my favorite machine. The reason for that is that I am an ex-NeXT developer, from around 1991 until 2005. I went through the original NeXT hardware, used NeXTstep on sparc a bit, moved to NeXTstep on Intel, then OPENSTEP, and even finished on the YellowBox, aka OPENSTEP ENTERPRISE (OpenStep on Windows NT). Now that I am collecting computers, I had to get a few cubes back, and play with them.

Doing that, I have to re-learn a few things, and doing so, I realised how hard it must be for people who didn't spent so many years with the machine. Documentaiton out there is either very superficial, incomplete, or just too specifialized.

My hope there is to create a document so anyone that have some black hardware is able to understand where it comes from, what it does, and hopefully use it a bit.

## The Basics

At the begining was the "NeXT Computer". It was a 25MHz 68030 cube box, with an internal optical disk. It was extremely slow, and fundamentally unusable.

It was then replaced by the "NeXTcube", with a 25MHz 68040 and an internal hard disk. This machine is the fundamental baseline of NeXT computers.

Both of those computers are identical magnesium cubes. You can swap components between them. Mostly. There are differences in power supplies.

The cube is a backplane, with space for 4 card, one being the motherboard.

The motherboard have to be placed in slot #0, the one just right to the power supply if you look at the cube from the back. No other slot will work without harware hacking.

If you want to distinguish a 68030 from a 68040, it is simple: look at the back, the 68040 have an RJ-45 ethernet connection.

There have been very few extension cards for the NeXT. NeXt made the NeXTdimension board, a 24 bits video card with video capture abilities. This card was rare but not unheard of, and there is some software for it, so having one in your cube is not too strange. See later section on the NeXTdimension.

In the non-NeXT cards, French IRCAM created the IRCAM board, containing a bunch of DSP for sound processing. There are very few existing, and they need special software.

As all computers from that period, there are two things you need to do:

* First, change the battery. Not that contrary to say, the Mac SE/30, the NeXT needs a battery to start.

* Second, you want to recap the board. Capacitors *will* leak and destroy the board.

## Variants

After the NeXTcube, NeXT create the NeXTstation. It is more or less identical to the cube, the only difference is the form factor. All cables are interchangeables between a cube and a NeXTstation.

Then, there was the NeXTstation Color.

Then, there wer "turbo" versions of each machine, (Cube Tubo, Station Turbo, Station Color Turbo). Unfortunately, the keyboard are incompatible, the turbos use a variation of Apple's ADB.

## Memory configurations

[talk about the memory configurations]

## The SoundBox

Steve Jobs being himself, he wanted a very simple computer, *with a single cable*. The way to set up a NeXT cube is as follow:

Power outlet -> cube -> monitor -> keyboard -> mouse

Also, to avoid having separate speakers and/or microphone, the monitor contains sound input and output.

The cube->monitor cable is a 3 meter cable that is hard to find. In many case, you'll find a station cable (60 cm) with a cube, which is barely usable.

That cable contains the video signal, but also power, sound output, sound input, keyboard and mouse. This "single cable" requirement forced NeXT to put sound and keyboard control into the monitor.

However, when designing the color NeXTstation, NeXT didn't have the financial mean to create their own monitor, so they had to use a standard color monitor. Hence they create a separate device to hold the sound input/output and the keyboard connections, called the "SoundBox".

At the end, a SoundBox is needed if you don't have the NeXT MegaPixel display. There are modern replacements.

## Powering up the NeXT

There is no power switch on the NeXT. To boot, you need to make sure you have a good battery inside, and that the keyboard is connected to the MegaPixel or SoundBox, and press the power key (in th middle of the keyboard). You should hear a "click" and the next should start.

If you have no keyboard/megapixel, a simple connection with a 4760 Ohm resistor between pin 6 and 19 of the DB-19 will boot the machine (this is helpful if you just want to check if the motherboard works). You'll have to unplug the machine to powert it down.

## The NeXT System Monitor

By default, a NeXT boots on ethernet, so, unless you have another NeXT set-up as a boot server, you'll get stuck on the "Network part" of the boot process.

So, until you are happy with the configuration of your NeXT, you want to boot to the monitor. Wait until the "Testing System" has finished displaying and press Left-Command + Numerical Keyboard Tilde. This will display the monitor.

Use 'b' to boot the NeXT, with the "root" device. ``bsd`` will be Boot SCSI Device, ``ben`` will be Boot Ethernet and ``bod`` will be Boot Optical Drive. You can add specifier, a kernel, and boot options. For instance:

``bsd(1,0)sd_mach -s`` means "Boot SCSI Device ID=1, LUN=0, using kernel file sd_mach, with the single user options". It is very rare to need to go that deep.

You should use the 'p' command to set the default boot parameters. You probably want to choose 'sd' as boot, and verbose booting (ie: drop to monitor). This way, when you power your NeXT, it will drop into the monitor, where you will press 'b' to boot it. When happy, remove the verbose booting and enjoy a full graphical boot.

If the ROM is password protected, removeing the battery should remove the password.

## Users

There are two users by default on a NeXT: the local ``root`` user, and the local ``me`` user. If the password for the ``me`` user is empty, the NeXT will autolog this user. The typical ``me`` password is ``myself``.

By default ``root`` has no password, so a fresh install will automatically log ``me`` in. You have to log out and log in back using ``root``.

If the NeXT has been used, it probably already have users, and you may not know the passwords. Do no panic, here is one way to bypass authentication on a NeXT.

Boot in the monitor. Enter ``bsd -s`` to boot single user. After the boot, you will be dropped into a terminal on the console. You then complete the boot as a background process, using ``sh /etc/rc&`` (passwords are served by ``netinfo``, it needs to be running for the following command to do the right thing). Use ``nu -m`` (nu==new user) to reset the root password. Reboot the machine using ``sync``, ``sync``, and ``reboot now``.

Tip: at the login screen, you can enter the user name "restart" to restart the NeXT, or "console" to get a console login.

Removing the me password. Use the ``nu -m`` command as root to remove the "me" password.

## Manual fsck

Sometimes, the NeXT may ask you to run ``fsck`` manually. In that case, boot "single users" (bsd -s), 


## Operating System Versions

* 0.8 : 0.8 is the first known version of the system. There is no official release as it was just installed on optical disks, and modified by users. There is a known version, but it is unclear how pristine it is.

* 0.9 : Same story as 0.8

* 1.0 : NeXTstep 1.0. First real version of the OS. Last version with the famous "Black Hole" as recycler bin.

* 1.0a : Last version of 1.0?

=> On NS10a-MO.raw

* 2.0 : NeXTstep 2.0 (March 1991) - support for Cubes

* 2.1 : A better 2.0

* 2.2 : Support for Turbo machines
  (note single CD for OS and dev, need to use floppy to install dev after install)

* 3.0 : NeXTstep 3.0 (Sep 1992)

* 3.1 : Support for x86 (May 1993)

* 3.2 : Support for HP-PA (Oct 1993)

* 3.3 : Support for sparc (Feb 1995)

* 3.3patch3 : Latest version with Y2K support (Nov 1999)

* 4.0, 4.1, 4.2, up to 4.2p3, (Mar 1999)

## Notes:

# Device names:

/dev/rod0a, /dev/rod0b : magneto-optical disk partitions


## Building a MO disk from a 0.8 image in Previous

# Create a 256MB MO file

``dd if=/dev/zero of=MO.raw bs=1048576 count=256``

Add it to Previous as a MO disk


## Machines for Luuk

NS2.0 => Oldest next step, most vintage
NS3.3 => Best next step
OS4.2 => Latest next step
