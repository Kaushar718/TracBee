document.addEventListener("DOMContentLoaded", function () {

 new Chart(document.getElementById("trendChart"), {
  type: "line",
  data: {
    labels: ["2022","2023","2024","2025","2026"],
    datasets: [{
      label: "Demand Growth",
      data: trendData,
      borderColor: "#23c36a",
      backgroundColor: "rgba(35,195,106,0.15)",
      fill: true,
      tension: 0.4,
      pointRadius: 5
    }]
  },
  options: {
    plugins: {
      legend: { labels: { color: "#fff" } }
    },
    scales: {
      x: { ticks: { color: "#94a3b8" } },
      y: { ticks: { color: "#94a3b8" } }
    }
  }
  });

  const container = document.getElementById("heatmapContainer");
  

  Object.entries(cityData).forEach(([city, value]) => {
    const box = document.createElement("div");
    box.classList.add("heatmap-box");
    box.style.background = `rgba(250,204,21,${value/100})`;
    box.innerHTML = `<h4>${city}</h4><p>${value}</p>`;
    container.appendChild(box);
  });

});
 