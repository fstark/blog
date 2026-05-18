#!/bin/sh
# make_zooms.sh — Generate zoom crops and 4x pixel-scaled versions for the blog post.
#
# Source images must already exist in ../img/:
#   birds-320.png  (320x200 MO5-resolution original)
#   birds_naive1.png … birds_naive5.png  (converted variants)
#
# Crops a 48x60 region at offset (200,78) from each image,
# then scales each crop 4x with nearest-neighbour (no blur).

set -e
cd "$(dirname "$0")/../img"

rm -f montag

# Resize the source images
magick lena.png -resize 320x200^ -gravity center -extent 320x200 lena-320.png
magick birds.jpg -resize 320x200^ -gravity center -extent 320x200 birds-320.png
magick minitel.jpg -resize 320x200^ -gravity center -extent 320x200 minitel-320.png
magick beach.jpg -resize 320x200^ -gravity center -extent 320x200 beach-320.png
magick pink.jpg -resize 320x200^ -gravity center -extent 320x200 pink-320.png

# Creates all the imaging pipeline

PNG2MO5=/Users/fred/Development/png2mo5/png2mo5/png2mo5

${PNG2MO5} lena-320.png -o lena_mo5.png
${PNG2MO5} pink-320.png -o pink_mo5.png
${PNG2MO5} minitel-320.png -o minitel_mo5.png
${PNG2MO5} beach-320.png -o beach_mo5.png
${PNG2MO5} birds-320.png -o birds_mo5.png

# Generate the birds
source ../../../../venv/bin/activate
cp birds-320.png birds_naive0.png
python ../tools/naive1.py birds.png birds_naive1.png
python ../tools/naive2.py birds.png birds_naive2.png
python ../tools/naive3.py birds.png birds_naive3.png
python ../tools/naive4.py birds.png birds_naive4.png

for i in 0 1 2 3 4 5; do
    src="birds_naive${i}.png"
    magick "$src" -crop 48x60+200+78 +repage "birds_zoom${i}.png"
    magick "birds_zoom${i}.png" -filter point -resize 400% "birds_zoom${i}_large.png"
    echo "birds_zoom${i}.png + birds_zoom${i}_large.png"
done

for i in 0 1 2 3 4 5; do
    src="birds_naive${i}.png"
    magick "$src" -crop 48x60+140+140 +repage "birds_zoom_alt${i}.png"
    magick "birds_zoom_alt${i}.png" -filter point -resize 400% "birds_zoom_alt${i}_large.png"
    echo "birds_zoom_alt${i}.png + birds_zoom_alt${i}_large.png"
done



magick \( birds_zoom0_large.png -bordercolor none -border 0x0 \) \( birds_zoom1_large.png -bordercolor none -border 20x0 \) +append birds_0_1.png
magick \( birds_zoom0_large.png -bordercolor none -border 0x0 \) \( birds_zoom1_large.png -bordercolor none -border 20x0 \) \( birds_zoom2_large.png -bordercolor none -border 20x0 \) +append birds_0_1_2.png
magick \( birds_zoom0_large.png -bordercolor none -border 0x0 \) \( birds_zoom2_large.png -bordercolor none -border 20x0 \) \( birds_zoom3_large.png -bordercolor none -border 20x0 \) +append birds_0_2_3.png
magick \( birds_zoom0_large.png -bordercolor none -border 0x0 \) \( birds_zoom3_large.png -bordercolor none -border 20x0 \) \( birds_zoom4_large.png -bordercolor none -border 20x0 \) +append birds_0_3_4.png


# Generate color swatches

echo '[(103, 1, 0), (101, 2, 0), (99, 2, 0), (100, 2, 0), (102, 2, 0), (104, 0, 0), (114, 4, 3), (118, 2, 2)]' | python ../tools/color_chart.py - birds_colors_detail.png
echo '[(0, 0, 0), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255), (128, 128, 128), (255, 128, 128), (128, 255, 128), (255, 255, 128), (128, 128, 255), (255, 128, 255), (128, 255, 255), (255, 128, 0)]' | python ../tools/color_chart.py - mo5_palette_detail.png


exit

# Do the montage


# Extract ~20 frames spread across the video (1016s total), skip first 10s
# Each game segment is ~10s, so sample every ~50s to get a good variety
rm -f input.txt
rm -f montage_*.png
for i in 15 35 65 95 125 155 195 235 275 315 355 395 435 475 515 555 595 635 675 715; do \
  ffmpeg -y -ss $i -i YT-BestOf.mp4 -frames:v 1 "montage_${i}.png" 2>/dev/null; \
  echo "file 'montage_${i}.png'" >> input.txt
  echo "duration 0.7" >> input.txt
done

ffmpeg -y -f concat -safe 0 -i input.txt \
  -vf "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 mo5_games_montage2.gif

rm -f input.txt
rm -f montage_*.png
