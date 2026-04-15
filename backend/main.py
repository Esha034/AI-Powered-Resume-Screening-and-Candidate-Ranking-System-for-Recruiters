from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import shutil
import os
import pdfplumber
from docx import Document
import re

from sentence_transformers import SentenceTransformer, util

# -------------------------------
# INIT
# -------------------------------
app = FastAPI(
    title="AI Resume Analyzer API",
    description="Analyze resumes against job descriptions using AI",
    version="1.0.0",
)

# CORS — allow frontend origins
# In production, replace "*" with your actual Render static site URL
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "*"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the sentence-transformer model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

UPLOAD_DIR = "temp_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

stored_files: dict[str, str] = {}


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def extract_text(file_path: str) -> str:
    """Extract text from PDF or DOCX files."""
    try:
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                return " ".join(
                    page.extract_text() for page in pdf.pages if page.extract_text()
                )
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return " ".join(para.text for para in doc.paragraphs)
    except Exception:
        return ""
    return ""


def clean_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str) -> list[str]:
    """Extract unique keywords (length > 2) from text."""
    words = text.split()
    return list({w for w in words if len(w) > 2})


def skill_score(jd_keywords: list[str], res_keywords: list[str]) -> float:
    """Calculate keyword overlap score."""
    if not jd_keywords:
        return 0
    matched = len(set(jd_keywords) & set(res_keywords))
    return (matched / len(jd_keywords)) * 100


def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    """Split text into chunks for semantic matching."""
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def calculate_score(jd: str, resume: str) -> float:
    """Calculate semantic similarity score using sentence-transformers."""
    jd_embedding = model.encode(jd, convert_to_tensor=True)

    chunks = chunk_text(resume, 200)
    if not chunks:
        return 0

    scores = []
    for chunk in chunks:
        resume_embedding = model.encode(chunk, convert_to_tensor=True)
        score = util.cos_sim(jd_embedding, resume_embedding).item()
        scores.append(score)

    return round(max(scores, default=0) * 100, 2)


def project_score(text: str) -> int:
    """Score based on project-related keywords."""
    words = ["project", "developed", "built", "created", "implemented"]
    count = sum(text.count(w) for w in words)
    if count >= 5:
        return 100
    if count >= 3:
        return 70
    if count >= 1:
        return 40
    return 10


def experience_score(text: str) -> int:
    """Score based on years of experience mentioned."""
    matches = re.findall(r"(\d+)\s+year", text)
    if matches:
        return min(int(max(matches)) * 20, 100)
    return 20


# -------------------------------
# API ENDPOINTS
# -------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint for Render."""
    return {"status": "ok"}


@app.get("/view/{filename}")
def view_resume(filename: str):
    """Serve a previously uploaded resume file."""
    path = stored_files.get(filename)
    if path and os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error": "File not found"}, status_code=404)


@app.post("/analyze")
async def analyze(jd: str = Form(...), file: UploadFile = File(...)):
    """
    Analyze resumes in a ZIP file against a job description.
    Returns ranked results with composite scores.
    """
    global stored_files
    stored_files = {}

    # Clear old files
    for f in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, f)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    if not file.filename or not file.filename.endswith(".zip"):
        return JSONResponse(
            {"error": "Please upload a ZIP file containing resumes."},
            status_code=400,
        )

    zip_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(UPLOAD_DIR)

    jd_text = clean_text(jd)
    jd_keywords = extract_keywords(jd_text)

    results = []

    for root, _, files in os.walk(UPLOAD_DIR):
        for filename in files:
            if not filename.endswith((".pdf", ".docx")):
                continue

            path = os.path.join(root, filename)
            stored_files[filename] = path

            resume_text = clean_text(extract_text(path))
            if not resume_text:
                continue

            semantic = calculate_score(jd_text, resume_text)
            res_keywords = extract_keywords(resume_text)
            skills = skill_score(jd_keywords, res_keywords)
            proj = project_score(resume_text)
            exp = experience_score(resume_text)

            final_score = (
                0.4 * semantic + 0.3 * skills + 0.2 * proj + 0.1 * exp
            )

            results.append({
                "name": filename,
                "score": round(final_score, 2),
                "semantic": semantic,
                "skills": round(skills, 2),
                "project": proj,
                "experience": exp,
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {"results": results}


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
