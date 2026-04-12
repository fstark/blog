#!/bin/bash

# Create animated GIF from PNG files with text overlay
# Output: ../img/build.gif with 1 second delay between frames

cd "$(dirname "$0")"

# Create output directory if it doesn't exist
mkdir -p ../img

# Create temporary directory for processed images
TEMP_DIR=$(mktemp -d)

# Read text file into array
mapfile -t TEXT_LINES < text.txt

# Process each image with corresponding text
i=0
for img in screenshots/*.png; do
    if [ $i -lt ${#TEXT_LINES[@]} ]; then
        # Extend canvas below image and add text
        convert "$img" \
            -gravity south \
            -background white \
            -splice 0x30 \
            -font Helvetica \
            -pointsize 16 \
            -fill black \
            -gravity south \
            -annotate +0+5 "${TEXT_LINES[$i]}" \
            "$TEMP_DIR/$(printf "%03d" $i).png"
        ((i++))
    fi
done

# Create animated GIF from processed images
# -delay 100 = 100 centiseconds = 1 second
# -loop 0 = infinite loop
convert -delay 200 -loop 0 "$TEMP_DIR"/*.png ../img/build.gif

# Clean up
rm -rf "$TEMP_DIR"

echo "Animated GIF created at ../img/build.gif"
