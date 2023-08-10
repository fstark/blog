#!/bin/sh

rsync -avz --delete _site/ fred@www.stark.fr:/var/www/html

