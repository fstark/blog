module.exports = eleventyConfig => {
  // Twitter handle shortcode
  eleventyConfig.addAsyncShortcode("twitter", async function imageShortcode(handle) {
    console.log(handle);
    return '<a href="https://www.twitter.com/' + handle + '" target="_blank">' + handle + '</a>';
  });

  // Mastodon handle shortcode
  eleventyConfig.addAsyncShortcode("mastodon", async function imageShortcode(server, handle) {
    console.log(handle);
    return '<a href="https://' + server + '/' + handle + '" target="_blank">' + handle + '</a>';
  });
};
