#!/bin/sh -e

npx @11ty/eleventy
npx @11ty/eleventy --config=eleventy.vintage-color.config.js
npx @11ty/eleventy --config=eleventy.vintage-bw.config.js

rsync -avz --delete _site/ fred@www.stark.fr:/var/www/html
rsync -avz --delete _site_retro/ fred@www.stark.fr:/var/www/retro
rsync -avz --delete _site_retro_bw/ fred@www.stark.fr:/var/www/retro_bw

