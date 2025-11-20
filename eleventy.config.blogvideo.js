const path = require("path");
const fs = require('fs');

module.exports = eleventyConfig => {
  function relativeToInputPath(inputPath, relativeFilePath) {
    let split = inputPath.split("/");
    split.pop();
    return path.resolve(split.join(path.sep), relativeFilePath);
  }

  eleventyConfig.addAsyncShortcode("blogvideo", async function imageShortcode(src, alt, widths, sizes) {

    let file = relativeToInputPath(this.page.inputPath, src);
    const destfile = path.join(eleventyConfig.dir.output, src);

    fs.copyFile(file, destfile, (err) => { });

    return '<video controls width="100%"><source src="/' + src + '" type="video/mp4">Your browser does not support the video tag.</video>';
  });
};
