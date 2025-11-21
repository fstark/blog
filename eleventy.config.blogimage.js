const path = require("path");
const eleventyImage = require("@11ty/eleventy-img");
const fs = require('fs');
const markdownIt = require("markdown-it");

module.exports = eleventyConfig => {
  // Initialize markdown-it for processing captions
  const md = markdownIt({ html: true });

  function relativeToInputPath(inputPath, relativeFilePath) {
    let split = inputPath.split("/");
    split.pop();
    return path.resolve(split.join(path.sep), relativeFilePath);
  }

  // -----------------------------------------------------
  //  Inserting an image in the blog flow
  // -----------------------------------------------------

  eleventyConfig.addAsyncShortcode("blogimage", async function imageShortcode(src, caption, widths, sizes, thumbnailMarker) {
    // thumbnailMarker is optional; if present and set to "thumbnail", 
    // this image should be used as the post's thumbnail

    let formats = [null];

    let file = relativeToInputPath(this.page.inputPath, src);
    let metadata = await eleventyImage(file, {
      widths: [640],
      formats,
      outputDir: path.join(eleventyConfig.dir.output, "img"),
    });

    let filemeta = null;

    if (metadata.jpeg)
      filemeta = metadata.jpeg[0];
    else if (metadata.png)
      filemeta = metadata.png[0];
    else if (metadata.gif)
      filemeta = metadata.gif[0];
    else
      console.log(metadata);

    const destfile = "img/large-" + filemeta.filename;

    fs.copyFile(file, path.join(eleventyConfig.dir.output, destfile), (err) => { });

    let markup = [];

    image2display = filemeta.url;

    if (filemeta.format === 'gif') {
      //  The images created for gifs are only the first frame...
      image2display = "/" + destfile;
    }

    // Process caption as markdown to support links and other markdown syntax
    const renderedCaption = md.renderInline(caption);

    markup.push('<div style="text-align: center;">');
    markup.push('<figure>');
    markup.push('<a href="/' + destfile + '" target="_blank">');
    markup.push('<img');
    markup.push('loading="lazy" decoding="async" src="' + image2display + '" class="blogimage"');
    markup.push('>');
    markup.push('</a>');
    markup.push('<figcaption>' + renderedCaption + '</figcaption>');
    markup.push('</figure>');
    markup.push('</div>');
    return markup.join(" ");
  });

  // -----------------------------------------------------
  //  Placeholder image for future/missing images
  // -----------------------------------------------------

  eleventyConfig.addShortcode("placeholder", function (description, caption) {
    // Create an SVG placeholder with the same dimensions as blogimage (640px)
    const width = 640;
    const height = 480;

    // Process caption as markdown to support links and other markdown syntax
    const renderedCaption = md.renderInline(caption);

    // Wrap text at word boundaries (40-50 chars per line)
    function wrapText(text, maxCharsPerLine = 45) {
      const words = text.split(' ');
      const lines = [];
      let currentLine = '';

      for (const word of words) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        if (testLine.length > maxCharsPerLine && currentLine) {
          lines.push(currentLine);
          currentLine = word;
        } else {
          currentLine = testLine;
        }
      }
      if (currentLine) {
        lines.push(currentLine);
      }
      return lines;
    }

    const lines = wrapText(description);
    const lineHeight = 28;
    const fontSize = 24;
    const totalHeight = lines.length * lineHeight;
    const startY = (height - totalHeight) / 2 + fontSize;

    // Generate text elements for each line
    const textElements = lines.map((line, index) => {
      const y = startY + (index * lineHeight);
      return `<text x="${width / 2}" y="${y}" text-anchor="middle" font-family="sans-serif" font-size="${fontSize}" fill="#666">${line}</text>`;
    }).join('\n      ');

    // Generate SVG with rectangle, diagonal lines, and centered multi-line text
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <rect width="${width}" height="${height}" fill="#f0f0f0" stroke="#999" stroke-width="2"/>
      <line x1="0" y1="0" x2="${width}" y2="${height}" stroke="#ccc" stroke-width="2"/>
      <line x1="${width}" y1="0" x2="0" y2="${height}" stroke="#ccc" stroke-width="2"/>
      ${textElements}
    </svg>`;

    // Use base64 encoding for the SVG to avoid separate file
    const base64svg = Buffer.from(svg).toString('base64');
    const dataUri = `data:image/svg+xml;base64,${base64svg}`;

    let markup = [];
    markup.push('<div style="text-align: center;">');
    markup.push('<figure>');
    markup.push('<img');
    markup.push(`src="${dataUri}" class="blogimage" alt="${description}"`);
    markup.push('>');
    markup.push('<figcaption>' + renderedCaption + '</figcaption>');
    markup.push('</figure>');
    markup.push('</div>');
    return markup.join(" ");
  });

  // -----------------------------------------------------
  //  Generate a square thumbnail for blog post listings
  // -----------------------------------------------------

  eleventyConfig.addAsyncShortcode("blogthumbnail", async function thumbnailShortcode(src, inputPath) {
    let formats = [null];

    // Handle relative path resolution
    let file;
    if (inputPath) {
      file = relativeToInputPath(inputPath, src);
    } else {
      // Fallback if called without inputPath
      file = src;
    }

    // Derive a unique prefix from the blog post path to avoid name collisions
    // e.g., /content/blog/mac-jailbar-repair/post.md -> "mac-jailbar-repair"
    let postSlug = '';
    if (inputPath) {
      const pathParts = inputPath.split(path.sep);
      // Find the blog post directory name (the folder containing the markdown file)
      const blogIndex = pathParts.indexOf('blog');
      if (blogIndex >= 0 && blogIndex < pathParts.length - 1) {
        postSlug = pathParts[blogIndex + 1];
      }
    }

    try {
      let metadata = await eleventyImage(file, {
        widths: [150],
        formats,
        outputDir: path.join(eleventyConfig.dir.output, "img"),
        // Use blog post slug as prefix to avoid name collisions
        filenameFormat: function (id, src, width, format, options) {
          const extension = path.extname(src);
          const name = path.basename(src, extension);
          const prefix = postSlug ? `${postSlug}-` : '';
          return `thumb-${prefix}${name}-${width}.${format || extension.substring(1)}`;
        }
      });

      let filemeta = null;
      if (metadata.jpeg)
        filemeta = metadata.jpeg[0];
      else if (metadata.png)
        filemeta = metadata.png[0];
      else if (metadata.gif)
        filemeta = metadata.gif[0];

      if (filemeta) {
        return filemeta.url;
      }
    } catch (e) {
      console.warn(`Failed to generate thumbnail for ${src}:`, e.message);
    }

    return null;
  });
};
