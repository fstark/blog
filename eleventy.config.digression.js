module.exports = eleventyConfig => {
	// Digression paired shortcode - displays side notes/tangential content
	// Usage: {% digression %} or {% digression "Custom Label:" %}
	eleventyConfig.addPairedShortcode("digression", function(content, label) {
		const labelText = label || "Digression:";
		return `<aside class="digression"><span class="digression-label">${labelText}</span> ${content}</aside>`;
	});
};
