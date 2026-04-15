// script.js
const API_BASE_URL = "https://esha03-ai-resume-analyzer-api.hf.space";

const jdInput = document.getElementById("jd-input");
const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzone-content");
const fileSelected = document.getElementById("file-selected");
const fileNameEl = document.getElementById("file-name");
const removeFileBtn = document.getElementById("remove-file");
const analyzeBtn = document.getElementById("analyze-btn");
const loader = document.getElementById("loader");
const errorSection = document.getElementById("error-section");
const errorText = document.getElementById("error-text");
const resultsSection = document.getElementById("results-section");
const resultsGrid = document.getElementById("results-grid");
const resultsCount = document.getElementById("results-count");

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) showSelectedFile(fileInput.files[0].name);
});

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone--active");
});
dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dropzone--active");
});
dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone--active");
    if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        showSelectedFile(fileInput.files[0].name);
    }
});

removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.value = "";
    dropzoneContent.style.display = "block";
    fileSelected.style.display = "none";
});

function showSelectedFile(name) {
    dropzoneContent.style.display = "none";
    fileSelected.style.display = "flex";
    fileNameEl.textContent = name;
}

async function analyzeResumes() {
    const jd = jdInput.value.trim();
    if (!jd) return showError("Please enter a job description.");
    if (!fileInput.files || !fileInput.files[0]) return showError("Please upload a ZIP file.");

    hideError();
    resultsSection.style.display = "none";
    loader.style.display = "block";
    analyzeBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append("jd", jd);
        formData.append("file", fileInput.files[0]);

        const response = await fetch(`${API_BASE_URL}/analyze`, { method: "POST", body: formData });
        const data = await response.json();

        if (!response.ok || data.error) throw new Error(data.error || "Server error");
        if (!data.results?.length) throw new Error("No resumes found.");

        renderResults(data.results);
    } catch (err) {
        showError(err.message);
    } finally {
        loader.style.display = "none";
        analyzeBtn.disabled = false;
    }
}

function renderResults(results) {
    resultsGrid.innerHTML = "";
    resultsCount.textContent = `${results.length} resumes analyzed`;

    results.forEach((item, i) => {
        // High score: gradient from pink to blue/green. We'll use a clean primary if >= 50, else red.
        let scoreColor = "var(--primary)"; // default
        if (item.score >= 80) scoreColor = "#10b981"; // Emerald
        else if (item.score >= 40) scoreColor = "#f59e0b"; // Amber
        else scoreColor = "#ef4444"; // Red

        const gradient = `conic-gradient(${scoreColor} ${item.score}%, #e2e8f0 0)`;
        
        let subTitle = "Low Match";
        if (item.score >= 80) subTitle = "High Priority Candidate";
        else if (item.score >= 40) subTitle = "Needs Review";

        resultsGrid.innerHTML += `
            <a href="${API_BASE_URL}/view/${encodeURIComponent(item.name)}" target="_blank" class="new-card" style="animation: slideUp 0.4s ease forwards; animation-delay: ${i*0.1}s; opacity: 0; transform: translateY(20px);">
                <div class="new-card-header">
                    <div class="new-card-info">
                        <h3 class="new-card-title" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</h3>
                        <p class="new-card-subtitle">${subTitle}</p>
                    </div>
                    <div class="score-circle" style="background: ${gradient}">
                        <span class="score-circle-val">${item.score}/100</span>
                        <span class="score-circle-lbl">Score</span>
                    </div>
                </div>
                <div class="resume-preview">
                    ${item.name.toLowerCase().endsWith('.pdf') ? `
                        <iframe src="${API_BASE_URL}/view/${encodeURIComponent(item.name)}#toolbar=0&navpanes=0&scrollbar=0" class="resume-iframe" scrolling="no" tabindex="-1"></iframe>
                    ` : `
                        <div class="resume-paper">
                            <div class="sk-row">
                                <div class="sk-avatar"></div>
                                <div class="sk-lines">
                                    <div class="sk-line sk-w-40"></div>
                                    <div class="sk-line sk-w-30"></div>
                                </div>
                            </div>
                            <div class="sk-body">
                                <div class="sk-line sk-w-100"></div>
                                <div class="sk-line sk-w-80"></div>
                                <div class="sk-line sk-w-60"></div>
                                <div class="sk-line sk-w-100" style="margin-top:15px;"></div>
                                <div class="sk-line sk-w-80"></div>
                                <div class="sk-line sk-w-100"></div>
                                <div class="sk-line sk-w-60"></div>
                            </div>
                        </div>
                    `}
                </div>
            </a>`;
    });
    
    resultsSection.style.display = "block";
    
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
}

function showError(msg) {
    errorText.textContent = msg;
    errorSection.style.display = "block";
}
function hideError() {
    errorSection.style.display = "none";
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
