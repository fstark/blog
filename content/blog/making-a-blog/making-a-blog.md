---
title: Making a Blog using 11ty (Eleventy)
description: Woes of blog making
date: 2023-08-07
order: 0
tags:
  - blog
  - rant
---

This is a rant. You should really skip it.

Haven't made a blog for a long time, but it seems I can't really tip-toe around it forever.

In an ideal world, there would be platforms out there where onecan push content, and it would live forever, hosted, searchable, ad-free.

However, enshittification is happening on every platform, so I have to do the thing myself.

For the macflim annoucement, I actually write the HTML by hand, as every bloggin framework out there seemed like a pain, so I bit the bullet.

However, I have quite a few aditional projects, and while creating a specific HTML file for each could be fun, maintaining it seem impossible. The macflim webpage is now out-of-date, and I am not looking forward adding information to it.

## My requirements

My set of hard requirements are pretty simple:

- I want to be able to create simple pages that render correctly on all devices
- I want no need to use javascript
- I want no adverstising or tracking
- I want to be able to host it myself
- I want reasonable control on the layout of the output
- I want the content to be available to me and everyone in an open fashion

There are softer requirements, that I understand can make thing way harder:

- I'd like to be able to have multiple writers
- I'd like to have the content stored in a public github and publish via commit
- I'd like to have a version of the website accessible to vintge web browser

Anyway, all this meant using a static web site generator, and hosting the resulting files myself. I did spent some time looking at various generators, but nothing seemed to be close to what I needed. I did think about writing mine, as the layout I need is pretty trivial, but that's the classic trap. If I want to do that fine, but I need to fail with a generator first.

As my need are simple, any generator should work. So I pickedup 11ty, even if I absolutely despise javascript, nodejs and npm (those are, to me, the epithom of everything that went wrong with computing, the kingdom of "a peu pres". All those things almost work).

## It almost work

To give an example of what "almost work" means, let's see how I can add an image to a page.

I can use

``
{ % image "path/to/image.png", "Image Title"}
``

*(Well, actually I can't I had to add a space betwee ``{`` and ``%``, because if I don't the templating engine interprets this as a command...)

However, I just want to specify a hard-coded size for the image display. Well, here is the [documentation of the "image plugin"](https://www.11ty.dev/docs/plugins/image/#creating-an-shortcode). I didn't want something complicated. I didn't want to know about the internal of the javascript. I just wanted to specify a size.

The third paragram says *Easily add width and height attributes on \<img> elements for proper aspect ratio mapping.*. Go one, scroll, and find the way to *easily add width and height* from the image tag. There is none. The onyl thing you'll find is some ``"(min-width: 30em) 50vw, 100vw"``, which, of course doesn't not work:

```
[11ty] 1. Having trouble rendering njk template ./content/blog/Making a Blog/Making a Blog.md (via TemplateContentRenderError)
[11ty] 2. (./content/blog/Making a Blog/Making a Blog.md)
[11ty]   EleventyShortcodeError: Error with Nunjucks shortcode `image` (via Template render error)
[11ty] 3. widths.map is not a function (via Template render error)
```

And this is supposed to be the leanest, simplest, website generator... And as things rarely go better in the web world, I see a lot of pain in my future...

## Parsing code blocks

While writing this rant, I didn't realise that the templating engine would parse the ``%image`` inside the code block, so it failed and just arbitrarily truncated the content

{% image "img/11ty-truncate.png", "Image Title" %}

## Restarting the server

Oh, did I mention that the development experience is awesome, as the 11ty command runs in the background and magically updates the webpage whenever I type something. The workflow of writing a text page with tokens and have the rendered version update gives an experience close to using WordStar in 1983, which I feel is appropriate for a retro-blog.

Of course, if I rename a page, the server shits itself, and won't work until I restart it. Almost works...

## Animated gifs...

So, I needed to embeded animated gifs. The fantastic ``image`` plugin supports animated gif, in the sense that it doesn't crash, and generates an image of the first frame of the gif.

Crawling the web, I discovered that I should add:

``js
				sharpOptions: {
				  animated: true
				}
``

to some code to have it handle animated gifs.

I looked at the most logical place and added that:

``js
		let metadata = await eleventyImage(file, {
			widths: widths || ["auto"],
			formats,
			outputDir: path.join(eleventyConfig.dir.output, "img"), // Advanced usage note: `eleventyConfig.dir` works here because we’re using addPlugin.
			sharpOptions: {
				animated: true
			}
		});
``

This was the result, I kid you not:

{% image "img/11ty-animated-gif.png", "An animated gif, according to 11ty..." %}

I am not surprised, but the awfulness of modern frameworks never fails to disapoint me...

Of course, I understood that was because the image plugin didn't output animated gif by default, so I added gif to the list of supported outputs. Which didn't work because it favored the other format. After removing the other formats, I got the marvelous:

{% image "img/11ty-animated-gif-2.png", "We go the animation working!" %}

And, yes, it was animated. It just seems that the plugin computed the size based on the stacking of all the frames of the animated gif...
