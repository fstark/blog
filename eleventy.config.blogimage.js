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

  eleventyConfig.addAsyncShortcode("blogimage", async function imageShortcode(src, caption, widths, sizes) {

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
};
