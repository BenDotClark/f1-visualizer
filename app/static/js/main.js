// main.js

// ============================
// Team Logo and Color Maps
// ============================

// Mapping constructor names to logo filenames used in /static/img/teams/
const teamLogoMap = {
  "Red Bull": "red-bull-racing-logo.png",
  "McLaren": "mclaren-logo.png",
  "Ferrari": "ferrari-logo.png",
  "Mercedes": "mercedes-logo.png",
  "Aston Martin": "aston-martin-logo.png",
  "Williams": "williams-logo.png",
  "Haas F1 Team": "haas-logo.png",
  "Alpine F1 Team": "alpine-logo.png",
  "Sauber": "kick-sauber-logo.png",
  "RB F1 Team": "racing-bulls-logo.png"
};

// Map official team colors
const teamColorMap = {
  "Mercedes": "#00D7B6",
  "Red Bull": "#4781D7",
  "Red Bull Racing": "#4781D7",
  "Ferrari": "#ED1131",
  "McLaren": "#F47600",
  "Alpine": "#00A1E8",
  "Racing Bulls": "#6C98FF",
  "Aston Martin": "#229971",
  "Williams": "#1868DB",
  "Kick Sauber": "#01C00E",
  "Sauber": "#01C00E",
  "Haas F1 Team": "#9C9FA2",
  "Haas": "#9C9FA2"
};

// ============================
// Spotlight Toggle Loader
// ============================

// Supports toggling between drivers/constructors
function loadSpotlight(type) {
  const container = document.getElementById("spotlightContainer");

  // Toggle button state
  document.getElementById("toggleDrivers").classList.toggle("active", type === "drivers");
  document.getElementById("toggleConstructors").classList.toggle("active", type === "constructors");

  container.innerHTML = `<p>Loading ${type}...</p>`;

  const url = type === "drivers" ? "/api/driver-spotlight" : "/api/constructor-spotlight";

  fetch(url)
    .then(res => res.json())
    .then(data => {
      container.innerHTML = "";
      data.forEach((entry, i) => {
        const cardHTML = type === "drivers"
          ? renderDriverCard(entry, i + 1)
          : renderConstructorCard(entry, i + 1);
        container.insertAdjacentHTML("beforeend", cardHTML);
      });
    })
    .catch(() => {
      container.innerHTML = `<p class="text-danger">Failed to load ${type} data.</p>`;
    });
}

// ============================
// Spotlight Card Renderers
// ============================

// New renderDriverCard() and renderConstructorCard() functions to modularize card generation
function renderDriverCard(driver, rank) {
  const teamLogo = teamLogoMap[driver.constructor] || "";
  return `
    <div class="driver-card">
      <div class="rank">P${rank}</div>
      <img src="/static/img/drivers/${driver.driverID}.png" class="driver-img" alt="${driver.name}">
      <div class="info">
        <h4 class="driver-code">${driver.name.split(" ").pop()}</h4>
        <p class="points">${driver.points} pts</p>
        <p class="team">${driver.constructor}</p>
      </div>
      <img src="/static/img/teams/${teamLogo}" class="team-logo" alt="${driver.constructor}">
    </div>
  `;
}

function renderConstructorCard(team, rank) {
  return `
    <div class="driver-card">
      <div class="rank">P${rank}</div>
      <img src="/static/img/teams/${team.logo}" class="driver-img" alt="${team.name}">
      <div class="info">
        <h4 class="driver-code">${team.name}</h4>
        <p class="points">${team.points} pts</p>
        <p class="team">🏆 ${team.wins} wins</p>
      </div>
    </div>
  `;
}
  
// ============================
// Race Table Results
// ============================

//Fetch latest race results and populate the table.
function loadLatestResults() {
  fetch("/api/latest-results")
    .then(res => res.json())
    .then(data => {
      const tableBody = document.getElementById("raceResults");
      const gpTitle = document.getElementById("grandPrixName");
      tableBody.innerHTML = ""; // Clear placeholder rows

      // Update the race title
      gpTitle.textContent = data.grandPrix || "Latest Grand Prix";

      // Handle unexpected response
      if (!Array.isArray(data.results) || data.results.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4">No race results available.</td></tr>`;
        return;
      }
  
      // Populate each result row
      data.results.forEach(result => {
        const constructorName = result.constructor;
        const logoFile = teamLogoMap[constructorName];
        const driverCode = result.code || "";
        // Determine status-based styling for time column
        const timeClass = result.time.includes("DNF")
          ? "result-dnf"
          : result.time.includes("Lap")
          ? "result-lap"
          : "";

        /**
        * Render a single race result row into the table.
        * Uses team logo and styles based on status (DNF, +Laps, etc.)
        */
        const rowHTML = `
          <tr>
            <td>${result.position}</td>
            <td class="driver-cell" title="${constructorName}">
              <div class="driver-name-wrapper">
                ${logoFile ? `<img src="/static/img/teams/${logoFile}" alt="${constructorName}" class="logo-icon">` : ""}
                <span class="fw-bold">${result.code}</span>
                <small class="constructor-name">${constructorName}</small>
              </div>
            </td>
            <td class="time-cell ${result.time.includes('DNF') ? 'result-dnf' : result.time.includes('Lap') ? 'result-lap' : ''}">
              ${result.time}
            </td>
          </tr>`;

        tableBody.appendChild(createElementFromHTML(rowHTML));
      });
    })
    .catch(err => {
      console.error("Failed to load latest race results:", err);
      const tableBody = document.getElementById("raceResults");
      tableBody.innerHTML = `<tr><td colspan="4">Unable to load data.</td></tr>`;
    });
}

// ============================
// Initialization
// ============================

// Initialize data loading after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  loadLatestResults();
  loadSpotlight("drivers");

  document.getElementById("toggleDrivers").addEventListener("click", () => {
    loadSpotlight("drivers");
  });
  document.getElementById("toggleConstructors").addEventListener("click", () => {
    loadSpotlight("constructors");
  });
});

// ============================
// Utility
// ============================

// Helper: Create DOM element from HTML string
function createElementFromHTML(htmlString) {
  const template = document.createElement("template");
  template.innerHTML = htmlString.trim();
  return template.content.firstChild;
}