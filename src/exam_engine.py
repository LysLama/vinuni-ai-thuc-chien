"""
Core Exam Engine for VinUni - Vingroup AI Thuc Chien Entrance Exam Preparation.
Handles question bank loading, random exam paper generation, scoring, analytics, and history tracking.
"""

import json
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = PROJECT_ROOT / "data" / "questions"
HISTORY_FILE = PROJECT_ROOT / "data" / "history.json"

MODULE_FILES = {
    "A": "module_a_toan_dinh_luong.json",
    "B": "module_b_lap_trinh_du_lieu.json",
    "C": "module_c_kien_thuc_san_pham_ai.json",
    "D": "module_d_logic_dao_duc_hanh_vi.json",
}

MODULE_NAMES = {
    "A": "Module A: Nền tảng Toán học & Tư duy Định lượng",
    "B": "Module B: Kỹ thuật Lập trình & Xử lý dữ liệu",
    "C": "Module C: Kiến thức AI & Tư duy sản phẩm AI",
    "D": "Module D: Tư duy Logic, Đạo đức & Hành vi",
}


def load_all_questions() -> Dict[str, List[Dict[str, Any]]]:
    """Loads all questions categorized by module."""
    data = {}
    for mod, filename in MODULE_FILES.items():
        file_path = QUESTIONS_DIR / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data[mod] = json.load(f)
        else:
            data[mod] = []
    return data


def get_bank_statistics() -> Dict[str, Any]:
    """Returns detailed statistics about the question bank."""
    all_data = load_all_questions()
    stats = {
        "total_questions": 0,
        "by_module": {},
        "by_type": {"multiple_choice": 0, "scenario": 0},
        "by_difficulty": {"Cơ bản": 0, "Trung bình": 0, "Nâng cao": 0},
    }
    for mod, q_list in all_data.items():
        stats["by_module"][mod] = {
            "name": MODULE_NAMES[mod],
            "count": len(q_list),
            "mc_count": sum(1 for q in q_list if q.get("type") == "multiple_choice"),
            "scenario_count": sum(1 for q in q_list if q.get("type") == "scenario"),
        }
        stats["total_questions"] += len(q_list)
        for q in q_list:
            q_type = q.get("type", "multiple_choice")
            stats["by_type"][q_type] = stats["by_type"].get(q_type, 0) + 1
            diff = q.get("difficulty", "Trung bình")
            stats["by_difficulty"][diff] = stats["by_difficulty"].get(diff, 0) + 1
    return stats


def generate_mock_exam(mode: str = "standard_100", module_filter: Optional[str] = None, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Generates an exam:
    - 'standard_100': Standard 90-minute, 100-point exam.
      Picks 5 questions per module (4 Multiple Choice + 1 Scenario) = 20 questions total.
      Each module has 25 points total.
    - 'module_practice': Takes questions exclusively from a single module.
    - 'all': Takes all questions in the bank.
    """
    if seed is not None:
        random.seed(seed)

    all_questions = load_all_questions()
    exam_questions = []

    if mode == "module_practice" and module_filter in MODULE_FILES:
        questions = list(all_questions.get(module_filter, []))
        random.shuffle(questions)
        return questions

    if mode == "all":
        for mod in ["A", "B", "C", "D"]:
            exam_questions.extend(all_questions.get(mod, []))
        return exam_questions

    # Standard 100-point Mock Exam
    # 4 Modules, each module gets 5 questions (e.g. 4 MC * 5 pts + 1 Scenario * 5 pts = 25 pts)
    for mod in ["A", "B", "C", "D"]:
        questions = all_questions.get(mod, [])
        mc_questions = [q for q in questions if q.get("type") == "multiple_choice"]
        sc_questions = [q for q in questions if q.get("type") == "scenario"]

        random.shuffle(mc_questions)
        random.shuffle(sc_questions)

        # Pick 4 MC questions and 1 Scenario question per module
        selected_mc = mc_questions[:4]
        selected_sc = sc_questions[:1] if sc_questions else mc_questions[4:5]

        combined = selected_mc + selected_sc
        # Standardize point values to 5 points each (5 questions * 5 points = 25 points per module)
        for item in combined:
            item_copy = dict(item)
            item_copy["points"] = 5
            exam_questions.append(item_copy)

    return exam_questions


def grade_exam(exam_questions: List[Dict[str, Any]], user_answers: Dict[str, str], elapsed_seconds: float = 0) -> Dict[str, Any]:
    """
    Evaluates user answers, computes scores per module, total score out of 100,
    and returns detailed feedback for review.
    """
    total_score = 0
    max_score = sum(q.get("points", 5) for q in exam_questions)
    module_scores = {mod: {"earned": 0, "max": 0, "name": MODULE_NAMES[mod]} for mod in ["A", "B", "C", "D"]}
    results_detail = []

    for q in exam_questions:
        q_id = q["id"]
        mod = q["module"]
        pts = q.get("points", 5)
        module_scores[mod]["max"] += pts

        user_ans = user_answers.get(q_id, "").strip()
        is_correct = False

        if q["type"] == "multiple_choice":
            correct_ans = q.get("correct_answer", "").strip().upper()
            if user_ans.upper() == correct_ans:
                is_correct = True
                total_score += pts
                module_scores[mod]["earned"] += pts
        else:
            # Scenario / short answer grading:
            # Awards full points if candidate provides a substantive response (> 30 characters)
            if len(user_ans) >= 30:
                is_correct = True
                total_score += pts
                module_scores[mod]["earned"] += pts

        results_detail.append({
            "id": q_id,
            "module": mod,
            "module_name": MODULE_NAMES.get(mod, ""),
            "topic": q.get("topic", ""),
            "difficulty": q.get("difficulty", "Trung bình"),
            "question": q["question"],
            "type": q["type"],
            "options": q.get("options", {}),
            "user_answer": user_ans,
            "correct_answer": q.get("correct_answer", ""),
            "sample_answer": q.get("sample_answer", ""),
            "is_correct": is_correct,
            "points_earned": pts if is_correct else 0,
            "points_max": pts,
            "explanation": q.get("explanation", ""),
        })

    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= 65.0

    # Diagnostic feedback: identify modules needing attention
    weak_modules = []
    strong_modules = []
    for mod, data in module_scores.items():
        pct = (data["earned"] / data["max"] * 100) if data["max"] > 0 else 0
        if pct < 60.0:
            weak_modules.append(data["name"])
        elif pct >= 80.0:
            strong_modules.append(data["name"])

    result_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": int(elapsed_seconds),
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round(percentage, 2),
        "is_passed": is_passed,
        "module_scores": module_scores,
        "weak_modules": weak_modules,
        "strong_modules": strong_modules,
        "details": results_detail,
    }

    # Save to history file for long-term progress tracking
    save_attempt_history(result_payload)

    return result_payload


def save_attempt_history(result: Dict[str, Any]) -> None:
    """Saves attempt summary into history JSON file."""
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    summary_entry = {
        "timestamp": result["timestamp"],
        "elapsed_seconds": result["elapsed_seconds"],
        "total_score": result["total_score"],
        "max_score": result["max_score"],
        "percentage": result["percentage"],
        "is_passed": result["is_passed"],
        "module_scores": {m: result["module_scores"][m]["earned"] for m in result["module_scores"]},
    }
    history.append(summary_entry)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Gracefully continue if running in read-only environment (e.g. Vercel serverless)
        pass


def load_history() -> List[Dict[str, Any]]:
    """Loads all historical attempts."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []
