const path = require("path");
const eleventyImage = require("@11ty/eleventy-img");
const fs = require('fs');

module.exports = eleventyConfig => {
	function relativeToInputPath(inputPath, relativeFilePath) {
		let split = inputPath.split("/");
		split.pop();

		return path.resolve(split.join(path.sep), relativeFilePath);
	}


	// Eleventy Image shortcode
	// https://www.11ty.dev/docs/plugins/image/
	eleventyConfig.addAsyncShortcode("image", async function imageShortcode(src, alt, widths, sizes) {

        if (src.endsWith( ".gif" ))
        {
            return '<img src="'+src+'" alt="${alt}" />';
        }

		// Full list of formats here: https://www.11ty.dev/docs/plugins/image/#output-formats
		// Warning: Avif can be resource-intensive so take care!
		// let formats = ["gif", "auto","avif", "webp", ];
		let formats = [null];

		let file = relativeToInputPath(this.page.inputPath, src);
		let metadata = await eleventyImage(file, {
			widths: widths || ["auto"],
			formats,
			outputDir: path.join(eleventyConfig.dir.output, "img"), // Advanced usage note: `eleventyConfig.dir` works here because we’re using addPlugin.
		});

		// TODO loading=eager and fetchpriority=high
		let imageAttributes = {
			alt,
			sizes,
			loading: "lazy",
			decoding: "async",
		};
		return eleventyImage.generateHTML(metadata, imageAttributes);
    });
    
// -----------------------------------------------------
//  Inserting an image in the blog flow
// -----------------------------------------------------

	eleventyConfig.addAsyncShortcode("blogimage", async function imageShortcode(src, caption, widths, sizes) {
		let formats = [null];

		let file = relativeToInputPath(this.page.inputPath, src);
		let metadata = await eleventyImage(file, {
			widths: [640],
			formats,
			outputDir: path.join(eleventyConfig.dir.output, "img"), // Advanced usage note: `eleventyConfig.dir` works here because we’re using addPlugin.
		});

        if (metadata.jpeg)
            filemeta = metadata.jpeg[0];
        else if (metadata.png)
            filemeta = metadata.png[0];
        else
            console.log( metadata );

        const destfile = "img/large-"+filemeta.filename;

        fs.copyFile( file, path.join(eleventyConfig.dir.output, destfile), (err) => {} );
        // console.log( path.join(eleventyConfig.dir.output, destfile) );

        let markup = [];
        // console.log( file );
        // console.log( metadata );
        markup.push( '<figure><a href="/'+destfile+'" target="_blank"><img' );
        markup.push( 'loading="lazy" decoding="async" src="'+filemeta.url+'" class="blogimage"')
        markup.push( '></a><figcaption>'+caption+'</figcaption></figure>' );
        return markup.join(" ");
    });
    
	eleventyConfig.addAsyncShortcode("blogvideo", async function imageShortcode(src, alt, widths, sizes) {
    
        let file = relativeToInputPath(this.page.inputPath, src);
        const destfile = path.join(eleventyConfig.dir.output, src);

    fs.copyFile( file, destfile, (err) => {} );

    return '<video controls width="100%"><source src="/'+src+'" type="video/mp4">Your browser does not support the video tag.</video>';
    } );

    eleventyConfig.addAsyncShortcode("twitter", async function imageShortcode( handle ) {
      console.log( handle );
      return '<a href="https://www.twitter.com/'+handle+'" target="_blank">'+handle+'</a>';
    });

    eleventyConfig.addAsyncShortcode("mastodon", async function imageShortcode( server, handle ) {
      console.log( handle );
      return '<a href="https://'+server+'/'+handle+'" target="_blank">'+handle+'</a>';
    });

    eleventyConfig.addAsyncShortcode("digression", async function digressionShortcode( text ) {
      return '';
    });

  };

/*
function generateHTML(metadata, attributes = {}, options = {}) {
  let isInline = options.whitespaceMode !== "block";
  let markup = [];
  let obj = generateObject(metadata, attributes, options);
  for(let tag in obj) {
    if(!Array.isArray(obj[tag])) {
      markup.push(mapObjectToHTML(tag, obj[tag]));
    } else {
      markup.push(`<${tag}>`);
      for(let child of obj[tag]) {
        let childTagName = Object.keys(child)[0];
        markup.push((!isInline ? "  " : "") + mapObjectToHTML(childTagName, child[childTagName]));
      }
      markup.push(`</${tag}>`);
    }
  }
  return markup.join(!isInline ? "\n" : "");
}
*/
