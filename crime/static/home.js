
document.addEventListener("DOMContentLoaded", function () {

    const API_BASE = "";

    const skillSelect = document.getElementById("homeSkill");
    const locationSelect = document.getElementById("homeLocation");
    const yearSelect = document.getElementById("homeYear");

    const searchForm = document.getElementById("homeSearchForm");
    const findJobsButton = document.getElementById("findJobsBtn");
    const resetButton = document.getElementById("resetHomeSearch");

    const skillPreview = document.getElementById("heroSkillPreview");
    const recentJobsGrid = document.getElementById("recentJobsGrid");

    // ==================================
    // MOBILE NAVIGATION
    // ==================================

    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const navigation = document.getElementById("homeNavigation");

    mobileMenuBtn.addEventListener("click", function () {

        const isOpen = navigation.classList.toggle("open");

        mobileMenuBtn.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });


    // ==================================
    // API HELPER
    // ==================================

    async function fetchJSON(url) {

        const response = await fetch(API_BASE + url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        return await response.json();
    }


    function formatNumber(value) {

        return Number(value || 0).toLocaleString("en-IN");
    }


    // ==================================
    // SKILL DROPDOWN
    // ==================================

    function populateSkills(skills) {

        skillSelect.replaceChildren();

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "All skills";

        skillSelect.appendChild(defaultOption);

        skills.forEach(item => {

            const option = document.createElement("option");

            option.value = item.skill;
            option.textContent = item.skill;

            skillSelect.appendChild(option);

        });
    }


    // ==================================
    // SKILL PREVIEW
    // ==================================

    function createSkillPreview(skills) {

        skillPreview.replaceChildren();

        if (!skills.length) {

            const empty = document.createElement("p");
            empty.textContent = "No skill information available.";
            empty.className = "preview-loading";

            skillPreview.appendChild(empty);

            return;
        }

        const topSkills = skills.slice(0, 4);

        const maxCount = Math.max(
            ...topSkills.map(item => item.job_count),
            1
        );

        topSkills.forEach(item => {

            const row = document.createElement("div");
            row.className = "preview-skill-row";

            const header = document.createElement("div");
            header.className = "preview-skill-top";

            const name = document.createElement("span");
            name.textContent = item.skill;

            const count = document.createElement("span");
            count.textContent =
                `${formatNumber(item.job_count)} jobs`;

            header.appendChild(name);
            header.appendChild(count);

            const track = document.createElement("div");
            track.className = "preview-skill-track";

            const fill = document.createElement("div");
            fill.className = "preview-skill-fill";

            const width = Math.max(
                3,
                (item.job_count / maxCount) * 100
            );

            fill.style.width = `${width}%`;

            track.appendChild(fill);

            row.appendChild(header);
            row.appendChild(track);

            skillPreview.appendChild(row);
        });
    }


    // ==================================
    // LOAD ANALYTICS
    // ==================================

    async function loadAnalytics() {

        try {

            const result = await fetchJSON(
                "/api/skills/demand/"
            );

            const skills = result.skills || [];

            const jobs = result.total_jobs || 0;

            document.getElementById("heroJobCount")
                .textContent = formatNumber(jobs);

            document.getElementById("marketJobs")
                .textContent = formatNumber(jobs);

            document.getElementById("marketSkills")
                .textContent = formatNumber(skills.length);

            const topSkill = skills[0];

            document.getElementById("marketTopSkill")
                .textContent = topSkill
                    ? topSkill.skill
                    : "No data";

            document.getElementById("marketTopSkillDescription")
                .textContent = topSkill
                    ? `${topSkill.job_count} of ${jobs} matching jobs`
                    : "No skill data available";

            document.getElementById("marketDisclaimer")
                .textContent =
                    "Source: Configured public employer job boards. " +
                    "Counts are based on imported active records, " +
                    "not the entire Indian job market. " +
                    "Skill detection uses keyword matching.";

            populateSkills(skills);

            createSkillPreview(skills);

        } catch (error) {

            console.error("Analytics loading error:", error);

            document.getElementById("heroJobCount").textContent = "--";

            document.getElementById("marketJobs").textContent = "--";

            document.getElementById("marketSkills").textContent = "--";

            document.getElementById("marketTopSkill").textContent =
                "Unavailable";

            skillPreview.replaceChildren();

            const message = document.createElement("p");
            message.className = "preview-loading";
            message.textContent = "Unable to load market data.";

            skillPreview.appendChild(message);

            document.getElementById("marketDisclaimer")
                .textContent =
                    "Analytics service is currently unavailable.";
        }
    }


    // ==================================
    // RECENT JOBS
    // ==================================

    function sourceLabel(source) {

        if (source === "TracBee Demo Dataset") {
            return "Demo data";
        }

        if (source === "Greenhouse:gitlab") {
            return "GitLab";
        }

        if (
            source ===
            "Greenhouse:razorpaysoftwareprivatelimited"
        ) {
            return "Razorpay";
        }

        return source || "Unknown source";
    }


    function formatDate(value) {

        if (!value) return "Date unavailable";

        const date = new Date(value + "T00:00:00");

        if (Number.isNaN(date.getTime())) {
            return "Date unavailable";
        }

        return date.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    }


    function createRecentJob(job) {

        const card = document.createElement("article");

        card.className = "recent-job-card";

        const company = document.createElement("p");
        company.className = "recent-job-company";
        company.textContent = job.company;

        const title = document.createElement("h3");
        title.textContent = job.title;

        const location = document.createElement("p");
        location.className = "recent-job-location";
        location.textContent =
            `${job.location} · ${formatDate(job.posted_at)}`;

        const footer = document.createElement("div");
        footer.className = "recent-job-footer";

        const source = document.createElement("span");
        source.className = "recent-job-source";
        source.textContent = sourceLabel(job.source);

        const link = document.createElement("a");

        link.textContent = "View job →";

        try {

            const parsed = new URL(job.source_url);

            if (
                parsed.protocol === "https:" ||
                parsed.protocol === "http:"
            ) {

                link.href = parsed.href;
                link.target = "_blank";
                link.rel = "noopener noreferrer";

            } else {

                link.textContent = "No link";
            }

        } catch {

            link.textContent = "No link";
        }

        footer.appendChild(source);
        footer.appendChild(link);

        card.appendChild(company);
        card.appendChild(title);
        card.appendChild(location);
        card.appendChild(footer);

        return card;
    }


    async function loadRecentJobs() {

        try {

            const data = await fetchJSON(
                "/api/jobs/?page=1&page_size=3"
            );

            recentJobsGrid.replaceChildren();

            if (!data.results || !data.results.length) {

                const empty = document.createElement("div");
                empty.className = "recent-empty";
                empty.textContent = "No job postings available.";

                recentJobsGrid.appendChild(empty);

                return;
            }

            data.results.forEach(job => {

                recentJobsGrid.appendChild(
                    createRecentJob(job)
                );

            });

        } catch (error) {

            console.error("Recent jobs error:", error);

            recentJobsGrid.replaceChildren();

            const message = document.createElement("div");
            message.className = "recent-empty";
            message.textContent =
                "Unable to load recent job postings.";

            recentJobsGrid.appendChild(message);
        }
    }


    // ==================================
    // SEARCH NAVIGATION
    // ==================================

    function buildSearchURL(destination) {

        const params = new URLSearchParams();

        const skill = skillSelect.value;
        const location = locationSelect.value;
        const year = yearSelect.value;

        if (skill) params.set("skill", skill);

        if (location) params.set("location", location);

        if (year) params.set("year", year);

        const query = params.toString();

        return destination + (query ? `?${query}` : "");
    }


    searchForm.addEventListener("submit", function (event) {

        event.preventDefault();

        window.location.href = buildSearchURL("/analysis/");
    });


    findJobsButton.addEventListener("click", function () {

        window.location.href = buildSearchURL("/jobs/");
    });


    resetButton.addEventListener("click", function () {

        searchForm.reset();

    });


    // ==================================
    // INITIAL LOAD
    // ==================================

    loadAnalytics();

    loadRecentJobs();

});
