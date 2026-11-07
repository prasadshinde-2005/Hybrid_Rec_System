const API_URL = "http://localhost:8000";

const songInput       = document.getElementById("songName");
const artistInput     = document.getElementById("artistName");
const kSelect         = document.getElementById("k");
const diversitySlider = document.getElementById("diversity");
const diversityField  = document.getElementById("diversityField");
const diversityValue  = document.getElementById("diversityValue");
const barPersonalized = document.getElementById("barPersonalized");
const barDiverse      = document.getElementById("barDiverse");
const recommendBtn    = document.getElementById("recommendBtn");
const statusDiv       = document.getElementById("status");
const resultsDiv      = document.getElementById("results");

/* =========================================================
   1. Floating Music Notes (Background)
   ========================================================= */
(function createMusicNotes() {
  const notesContainer = document.getElementById("musicNotes");
  if (!notesContainer) return;
  const symbols = ["♪", "♫", "♬", "🎵", "🎶"];
  for (let i = 0; i < 15; i++) {
    const note = document.createElement("div");
    note.className = "note";
    note.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    note.style.left = Math.random() * 100 + "%";
    note.style.fontSize = (16 + Math.random() * 20) + "px";
    note.style.animationDuration = (10 + Math.random() * 15) + "s";
    note.style.animationDelay = (Math.random() * 10) + "s";
    notesContainer.appendChild(note);
  }
})();

/* =========================================================
   2. Diversity Slider
   ========================================================= */
function updateDiversityBars() {
  const d = parseInt(diversitySlider.value, 10);
  diversityValue.textContent = d;
  const personalizedPct = (10 - d) * 10;
  const diversePct      = d * 10;
  barPersonalized.style.width = personalizedPct + "%";
  barDiverse.style.width      = diversePct + "%";
  barPersonalized.textContent = personalizedPct ? personalizedPct + "%" : "";
  barDiverse.textContent      = diversePct ? diversePct + "%" : "";
}

diversitySlider.addEventListener("input", updateDiversityBars);
updateDiversityBars();

/* =========================================================
   3. Status Helper
   ========================================================= */
function setStatus(type, message) {
  statusDiv.className = type;
  statusDiv.textContent = message;
  statusDiv.style.display = message ? "block" : "none";
}

/* =========================================================
   4. Render Recommendations
   ========================================================= */
function renderRecommendations(engine, recommendations) {
  resultsDiv.innerHTML = "";

  if (!recommendations || recommendations.length === 0) {
    setStatus("error", "No recommendations found.");
    return;
  }

  /* ---- Currently Playing (first song) ---- */
  const firstSong = recommendations[0];
  const currentSection = document.createElement("div");
  currentSection.className = "currently-playing-section";

  const audioHtmlCurrent = firstSong.spotify_preview_url
    ? `<audio controls preload="none" src="${firstSong.spotify_preview_url}"></audio>`
    : `<span style="opacity:0.6;font-size:13px;display:block;margin-top:12px;">No preview available</span>`;

  currentSection.innerHTML = `
    <div class="album-art playing">🎵</div>
    <div class="current-info">
      <div class="section-title">
        Currently Playing
        <span class="equalizer">
          <span></span><span></span><span></span><span></span>
        </span>
      </div>
      <strong>${firstSong.name}</strong>
      <span>by ${firstSong.artist}</span>
      ${audioHtmlCurrent}
    </div>
  `;
  resultsDiv.appendChild(currentSection);

  /* ---- Up Next (rest of songs) ---- */
  if (recommendations.length > 1) {
    const upNextSection = document.createElement("div");
    upNextSection.className = "up-next-section";

    const nextTitle = document.createElement("div");
    nextTitle.className = "section-title";
    nextTitle.innerHTML = `Up Next 🎵`;
    upNextSection.appendChild(nextTitle);

    recommendations.slice(1).forEach((song, idx) => {
      const pos = idx + 2;
      const card = document.createElement("div");
      card.className = "song-card";
      card.style.animationDelay = (idx * 0.06) + "s";

      const audioHtml = song.spotify_preview_url
        ? `<audio controls preload="none" src="${song.spotify_preview_url}"></audio>`
        : `<span style="opacity:0.6;font-size:13px;">No preview</span>`;

      card.innerHTML = `
        <span class="song-number">${pos}</span>
        <div class="song-info">
          <strong>${song.name}</strong>
          <span>by ${song.artist}</span>
        </div>
        ${audioHtml}
      `;

      upNextSection.appendChild(card);
    });

    resultsDiv.appendChild(upNextSection);
  }
}

/* =========================================================
   5. Button Click
   ========================================================= */
recommendBtn.addEventListener("click", async () => {
  const song_name  = songInput.value.trim();
  const artist_name = artistInput.value.trim();
  const k          = parseInt(kSelect.value, 10);
  const diversity  = parseInt(diversitySlider.value, 10);

  if (!song_name || !artist_name) {
    setStatus("info", "Please enter both song name and artist name.");
    return;
  }

  recommendBtn.disabled = true;
  setStatus("info", "Loading recommendations...");

  /* Skeleton loader */
  resultsDiv.innerHTML = `
    <div class="skeleton-container">
      <div class="skeleton" style="height:120px;"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
    </div>
  `;

  try {
    const response = await fetch(`${API_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ song_name, artist_name, k, diversity }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || "Something went wrong.");
    }

    /* Show diversity chart only for hybrid engine */
    if (data.engine === "hybrid") {
      diversityField.style.display = "flex";
      updateDiversityBars();
    } else {
      diversityField.style.display = "none";
    }

    setStatus(
      "success",
      `Found ${data.recommendations.length} recommendations using ${data.engine} filtering.`
    );
    renderRecommendations(data.engine, data.recommendations);
  } catch (err) {
    setStatus("error", err.message);
    resultsDiv.innerHTML = "";
  } finally {
    recommendBtn.disabled = false;
  }
});