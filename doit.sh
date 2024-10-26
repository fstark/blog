#!/bin/sh -e

npm run build
rsync -avz --delete _site/ fred@www.stark.fr:/var/www/html

