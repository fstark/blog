const markdownIt = require("markdown-it");

module.exports = eleventyConfig => {
	// Digression paired shortcode - displays side notes/tangential content
	// Usage: {% digression %} or {% digression "Custom Label:" %}
	
	let md;
	
	eleventyConfig.addPairedShortcode("digression", function(content, label) {
		// Lazy initialization of markdown-it
		if (!md) {
			md = markdownIt({ html: true });
		}
		
		// Render the content as markdown
		// Using render() instead of renderInline() to properly handle paragraphs
		const renderedContent = md.render(content);
		
		// Only include label if one is provided
		const labelHtml = label ? `<span class="digression-label">${label}</span> ` : '';
		
		return `<aside class="digression">${labelHtml}${renderedContent}</aside>`;
	});
};
