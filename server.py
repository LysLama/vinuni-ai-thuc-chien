"""
FastAPI Server for VinUni - Vingroup AI Thuc Chien Exam Practice Web Application.
Provides RESTful API for question banks, mock exam generation, grading, and serves the static frontend.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Enable CORS for local development
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


@app.get("/api/stats")
def get_stats():
    """Returns question bank statistics."""
    return get_bank_statistics()


@app.get("/api/questions")
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
def get_history():
    """Returns history of mock exam attempts."""
    return {"history": load_history()}


@app.get("/api/docs/{doc_name}")
def get_document(doc_name: str):
    """Fetches markdown content of study guides."""
    docs_dir = ROOT_DIR / "docs"
    safe_name = Path(doc_name).name
    if not safe_name.endswith(".md"):
        safe_name += ".md"

    file_path = docs_dir / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"name": safe_name, "content": content}


# Mount static files at root
STATIC_DIR = ROOT_DIR / "web"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("  🚀 VINUNI AI THỰC CHIẾN - EXAM PLATFORM WEB SERVER")
    print("  Truy cập hệ thống luyện thi tại: http://localhost:8000")
    print("=" * 70 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
