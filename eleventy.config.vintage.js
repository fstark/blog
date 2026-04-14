// eleventy.config.vintage.js
// Factory function for generating vintage-Mac-compatible site variants.
//
// Usage:
//   const vintage = require("./eleventy.config.vintage.js");
//   module.exports = vintage("color");   // 256-color variant
//   module.exports = vintage("bw");      // Black-and-white variant

const { DateTime } = require("luxon");
const markdownItAnchor = require("markdown-it-anchor");
const pluginRss = require("@11ty/eleventy-plugin-rss");
const pluginNavigation = require("@11ty/eleventy-navigation");
const { EleventyHtmlBasePlugin } = require("@11ty/eleventy");
const pluginDrafts = require("./eleventy.config.drafts.js");
const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");
const markdownIt = require("markdown-it");

// Detect external tools at startup
function hasCommand(cmd) {
	try {
		execSync(`command -v ${cmd}`, { stdio: "pipe" });
		return true;
	} catch (e) {
		return false;
	}
}

const hasImageMagick = hasCommand("magick") || hasCommand("convert");
const magickCmd = hasCommand("magick") ? "magick" : "convert";
const hasFfmpeg = hasCommand("ffmpeg");

module.exports = function (mode) {
	const isColor = mode === "color";
	const outputDir = isColor ? "_site_retro" : "_site_retro_bw";
	const imgMaxWidth = isColor ? 580 : 480;

	// Track converted images to avoid redundant work
	const convertedImages = new Set();

	return function (eleventyConfig) {
		process.env.VINTAGE_MODE = mode;

		eleventyConfig.addGlobalData("vintageMode", mode);

		// Passthrough: content public files (PDFs, downloadable files)
		eleventyConfig.addPassthroughCopy("content/**/public/*");

		eleventyConfig.addWatchTarget("content/**/*.{svg,webp,png,jpeg,jpg,gif}");

		// --- Plugins ---
		eleventyConfig.addPlugin(pluginDrafts);
		eleventyConfig.addPlugin(pluginNavigation);
		eleventyConfig.addPlugin(pluginRss);
		eleventyConfig.addPlugin(EleventyHtmlBasePlugin);

		// --- Filters (mirrored from main config) ---

		eleventyConfig.addFilter("readableDate", (dateObj, format, zone) => {
			return DateTime.fromJSDate(dateObj, { zone: zone || "utc" }).toFormat(format || "dd LLLL yyyy");
		});

		eleventyConfig.addFilter("htmlDateString", (dateObj) => {
			return DateTime.fromJSDate(dateObj, { zone: "utc" }).toFormat("yyyy-LL-dd");
		});

		eleventyConfig.addFilter("head", (array, n) => {
			if (!Array.isArray(array) || array.length === 0) return [];
			if (n < 0) return array.slice(n);
			return array.slice(0, n);
		});

		eleventyConfig.addFilter("min", (...numbers) => {
			return Math.min.apply(null, numbers);
		});

		eleventyConfig.addFilter("getAllTags", collection => {
			let tagSet = new Set();
			for (let item of collection) {
				(item.data.tags || []).forEach(tag => tagSet.add(tag));
			}
			return Array.from(tagSet);
		});

		eleventyConfig.addFilter("filterTagList", function (tags) {
			return (tags || []).filter(tag => ["all", "nav", "post", "posts"].indexOf(tag) === -1);
		});

		function sortByOrder(values) {
			let vals = [...values];
			return vals.sort((a, b) => {
				const dateComparison = new Date(a.date) - new Date(b.date);
				if (dateComparison !== 0) return dateComparison;
				return a.data.order - b.data.order;
			});
		}
		eleventyConfig.addFilter("sortByOrder", sortByOrder);

		eleventyConfig.addFilter("getFirstBlogImage", function (post) {
			if (!post || !post.template || !post.template.frontMatter) return null;
			const content = post.template.frontMatter.content;
			if (!content) return null;

			const thumbnailRegex = /{%\s*blogimage\s+"([^"]+)"[^%]*"thumbnail"\s*%}/;
			const thumbnailMatch = content.match(thumbnailRegex);
			if (thumbnailMatch && thumbnailMatch[1]) {
				return { src: thumbnailMatch[1], inputPath: post.inputPath };
			}

			const firstMatch = content.match(/{%\s*blogimage\s+"([^"]+)"/);
			if (firstMatch && firstMatch[1]) {
				return { src: firstMatch[1], inputPath: post.inputPath };
			}
			return null;
		});

		// --- Helpers ---

		function relativeToInputPath(inputPath, relativeFilePath) {
			let split = inputPath.split("/");
			split.pop();
			return path.resolve(split.join(path.sep), relativeFilePath);
		}

		function ensureDir(filePath) {
			const dir = path.dirname(filePath);
			if (!fs.existsSync(dir)) {
				fs.mkdirSync(dir, { recursive: true });
			}
		}

		// --- Image conversion ---

		async function convertImageToGif(srcFile, destFile, maxWidth) {
			if (convertedImages.has(destFile)) return;
			if (!fs.existsSync(srcFile)) {
				console.warn(`[vintage-${mode}] Source not found: ${srcFile}`);
				return;
			}

			ensureDir(destFile);
			maxWidth = maxWidth || imgMaxWidth;

			try {
				if (hasImageMagick) {
					if (isColor) {
						execSync(`${magickCmd} "${srcFile}" -resize ${maxWidth}x\\> -colors 256 "${destFile}"`, { stdio: "pipe", timeout: 30000 });
					} else {
						execSync(`${magickCmd} "${srcFile}" -resize ${maxWidth}x\\> -colorspace Gray -dither FloydSteinberg -colors 2 "${destFile}"`, { stdio: "pipe", timeout: 30000 });
					}
				} else {
					// Fallback: use sharp (available via @11ty/eleventy-img)
					const sharp = require("sharp");
					let pipeline = sharp(srcFile).resize(maxWidth, null, { withoutEnlargement: true });
					if (!isColor) {
						pipeline = pipeline.greyscale();
					}
					await pipeline.gif().toFile(destFile);
				}
				convertedImages.add(destFile);
			} catch (e) {
				console.warn(`[vintage-${mode}] Image conversion failed for ${srcFile}: ${e.message}`);
			}
		}

		async function convertVideoToGif(srcFile, destFile, duration) {
			if (!hasFfmpeg) return false;
			if (!fs.existsSync(srcFile)) return false;

			ensureDir(destFile);
			const width = isColor ? 320 : 250;
			duration = duration || 10;

			try {
				if (isColor) {
					execSync(
						`ffmpeg -y -i "${srcFile}" -t ${duration} -vf "fps=5,scale=${width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse" "${destFile}"`,
						{ stdio: "pipe", timeout: 120000 }
					);
				} else {
					execSync(
						`ffmpeg -y -i "${srcFile}" -t ${duration} -vf "fps=5,scale=${width}:-1:flags=lanczos,format=gray,split[s0][s1];[s0]palettegen=max_colors=2[p];[s1][p]paletteuse=dither=floyd_steinberg" "${destFile}"`,
						{ stdio: "pipe", timeout: 120000 }
					);
				}
				return true;
			} catch (e) {
				console.warn(`[vintage-${mode}] Video conversion failed for ${srcFile}: ${e.message}`);
				return false;
			}
		}

		// --- Vintage shortcodes ---

		const md = markdownIt({ html: true });

		// Unique GIF name for a shortcode image
		function vintageGifName(pageInputPath, src) {
			const postSlug = path.basename(path.dirname(pageInputPath));
			const baseName = path.basename(src, path.extname(src));
			// Sanitize for filesystem
			const safeName = baseName.replace(/[^a-zA-Z0-9._-]/g, "_");
			return `img/${mode}-${postSlug}-${safeName}.gif`;
		}

		// blogimage
		eleventyConfig.addAsyncShortcode("blogimage", async function (src, caption, widths, sizes, thumbnailMarker) {
			const file = relativeToInputPath(this.page.inputPath, src);
			const gifName = vintageGifName(this.page.inputPath, src);
			const destFile = path.join(outputDir, gifName);

			await convertImageToGif(file, destFile);

			const renderedCaption = caption ? md.renderInline(caption) : "";
			const url = "/" + gifName;

			return [
				'<center>',
				`<img src="${url}" alt="${renderedCaption}">`,
				`<br><font size="2"><i>${renderedCaption}</i></font>`,
				'</center><br>'
			].join("\n");
		});

		// blogvideo → animated GIF (10s, low framerate)
		eleventyConfig.addAsyncShortcode("blogvideo", async function (src, caption) {
			const file = relativeToInputPath(this.page.inputPath, src);
			const gifName = vintageGifName(this.page.inputPath, src);
			const destFile = path.join(outputDir, gifName);

			const success = await convertVideoToGif(file, destFile, 10);

			if (success) {
				return [
					'<center>',
					`<img src="/${gifName}" alt="${caption}">`,
					`<br><font size="2"><i>${caption} (animated)</i></font>`,
					'</center><br>'
				].join("\n");
			} else {
				return `<center><font size="2"><i>[Video: ${caption}]</i></font></center><br>`;
			}
		});

		// image (used in about page, layouts)
		eleventyConfig.addAsyncShortcode("image", async function (src, alt) {
			const file = relativeToInputPath(this.page.inputPath, src);
			const gifName = vintageGifName(this.page.inputPath, src);
			const destFile = path.join(outputDir, gifName);

			await convertImageToGif(file, destFile);

			return `<img src="/${gifName}" alt="${alt}">`;
		});

		// blogthumbnail (not used in vintage postslist, but registered to avoid errors)
		eleventyConfig.addAsyncShortcode("blogthumbnail", async function (src, inputPath) {
			const file = relativeToInputPath(inputPath || this.page.inputPath, src);

			let postSlug = "";
			const pathParts = (inputPath || this.page.inputPath).split(path.sep);
			const blogIndex = pathParts.indexOf("blog");
			if (blogIndex >= 0 && blogIndex < pathParts.length - 1) {
				postSlug = pathParts[blogIndex + 1];
			}

			const baseName = path.basename(src, path.extname(src));
			const safeName = baseName.replace(/[^a-zA-Z0-9._-]/g, "_");
			const gifName = `img/${mode}-thumb-${postSlug}-${safeName}.gif`;
			const destFile = path.join(outputDir, gifName);

			try {
				await convertImageToGif(file, destFile, 100);
			} catch (e) {
				return "";
			}

			return "/" + gifName;
		});

		// placeholder (no SVG in vintage mode)
		eleventyConfig.addShortcode("placeholder", function (description, caption) {
			const renderedCaption = caption ? md.renderInline(caption) : "";
			return [
				'<center>',
				`<i>[${description}]</i>`,
				`<br><font size="2"><i>${renderedCaption}</i></font>`,
				'</center><br>'
			].join("\n");
		});

		// digression → blockquote (no CSS)
		eleventyConfig.addPairedShortcode("digression", function (content, label) {
			const renderedContent = md.render(content);
			const labelHtml = label ? `<b>${label}</b> ` : "<b>Digression:</b> ";
			return `<blockquote>\n${labelHtml}${renderedContent}\n</blockquote>`;
		});

		// github (plain link, no SVG icons)
		eleventyConfig.addShortcode("github", function (repo, text, file) {
			const username = "fstark";
			let url = `https://github.com/${username}/${repo}`;
			if (file) {
				const isDirectory = file.endsWith("/");
				const pathType = isDirectory ? "tree" : "blob";
				const cleanPath = file.replace(/\/$/, "");
				url += `/${pathType}/main/${cleanPath}`;
			}
			return `<a href="${url}">${text}</a>`;
		});

		// twitter
		eleventyConfig.addAsyncShortcode("twitter", async function (handle) {
			return `<a href="https://www.twitter.com/${handle}">${handle}</a>`;
		});

		// mastodon
		eleventyConfig.addAsyncShortcode("mastodon", async function (server, handle) {
			return `<a href="https://${server}/${handle}">${handle}</a>`;
		});

		// --- Transform: convert inline markdown images (PNG→GIF, etc.) ---
		eleventyConfig.addTransform("vintageMarkdownImages", async function (content) {
			if (!this.page.outputPath || !this.page.outputPath.endsWith(".html")) {
				return content;
			}

			const pageInputDir = path.dirname(this.page.inputPath);
			const pageOutputDir = path.dirname(this.page.outputPath);

			const imgRegex = /(<img\b[^>]*?\bsrc=")([^"]+)("[^>]*?>)/gi;
			const promises = [];
			const replacements = [];

			let match;
			while ((match = imgRegex.exec(content)) !== null) {
				const fullMatch = match[0];
				const before = match[1];
				const src = match[2];
				const after = match[3];

				// Skip external URLs, data URIs, and already-converted vintage images
				if (src.startsWith("http") || src.startsWith("data:") || src.startsWith("//")) continue;
				if (src.includes(`/${mode}-`)) continue;

				const ext = path.extname(src).toLowerCase();
				// Only convert image formats Netscape 2.0 can't handle (or that need vintage treatment)
				if (![".png", ".webp", ".avif", ".svg"].includes(ext) && ext !== ".jpg" && ext !== ".jpeg" && ext !== ".gif") continue;
				// SVGs can't be easily converted
				if (ext === ".svg") continue;

				// Resolve source file
				const sourceFile = path.resolve(pageInputDir, src);
				if (!fs.existsSync(sourceFile)) continue;

				// For PNG/WebP/AVIF → GIF; for JPG/GIF → copy with vintage treatment
				const gifSrc = src.replace(/\.(png|jpg|jpeg|webp|avif|gif)$/i, ".gif");
				const destFile = path.resolve(pageOutputDir, gifSrc);

				replacements.push({ fullMatch, before, after, src, gifSrc, sourceFile, destFile });
			}

			// Convert all images
			for (const r of replacements) {
				await convertImageToGif(r.sourceFile, r.destFile);
			}

			// Apply replacements in the HTML
			let result = content;
			for (const r of replacements) {
				result = result.replace(r.fullMatch, `${r.before}${r.gifSrc}${r.after}`);
			}

			return result;
		});

		// --- Dev server: bind to all interfaces for LAN access ---
		eleventyConfig.setServerOptions({
			hostname: "0.0.0.0",
		});

		// --- Markdown configuration ---
		eleventyConfig.amendLibrary("md", mdLib => {
			mdLib.use(markdownItAnchor, {
				permalink: false,
				level: [1, 2, 3, 4],
				slugify: eleventyConfig.getFilter("slugify")
			});
		});

		return {
			templateFormats: ["md", "njk", "html", "liquid"],
			markdownTemplateEngine: "njk",
			htmlTemplateEngine: "njk",
			dir: {
				input: "content",
				includes: "../_includes_vintage",
				data: "../_data",
				output: outputDir,
			},
			pathPrefix: "/",
		};
	};
};
