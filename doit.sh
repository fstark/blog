#!/bin/sh -e

npx @11ty/eleventy
rsync -avz --delete _site/ fred@www.stark.fr:/var/www/html

