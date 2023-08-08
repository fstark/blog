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
bon, je me lance dans le se/30 « bruce » jailbar

{% blogimage "img/jailbar-mac.jpg", "Jailbar Macintosh" %}
de plus près

on voit qu’on a une ligne noire tout les huits pixels
un pb au niveau vram

l’interieur est incroyablement propre

le ventilo fait peu de bruit
la CM est propre, ps de son, donc condos foutus de toute facon

la video ram sont les deux chips en haut au milieu 

l’astuce du cable d’alim de PC pour connecter les cartes mere : ca sauve la vie

chaque puce de vram fait 4 bits. je checke les sorties
les huits ont un signal, donc les puces sont ok!

donc le signal sors de la vram mais arrive pas la ou il faut
je short les outputs pour trouver celui ou, meme shorte, l’image change pas… 
qd j’en short un, ca fait ca a l’image:

(une barre de pixels blancs en plus)
sauf pour celui-la:


Je vous met la doc du chip


donc SO1 sur UC6 est déconnecté
il doit aller sur UE8

et qd je verifie, la connection est ok pour les 7 autres data bits.
ergo: la trace est kaput qque part entre les deux.



ma conclusion de la trace manquante


my first bodge


laborieux (j’espere que c’est solide…)

And, bingo!


