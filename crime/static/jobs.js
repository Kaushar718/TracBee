
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("jobsFilterForm");
    const jobGrid = document.getElementById("jobGrid");
    const status = document.getElementById("jobsStatus");
    const resultsInfo = document.getElementById("resultsInfo");
    const pageInfo = document.getElementById("pageInfo");
    const previousButton = document.getElementById("previousPage");
    const nextButton = document.getElementById("nextPage");
    const clearButton = document.getElementById("clearFilters");

    let currentPage = 1;
    let totalPages = 1;

    const initialParams = new URLSearchParams(window.location.search);

    ["search", "skill", "company", "location", "year"].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = initialParams.get(id) || "";
        }
    });

    const employmentInput = document.getElementById("employmentType");

    if (employmentInput) {
        employmentInput.value =
            initialParams.get("employment_type") || "";
    }

    function getFilters(page) {
        const params = new URLSearchParams();

        [
            "search",
            "skill",
            "company",
            "location",
            "year",
            "employmentType"
        ].forEach(id => {

            const input = document.getElementById(id);

            if (!input) return;

            const value = input.value.trim();

            if (value) {
                params.set(
                    id === "employmentType" ? "employment_type" : id,
                    value
                );
            }
        });

        params.set("page", page);
        params.set("page_size", 10);

        return params;
    }

    function addText(parent, tag, className, value) {

        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        element.textContent = value || "";

        parent.appendChild(element);

        return element;
    }

    function getSourceName(source) {

        if (source === "TracBee Demo Dataset") {
            return "Demo dataset";
        }

        const token = (source || "").split(":")[1] || "";

        if (token === "gitlab") {
            return "GitLab · Greenhouse";
        }

        if (token === "razorpaysoftwareprivatelimited") {
            return "Razorpay · Greenhouse";
        }

        return source || "Unknown source";
    }

    function formatDate(value) {

        if (!value) {
            return "Date not available";
        }

        const date = new Date(value + "T00:00:00");

        if (Number.isNaN(date.getTime())) {
            return "Date not available";
        }

        return date.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    }

    function formatSalary(job) {

        if (job.salary_min === null && job.salary_max === null) {
            return "Salary not disclosed";
        }

        const currency = job.currency || "INR";

        return [
            job.salary_min ?? "",
            job.salary_max ?? ""
        ].filter(Boolean).join(" – ") + " " + currency;
    }

    function getShortDescription(description) {

        if (!description) {
            return "No job description available.";
        }

        const cleanText = description
            .replace(/<[^>]*>/g, " ")
            .replace(/&nbsp;/gi, " ")
            .replace(/&amp;/gi, "&")
            .replace(/\s+/g, " ")
            .trim();

        const limit = 160;

        if (cleanText.length <= limit) {
            return cleanText;
        }

        return cleanText.slice(0, limit).trimEnd() + "...";
    }

    function createJobCard(job) {

        const card = document.createElement("article");
        card.className = "job-card";

        addText(card, "p", "job-company", job.company);
        addText(card, "h3", "job-title", job.title);

        const meta = document.createElement("div");
        meta.className = "job-meta";

        addText(
            meta,
            "span",
            "",
            job.location || "Location not specified"
        );

        addText(
            meta,
            "span",
            "",
            formatDate(job.posted_at)
        );

        addText(
            meta,
            "span",
            "",
            (job.employment_type || "Not specified").replaceAll("_", " ")
        );

        card.appendChild(meta);

        addText(
            card,
            "p",
            "job-description",
            getShortDescription(job.description)
        );

        const skillsContainer = document.createElement("div");
        skillsContainer.className = "skills";

        if (job.skills && job.skills.length) {

            job.skills.slice(0, 5).forEach(skill => {
                addText(
                    skillsContainer,
                    "span",
                    "skill-badge",
                    skill
                );
            });

        } else {

            addText(
                skillsContainer,
                "span",
                "skill-badge",
                "Skills not detected"
            );
        }

        card.appendChild(skillsContainer);

        addText(
            card,
            "p",
            "job-salary",
            formatSalary(job)
        );

        const footer = document.createElement("div");
        footer.className = "job-footer";

        addText(
            footer,
            "span",
            "source-label",
            getSourceName(job.source)
        );

        const link = document.createElement("a");

        link.className = "view-job";
        link.textContent = "View Details";

        if (job.id !== undefined && job.id !== null) {

            link.href = `/jobs/${encodeURIComponent(job.id)}/`;

        } else {

            link.textContent = "Details unavailable";
            link.classList.add("disabled");
            link.setAttribute("aria-disabled", "true");
        }

        footer.appendChild(link);
        card.appendChild(footer);

        return card;
    }

    function showEmptyState(message) {

        jobGrid.replaceChildren();

        const box = document.createElement("div");
        box.className = "empty-state";

        addText(box, "h3", "", message);

        addText(
            box,
            "p",
            "",
            "Try changing your search or filters."
        );

        jobGrid.appendChild(box);
    }

    async function loadJobs(page = 1) {

        currentPage = page;

        jobGrid.replaceChildren();

        status.textContent = "Loading job postings...";

        try {

            const params = getFilters(page);

            const response = await fetch(
                `/api/jobs/?${params.toString()}`,
                {
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            const jobs = data.results || [];

            totalPages = data.total_pages || 1;

            resultsInfo.textContent =
                `${data.total_count} matching job postings found`;

            pageInfo.textContent =
                `Page ${data.current_page} of ${totalPages}`;

            previousButton.disabled = data.current_page <= 1;

            nextButton.disabled = data.current_page >= totalPages;

            const browserParams = new URLSearchParams(
                params.toString()
            );

            browserParams.delete("page_size");

            window.history.replaceState(
                {},
                "",
                `${window.location.pathname}?${browserParams}`
            );

            if (!jobs.length) {

                showEmptyState("No matching jobs found.");

            } else {

                jobs.forEach(job => {
                    jobGrid.appendChild(createJobCard(job));
                });
            }

            status.textContent = "Job listings loaded successfully.";

        } catch (error) {

            console.error("TracBee Jobs API error:", error);

            status.textContent =
                "Unable to load jobs. Please try again.";

            showEmptyState("Something went wrong.");

            resultsInfo.textContent =
                "Job listings are currently unavailable.";
        }
    }

    form.addEventListener("submit", function (event) {

        event.preventDefault();

        loadJobs(1);
    });

    clearButton.addEventListener("click", function () {

        form.reset();

        loadJobs(1);
    });

    previousButton.addEventListener("click", function () {

        if (currentPage > 1) {
            loadJobs(currentPage - 1);
        }
    });

    nextButton.addEventListener("click", function () {

        if (currentPage < totalPages) {
            loadJobs(currentPage + 1);
        }
    });

    loadJobs(1);

});
