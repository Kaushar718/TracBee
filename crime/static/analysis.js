
document.addEventListener("DOMContentLoaded", async function () {

    const getElement = (id) => document.getElementById(id);

    const params = new URLSearchParams(window.location.search);

    const requestedSkill = (params.get("skill") || "").trim();
    const requestedYear = (params.get("year") || "").trim();
    const requestedLocation = (params.get("location") || "").trim();

    getElement("skillFilter").value = requestedSkill;
    getElement("yearFilter").value = requestedYear;
    getElement("locationFilter").value = requestedLocation;

    function cleanFilter(value) {
        if (!value) return "";

        const normalized = value.toLowerCase();

        if (
            normalized === "all" ||
            normalized === "any" ||
            normalized.startsWith("any ") ||
            normalized.startsWith("all ")
        ) {
            return "";
        }

        return value;
    }

    const locationFilter = cleanFilter(requestedLocation);
    const yearFilter = cleanFilter(requestedYear);

    getElement("skillName").textContent =
        requestedSkill || "All skills";

    getElement("yearName").textContent =
        yearFilter || "All years";

    getElement("locationName").textContent =
        locationFilter || "All locations";

    const queryParams = new URLSearchParams();

    // Support the Bangalore / Bengaluru naming difference
    if (locationFilter) {
        const apiLocation =
            locationFilter.toLowerCase() === "bangalore"
                ? "Bengaluru"
                : locationFilter;

        queryParams.set("location", apiLocation);
    }

    if (yearFilter) {
        queryParams.set("year", yearFilter);
    }

    const apiURL =
        "/api/skills/demand/" +
        (queryParams.toString() ? `?${queryParams}` : "");

    let demandChart = null;

    try {

        const response = await fetch(apiURL);

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const result = await response.json();

        const skills = result.skills || [];

        const totalJobs = result.total_jobs || 0;

        const selectedSkill = requestedSkill
            ? skills.find(
                item =>
                    item.skill.toLowerCase() ===
                    requestedSkill.toLowerCase()
            )
            : skills[0];

        const topSkill = skills[0];

        // ================= KPI CARDS =================

        getElement("totalJobs").textContent = totalJobs;

        getElement("totalSkills").textContent = skills.length;

        getElement("focusSkillLabel").textContent =
            requestedSkill
                ? `${requestedSkill} Job Postings`
                : "Top Skill Job Postings";

        getElement("focusSkillJobs").textContent =
            selectedSkill ? selectedSkill.job_count : 0;

        getElement("topSkill").textContent =
            topSkill ? topSkill.skill : "No data";

        getElement("topSkillCount").textContent =
            topSkill
                ? `${topSkill.job_count} matching job postings`
                : "No matching jobs";

        // ================= SKILL BREAKDOWN =================

        const skillList = getElement("skillDemandList");
        skillList.replaceChildren();

        if (skills.length === 0) {

            const emptyItem = document.createElement("li");
            emptyItem.textContent = "No matching skills found.";
            skillList.appendChild(emptyItem);

        } else {

            skills.forEach(item => {

                const li = document.createElement("li");

                const name = document.createElement("strong");
                name.textContent = item.skill;

                const details = document.createElement("span");

                details.textContent =
                    `${item.job_count} jobs · ${item.demand_percentage}%`;

                li.appendChild(name);
                li.appendChild(details);

                skillList.appendChild(li);

            });
        }

        // ================= DYNAMIC CHART =================

        const canvas = getElement("trendChart");

        if (demandChart) {
            demandChart.destroy();
        }

        demandChart = new Chart(canvas, {
            type: "bar",

            data: {
                labels: skills.map(item => item.skill),

                datasets: [{
                    label: "Number of Job Postings",

                    data: skills.map(item => item.job_count),

                    backgroundColor: "#6366f1",

                    borderRadius: 7
                }]
            },

            options: {
                responsive: true,

                maintainAspectRatio: true,

                plugins: {
                    legend: {
                        display: true
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });

        // ================= KEY INSIGHTS =================

        const insightsList = getElement("insightsList");
        insightsList.replaceChildren();

        function addInsight(message) {
            const li = document.createElement("li");
            li.textContent = message;
            insightsList.appendChild(li);
        }

        if (totalJobs === 0) {

            addInsight("No job postings match the selected filters.");

        } else {

            if (topSkill) {
                addInsight(
                    `${topSkill.skill} is the most frequently requested skill in this sample, appearing in ${topSkill.job_count} of ${totalJobs} matching jobs (${topSkill.demand_percentage}%).`
                );
            }

            addInsight(
                `${skills.length} distinct skills were found across ${totalJobs} matching job postings.`
            );

            if (requestedSkill) {

                if (selectedSkill) {
                    addInsight(
                        `${requestedSkill} appears in ${selectedSkill.job_count} matching job postings.`
                    );
                } else {
                    addInsight(
                        `No matching records were found for ${requestedSkill}.`
                    );
                }
            }
        }

       getElement("dataNotice").textContent =
    "Showing " +
    (result.total_jobs === 0
        ? "no matching records."
        : "job postings from the selected dataset."); 

        getElement("analysisStatus").textContent =
            "Analytics loaded successfully.";

    } catch (error) {

        console.error("TracBee API Error:", error);

        getElement("analysisStatus").textContent =
            "Unable to load analytics. Please check the API and try again.";

    }

});

// ================= EXPORT REPORT =================

const exportButton = document.getElementById("exportBtn");

if (exportButton) {
    exportButton.addEventListener("click", function () {
        window.print();
    });
}
