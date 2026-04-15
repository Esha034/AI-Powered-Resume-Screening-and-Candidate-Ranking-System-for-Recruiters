# Resulyze: AI Powered Resume Analyzer

Welcome to Resulyze! This project is an intelligent web application designed to make the hiring and screening process incredibly fast and efficient. If you have a stack of resumes in a ZIP file and a specific job description, Resulyze will review them all, score them using advanced AI, and give you a beautiful dashboard showing exactly who your top candidates are.

## What is this project?

Resulyze takes the manual headache out of screening resumes. Instead of reading through dozens of documents to see if a candidate mentioned specific skills, the system uses natural language processing to truly understand the context of both the job description and the resumes. It then ranks the candidates based on how well their experience aligns with what you are looking for.

## Key Features

* **Automated Bulk Parsing:** Upload a single ZIP file containing multiple PDF or DOCX resumes. The backend handles extracting and processing them all at once.
* **Intelligent AI Matching:** Uses powerful sentence transformers to calculate how closely a candidate's experience, skills, and projects align with the actual job responsibilities.
* **Detailed Score Breakdown:** It does not just give a random overall number. You get specific sub-scores for Semantic Match, Skills, Projects, and Experience.
* **Live Document Preview:** The UI displays a crisp, scaled down visual glimpse of the actual PDF directly on the candidate card. No need to download files just to peek at them.
* **Premium Interface:** A modern, soft pastel dashboard that feels like a refined, enterprise ready product.

## Tech Stack

* **Frontend:** HTML5, Vanilla CSS (Glassmorphism design), JavaScript.
* **Backend:** Python 3, FastAPI (REST API), Uvicorn.
* **Machine Learning & AI:** `sentence-transformers` (`all-MiniLM-L6-v2`), PyTorch.
* **Document Parsing:** `pdfplumber` (for PDFs), `python-docx` (for Word documents).

## Scoring Mechanism

The final candidate ranking is a composite score calculated using four distinct weighted metrics:

1. **Semantic Match (40% Weight):** Uses advanced natural language processing (`sentence-transformers`) to convert both the job description and the resume into mathematical vectors, then calculates the cosine similarity. This measures the true context and relevance of the resume.
2. **Skills Match (30% Weight):** Calculates the exact keyword overlap percentage between the job description and the resume.
3. **Project & Action Orientation (20% Weight):** Scans for action verbs (e.g. "developed", "built", "implemented") to gauge how hands-on the candidate's experience is.
4. **Experience Level (10% Weight):** Extracts quantitative mentions of years of experience using regular expressions to approximate seniority.

## Project Workflow or Architecture

The workflow is simple but highly effective. 

1. You upload your ZIP archive of resumes and type out your job description into the web interface.
2. The frontend sends this data to the FastAPI backend.
3. The backend extracts the ZIP file in a secure temporary directory. Next, it reads the text from every PDF and DOCX file using python libraries like pdfplumber.
4. An open source language model transforms both the job description and the resume text into mathematical vectors. 
5. It then measures the cosine similarity between these vectors. A higher textual similarity means the resume is a much better match for the role.
6. The backend calculates the final composite score based on semantics, skills, projects, and exact experience.
7. The backend packages these scores and rankings, sending them back to the frontend which renders the dashboard complete with live thumbnails and animated progress rings.

## Project Structure and Modules

The project is intentionally decoupled into two distinct parts to make development and cloud deployment completely straightforward.

### 1. The Backend Module
This is the brain of the application. It is a REST API built uniquely with FastAPI for speed.
* **main.py:** Contains all the logic for the API endpoints, file extraction, directory cleanup, text parsing, and the AI scoring algorithm.
* **requirements.txt:** Manages all the heavy lifting Machine Learning libraries like torch, sentence-transformers, and FastAPI.
* **Dockerfile:** Configured specifically so the backend can easily be deployed on free container platforms like Hugging Face Spaces via a non-root user setup.

### 2. The Frontend Module
This is the web user interface. It is built entirely with vanilla web technologies (HTML, CSS, JavaScript) so it is blazing fast and requires zero complex build steps.
* **index.html:** The structural layout of the dashboard, form elements, and tracking grid.
* **style.css:** All the beautiful visual flair. It handles the soft mesh gradients, glassmorphic cards, typography, and the tricky iframe scaling for thumbnail previews.
* **script.js:** Manages browser side interactions like drag and drop, sends the API requests, and dynamically stamps out the result cards once data comes back.

## Setting Up the Project Locally

To test Resulyze cleanly on your own machine, you will want to run the backend and the frontend separately. We recommend using `uv` for python dependency management because it is incredibly fast.

### Running the Backend

1. Open your terminal and navigate to the `backend` folder.
2. Create and activate a virtual environment:
   ```bash
   uv venv
   # On Windows:
   .venv\Scripts\activate
   # On Mac/Linux:
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
The backend API will now be listening eagerly on `http://localhost:8000`.

### Running the Frontend

Since the frontend is composed of standard web files, you can use any straightforward web server to load it. If you use VS Code, simply right click the `index.html` file inside the `frontend` folder and use the "Live Server" extension.

Alternatively, you can just use Python to serve the folder:
1. Open a new terminal and navigate to the `frontend` folder.
2. Run the simple HTTP server:
   ```bash
   python -m http.server 5500
   ```
Visit `http://localhost:5500` in your web browser and you will be greeted by the Resulyze dashboard!

## Deployment Guide

If you want to put this project live on the internet, the decoupled architecture makes it easy.

1. **Backend Hosting:** Because the AI libraries require high processing power and RAM, the simplest place to host the `backend` folder for free is on **Hugging Face Spaces (Docker SDK)**. They grant you up to 16GB of RAM. You simply upload your backend files and the provided Dockerfile will build the container.
2. **Frontend Hosting:** Since the frontend is static HTML, you can deploy the `frontend` folder anywhere in seconds. Services like **Netlify, Vercel, or GitHub Pages** work perfectly and for free. Once deployed, just update your `script.js` to point `API_BASE_URL` to your new live Hugging Face URL.
