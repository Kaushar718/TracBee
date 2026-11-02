
document.addEventListener("DOMContentLoaded", function () {

    const headingPatterns = [
        {
            name: "An overview of this role",
            type: "heading"
        },
        {
            name: "What you’ll do",
            type: "heading"
        },
        {
            name: "What you'll do",
            type: "heading"
        },
        {
            name: "What you’ll bring",
            type: "heading"
        },
        {
            name: "What you'll bring",
            type: "heading"
        },
        {
            name: "About the team",
            type: "heading"
        },
        {
            name: "How GitLab Supports Full-Time Employees",
            type: "heading"
        },
        {
            name: "Country Hiring Guidelines",
            type: "heading"
        },
        {
            name: "Privacy Policy",
            type: "heading"
        },
        {
            name: "Responsibilities",
            type: "heading"
        },
        {
            name: "Requirements",
            type: "heading"
        },
        {
            name: "Qualifications",
            type: "heading"
        },
        {
            name: "Benefits",
            type: "heading"
        },
        {
            name: "What we're looking for",
            type: "heading"
        },
        {
            name: "What we're looking for:",
            type: "heading"
        },
        {
            name: "About the role",
            type: "heading"
        },
        {
            name: "About the company",
            type: "heading"
        }
    ];

    const headingNames = headingPatterns.map(item =>
        item.name.toLowerCase().replace(/:$/, "")
    );

    function normalizeText(text) {

        return text
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .replace(/\u00a0/g, " ")
            .replace(/[ \t]+/g, " ")
            .trim();

    }

    function escapeRegex(text) {

        return text.replace(
            /[.*+?^${}()|[\]\\]/g,
            "\\$&"
        );

    }

    function splitDescription(text) {

        let result = normalizeText(text);

        // Add line breaks before known headings.
        headingPatterns.forEach(item => {

            const pattern = new RegExp(
                "(?<!^)" + escapeRegex(item.name),
                "gi"
            );

            result = result.replace(
                pattern,
                "\n\n" + item.name + "\n"
            );

        });

        // Split sentences into readable units only for
        // the known responsibility and qualification sections.
        return result
            .split(/\n+/)
            .map(line => line.trim())
            .filter(line => line.length > 0);

    }

    function isHeading(line) {

        const cleaned = line
            .replace(/:$/, "")
            .trim()
            .toLowerCase();

        return headingNames.includes(cleaned);

    }

    function isBulletLike(line) {

        return /^[-•*▪◦]\s+/.test(line);

    }

    function removeBulletSymbol(line) {

        return line.replace(/^[-•*▪◦]\s+/, "").trim();

    }

    function isListSection(heading) {

        const value = heading.toLowerCase();

        return (
            value.includes("what you") ||
            value.includes("responsibilit") ||
            value.includes("requirement") ||
            value.includes("qualification") ||
            value.includes("benefit") ||
            value.includes("what we're looking")
        );

    }

    function createHeading(text) {

        const heading = document.createElement("h3");

        heading.className = "job-heading";
        heading.textContent = text;

        return heading;

    }

    function createParagraph(text) {

        const paragraph = document.createElement("p");

        paragraph.className = "job-paragraph";
        paragraph.textContent = text;

        return paragraph;

    }

    function createListItem(text) {

        const item = document.createElement("li");

        item.textContent = removeBulletSymbol(text);

        return item;

    }

    function formatDescription(container) {

        if (!container) return;

        const originalText = container.dataset.description;

        if (!originalText) return;

        const lines = splitDescription(originalText);

        const fragment = document.createDocumentFragment();

        let currentList = null;
        let currentHeading = "";
        let pendingParagraph = [];

        function flushParagraph() {

            if (pendingParagraph.length === 0) return;

            const paragraphText = pendingParagraph.join(" ").trim();

            if (paragraphText) {
                fragment.appendChild(
                    createParagraph(paragraphText)
                );
            }

            pendingParagraph = [];

        }

        function flushList() {

            currentList = null;

        }

        lines.forEach(line => {

            if (isHeading(line)) {

                flushParagraph();
                flushList();

                currentHeading = line.replace(/:$/, "").trim();

                fragment.appendChild(
                    createHeading(currentHeading)
                );

                return;

            }

            if (isBulletLike(line)) {

                flushParagraph();

                if (!currentList) {

                    currentList = document.createElement("ul");

                    fragment.appendChild(currentList);

                }

                currentList.appendChild(
                    createListItem(line)
                );

                return;

            }

            if (currentHeading && isListSection(currentHeading)) {

                flushParagraph();

                if (!currentList) {

                    currentList = document.createElement("ul");

                    fragment.appendChild(currentList);

                }

                currentList.appendChild(
                    createListItem(line)
                );

                return;

            }

            flushList();

            pendingParagraph.push(line);

        });

        flushParagraph();

        container.replaceChildren(fragment);

    }

    // Format short preview.
    const preview = document.getElementById(
        "jobDescriptionPreview"
    );

    formatDescription(preview);

    // Format complete description.
    const fullDescription = document.getElementById(
        "fullJobDescription"
    );

    formatDescription(fullDescription);

});
