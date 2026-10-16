#!/usr/bin/env python3
"""
CLI Exam Simulation & Practice Tool
Chương trình Luyện thi Đánh giá Năng lực - AI Thực Chiến VinUni (Khóa V)
Hỗ trợ: Thi thử chuẩn 90 phút 100 điểm, Luyện thi theo từng Module, Xem giải thích chi tiết.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from exam_engine import (
    generate_mock_exam,
    grade_exam,
    get_bank_statistics,
    load_all_questions,
    MODULE_NAMES,
)


def print_banner():
    print("\n" + "=" * 75)
    print("  🎓 HỆ THỐNG LUYỆN THI ĐÁNH GIÁ NĂNG LỰC ĐẦU VÀO - KHÓA V")
    print("  Chương trình Đào tạo Nhân tài AI Thực chiến (Vingroup - VinUni)")
    print("=" * 75)


def run_exam_flow(exam, mode_title="BÀI THI MÔ PHỎNG"):
    print(f"\n--- {mode_title} (Số lượng: {len(exam)} câu hỏi) ---")
    print("Bắt đầu tính giờ làm bài...")
    start_time = time.time()
    user_answers = {}

    current_mod = ""
    for idx, q in enumerate(exam, 1):
        if q["module"] != current_mod:
            current_mod = q["module"]
            print("\n" + "#" * 70)
            print(f"  {MODULE_NAMES[current_mod].upper()}")
            print("#" * 70 + "\n")

        diff = q.get("difficulty", "Trung bình")
        topic = q.get("topic", "")
        print(f"Câu {idx}/{len(exam)} [{q['id']}] - Chủ đề: {topic} ({diff}) - [{q.get('points', 5)} điểm]:")
        print(q["question"])

        if q["type"] == "multiple_choice":
            for opt_k, opt_v in q["options"].items():
                print(f"   {opt_k}. {opt_v}")
            while True:
                ans = input("=> Đáp án của bạn (A/B/C/D, hoặc 'skip' để bỏ qua): ").strip().upper()
                if ans in ["A", "B", "C", "D", "SKIP"]:
                    if ans != "SKIP":
                        user_answers[q["id"]] = ans
                    break
                print("Lỗi: Vui lòng nhập A, B, C hoặc D!")
        else:
            print("\n[Bài tập tình huống / Tự luận ngắn]")
            print("Nhập phương án giải quyết (hoặc Enter để bỏ qua):")
            ans = input("=> ").strip()
            if ans:
                user_answers[q["id"]] = ans

        print("-" * 50)

    elapsed_seconds = time.time() - start_time
    mins = int(elapsed_seconds // 60)
    secs = int(elapsed_seconds % 60)

    print("\n" + "=" * 75)
    print("                     BÁO CÁO KẾT QUẢ")
    print("=" * 75)
    result = grade_exam(exam, user_answers, elapsed_seconds=elapsed_seconds)

    print(f"Thời gian hoàn thành: {mins} phút {secs} giây")
    print(f"Tổng điểm đạt được: {result['total_score']} / {result['max_score']} ({result['percentage']}%)")
    status = " ĐẠT YÊU CẦU ĐẦU VÀO" if result["is_passed"] else "⚠️ CẦN RÀ SOÁT LẠI KIẾN THỨC"
    print(f"Đánh giá hội đồng: {status}")

    print("\nChi tiết điểm số theo từng Module:")
    for mod_key, mod_info in result["module_scores"].items():
        pct = (mod_info["earned"] / mod_info["max"] * 100) if mod_info["max"] > 0 else 0
        bar = "█" * int(pct // 10) + "░" * (10 - int(pct // 10))
        print(f"  - {mod_info['name']}: {mod_info['earned']}/{mod_info['max']}đ [{bar}] ({pct:.1f}%)")

    print("\nBạn có muốn xem giải thích chi tiết từng câu không? (y/n)")
    if input("=> ").strip().lower() == "y":
        print("\n" + "=" * 75)
        print("                     LỜI GIẢI VÀ GIẢI THÍCH CHI TIẾT")
        print("=" * 75)
        for item in result["details"]:
            status_icon = " ĐÚNG" if item["is_correct"] else "❌ SAI"
            print(f"\n[{item['id']}] {status_icon} - {item['module_name']} - {item['topic']}")
            print(f"Câu hỏi: {item['question']}")
            if item["type"] == "multiple_choice":
                print(f"Bạn chọn: {item['user_answer'] or 'Chưa chọn'} | Đáp án đúng: {item['correct_answer']}")
            else:
                print(f"Bạn trả lời: {item['user_answer'] or 'Trống'}")
                print(f"Đáp án mẫu:\n{item['sample_answer']}")
            print(f"💡 Phân tích: {item['explanation']}")
            print("-" * 50)


def main():
    print_banner()
    stats = get_bank_statistics()
    print(f"Hệ thống đã nạp: {stats['total_questions']} câu hỏi chuẩn hóa.")
    print("Địa điểm thi: Trường Đại học VinUni (3-4/10/2026)")
    print("Hạn đăng ký: Trước 10:00 sáng ngày 30/9/2026\n")

    while True:
        print("\nMENU LUYỆN TẬP:")
        print("1. 🏆 Thi Thử 90 Phút (Chuẩn cấu trúc 20 câu - 100 điểm)")
        print("2. 📐 Luyện tập Module A: Toán học & Định lượng (30 câu)")
        print("3. 💻 Luyện tập Module B: Lập trình & Dữ liệu (30 câu)")
        print("4. 🤖 Luyện tập Module C: Kiến thức & Sản phẩm AI (30 câu)")
        print("5. ⚖️ Luyện tập Module D: Tư duy Logic, Đạo đức & Hành vi (30 câu)")
        print("6. 📊 Thống kê ngân hàng đề")
        print("0. Thoát")

        choice = input("\nChọn chức năng (0-6): ").strip()
        if choice == "1":
            exam = generate_mock_exam("standard_100")
            run_exam_flow(exam, "THI THỬ CHUẨN 90 PHÚT - 100 ĐIỂM")
        elif choice in ["2", "3", "4", "5"]:
            mod_map = {"2": "A", "3": "B", "4": "C", "5": "D"}
            mod = mod_map[choice]
            exam = generate_mock_exam("module_practice", module_filter=mod)
            run_exam_flow(exam, f"LUYỆN TẬP {MODULE_NAMES[mod].upper()}")
        elif choice == "6":
            print("\n" + "=" * 50)
            print("THỐNG KÊ NGÂN HÀNG CÂU HỎI THỰC CHIẾN:")
            for m, info in stats["by_module"].items():
                print(f"  - {info['name']}: {info['count']} câu ({info['mc_count']} trắc nghiệm + {info['scenario_count']} tình huống)")
            print(f"Độ khó: {stats['by_difficulty']}")
            print("=" * 50)
        elif choice == "0":
            print("\nChúc bạn ôn tập xuất sắc và đỗ Khóa V Chương trình AI Thực Chiến VinUni!\n")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại!")


if __name__ == "__main__":
    main()
