---
title: Vectorizing a Bitmap Image
description: Vectorizing a bitmap image
date: 2023-08-08
order: 1
eleventyExcludeFromCollections: true
tags:
  - coding
  - algorithmics
---

{% blogimage "img/tracing-process.png", "From a prompt to a vectorized print" %}

When writing [PloTTY](/blog/plotty), I needed a way to turn arbitrary images into a set of vectors that were tracable on an old pen plotter.

I thought about two broad approaches: one was to find a way to render *surfaces* and [shade those](https://paintingdemos.com/6-shading-techniques-for-your-drawings/), the other was to only trace contours.

It is clear that the first approach would apply to a broader set of input images, and I haven't rulesd out to revisit pltty one day with a hatching approach in mind. Howerer, I settled on tracing contour because a) it would produce smaller images (I had no idea if it would take 10 minutes or 6 hours to draw a complex image), b) it would be nicer on the plotter mecanism (it is an old lady, after all), and c) I had a vague idea about how to do it.

The first order of business is to get source images that are suiteable. I am looking for blak-and-white clearly delineated images. I got thouse out of midjourney using a prompt of "something black and white line art constant thickness simple children coloring book". The algorithm works perfectly on any black and white, clrealy delimited images.

Let's dig info the details, it is surprisingly straightforward.

## Loading, resizing, black and white

We use the ``opencv`` library to do most image manipulations.

The first order of business is to load the image:

```python
img = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
```

The next step is to extract the corner, as midjoutney unfortunately generates 4 images.

```python
# Extract corner
h,w = img.shape
if corner!=0:
    corners = [(0,0),(0,1),(1,0),(1,1)]
    c = corners[corner-1]
    start_row = h//2 * c[0]
    end_row = start_row + h//2
    start_col = w//2 * c[1]
    end_col = start_col + w//2
    img = img[start_row:end_row, start_col:end_col]
```

Nothing particularly exciting here. Note that opencv images are just matrices.

Using 0 as a corner will skip this operation, which is useful for custom images.

## Resizing the image

```python
size = 95*5     # PB-700 size

# Resize to PB-700 resolution
img = cv2.resize( img, (size,size), interpolation = cv2.INTER_AREA)
```

The plotter paper is 114mm wide, but the usable portion is only 95mmm, according to the documentation. The resolution is 0.2mm, so there are 475 addressable points. In this version I arbitrarily decided that images would be square, which is non-sense: there would be no problem do a very tail portrait with PloTTY.

Using 475 pixels means that lines will be separated by at least 0.4mm, as there will the need for a separating white pixels. So, in theory, it should be possible to get slightly finer images out of a CA-10 by using a 950 pixels grid but forcing plot coordinates to be on even coordinates. It would make the rest of the code harder to follow and fragile.

```python
# Converting image to a binary image
# ( black and white only image).
_, threshold = cv2.threshold(img, 55, 255, cv2.THRESH_BINARY)
```

Converting to pure black and white is simple (but slightly mysterious due to the fact that cv2.threshold returns 2 values, the first ignored one being the threshold value used).

I decided to use ``55`` as the threshold value, but it is completely arbitrary. Using adaptative thresholding with something like: ``threshold = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)`` is probably more robust. But, I haven't raninto a problem there yet.

Second, we'll do the magic trick of removing the large black areas





PloTTY is a set of linux command lines that transforms images into traces, suitable for drawing on a vintage Casio PB-700, with its FA-10 pen plotter.

Here is a typical example of the result

![Final Result](writeup/final.jpg)

Read more to get more detail of the process!

First, the source image, courtersy midjourney:

![Source](writeup/source.png)

The source is then resized and converted to black and white, giving:

![Source](writeup/threshold.png)

The large black areas need to be removed, so an erosion map is computed:

![Erosion](writeup/erosion.png)

And removed from the orginal image, leading to:

![Eroded](writeup/eroded.png)

This eroded picture contains lines, that we can convert to single pixels, giving:

![Skeleton](writeup/skeleton.png)

This is still a pixel image, but it can be traced, giving the following segments:

![Segments](writeup/segments.png)

Segments are ordered and flipped to minimize the travel of the plotter head:

![Motion](writeup/motions.png)

And, drawing the image would give the following result:

![Result](writeup/result.png)
