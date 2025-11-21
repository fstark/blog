module.exports = eleventyConfig => {
    // GitHub repository link shortcode for fstark's repositories
    // Usage: {% github "repo", "display text", "optional/file/path" %}
    eleventyConfig.addShortcode("github", function (repo, text, file) {
        const username = "fstark";
        let url = `https://github.com/${username}/${repo}`;
        let icon;

        // If a file path is provided, add it to the URL
        if (file) {
            // Determine if it's a directory (ends with /) or a file
            const isDirectory = file.endsWith('/');
            const pathType = isDirectory ? 'tree' : 'blob';
            // Remove trailing slash for URL construction
            const cleanPath = file.replace(/\/$/, '');
            url += `/${pathType}/main/${cleanPath}`;

            // Choose icon based on type
            if (isDirectory) {
                // Folder icon (outline)
                icon = `<svg height="16" width="16" viewBox="0 0 16 16" style="display: inline-block; vertical-align: text-bottom; margin-left: 4px;" aria-hidden="true"><path fill="currentColor" d="M1.75 1A1.75 1.75 0 000 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0016 13.25v-8.5A1.75 1.75 0 0014.25 3H7.5a.25.25 0 01-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75zM1.5 2.75a.25.25 0 01.25-.25H5c.199 0 .384.079.53.22l.912 1.22c.223.297.548.47.912.47h6.896a.25.25 0 01.25.25v8.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V2.75z"></path></svg>`;
            } else {
                // File icon (outline)
                icon = `<svg height="16" width="16" viewBox="0 0 16 16" style="display: inline-block; vertical-align: text-bottom; margin-left: 4px;" aria-hidden="true"><path fill="currentColor" d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0113.25 16h-9.5A1.75 1.75 0 012 14.25V1.75zm1.75-.25a.25.25 0 00-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 00.25-.25V6h-2.75A1.75 1.75 0 019 4.25V1.5H3.75a.25.25 0 00-.25.25zM10.5 4.25c0 .138.112.25.25.25h2.688a.252.252 0 00-.011-.013l-2.914-2.914a.272.272 0 00-.013-.011V4.25z"></path></svg>`;
            }
        } else {
            // GitHub repository icon (official GitHub logo)
            icon = `<svg height="16" width="16" viewBox="0 0 16 16" style="display: inline-block; vertical-align: text-bottom; margin-left: 4px;" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>`;
        }

        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}${icon}</a>`;
    });
};
