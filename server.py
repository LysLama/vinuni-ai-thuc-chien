"""
FastAPI Server for VinUni - Vingroup AI Thuc Chien Exam Practice Web Application.
Provides RESTful API for question banks, mock exam generation, grading, and serves the static frontend.
Compatible with standalone local execution, uvicorn, and Vercel serverless deployment.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

# Add src to system path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from exam_engine import (
    load_all_questions,
    get_bank_statistics,
    generate_mock_exam,
    grade_exam,
    load_history,
    MODULE_NAMES,
)

app = FastAPI(
    title="VinUni AI Thuc Chien Exam Platform API",
    description="Backend API for 240 Questions Mock Exam & Practice Platform",
    version="2.1.0",
)

# Enable CORS for local development & Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExamSubmission(BaseModel):
    questions: list
    answers: Dict[str, str]
    elapsed_seconds: float = 0


# --- API Routes (Supporting both /api/* and root-level aliases) ---

@app.get("/api/stats")
@app.get("/stats")
def get_stats():
    """Returns question bank statistics."""
    return get_bank_statistics()


@app.get("/api/questions")
@app.get("/questions")
def get_questions(module: Optional[str] = None, difficulty: Optional[str] = None):
    """Fetches questions optionally filtered by module and difficulty."""
    all_q = load_all_questions()
    result = []
    
    if module and module in all_q:
        result = all_q[module]
    else:
        for m in ["A", "B", "C", "D"]:
            result.extend(all_q.get(m, []))

    if difficulty and difficulty != "Tất cả":
        result = [q for q in result if q.get("difficulty") == difficulty]

    return {"count": len(result), "questions": result}


@app.post("/api/exam/generate")
@app.post("/exam/generate")
def create_exam(mode: str = Query("standard_100", enum=["standard_100", "module_practice", "all"]),
                module: Optional[str] = None,
                seed: Optional[int] = None):
    """Generates a randomized exam paper."""
    exam = generate_mock_exam(mode=mode, module_filter=module, seed=seed)
    return {
        "mode": mode,
        "module": module,
        "count": len(exam),
        "total_points": sum(q.get("points", 5) for q in exam),
        "questions": exam,
    }


@app.post("/api/exam/grade")
@app.post("/exam/grade")
def evaluate_exam(submission: ExamSubmission):
    """Evaluates exam answers and returns score, analytics, and explanations."""
    if not submission.questions:
        raise HTTPException(status_code=400, detail="Questions list cannot be empty")
    
    result = grade_exam(
        submission.questions,
        submission.answers,
        elapsed_seconds=submission.elapsed_seconds,
    )
    return result


@app.get("/api/history")
@app.get("/history")
def get_history():
    """Returns history of mock exam attempts."""
    return {"history": load_history()}


@app.get("/api/docs/{doc_name}")
@app.get("/docs/{doc_name}")
def get_document(doc_name: str):
    """Fetches markdown content of study guides."""
    safe_name = Path(doc_name).name
    if not safe_name.endswith(".md"):
        safe_name += ".md"

    for candidate_dir in [ROOT_DIR / "docs", ROOT_DIR / "web" / "docs", ROOT_DIR / "public" / "docs"]:
        file_path = candidate_dir / safe_name
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return {"name": safe_name, "content": f.read()}

    raise HTTPException(status_code=404, detail="Document not found")


# --- Root & Static Fallback Routes (Prevents {"detail":"Not Found"} on Vercel) ---

def find_index_file() -> Optional[Path]:
    for p in [
        ROOT_DIR / "web" / "index.html",
        ROOT_DIR / "public" / "index.html",
        ROOT_DIR / "index.html",
    ]:
        if p.is_file():
            return p
    return None


@app.get("/", response_class=HTMLResponse)
def get_root():
    """Serves the primary exam interface."""
    index_path = find_index_file()
    if index_path:
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>VinUni AI Thuc Chien Exam Platform</h1>")


@app.get("/{full_path:path}")
def get_static_or_spa(full_path: str):
    """Serves static assets or falls back to SPA index.html."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    for base in [ROOT_DIR / "web", ROOT_DIR / "public", ROOT_DIR]:
        target = base / full_path
        if target.is_file():
            return FileResponse(str(target))

    index_path = find_index_file()
    if index_path:
        return FileResponse(str(index_path))

    raise HTTPException(status_code=404, detail="File Not Found")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("  🚀 VINUNI AI THỰC CHIẾN - EXAM PLATFORM WEB SERVER")
    print("  Truy cập hệ thống luyện thi tại: http://localhost:8000")
    print("=" * 70 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
