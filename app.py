import streamlit as st
import time
import sys
from pathlib import Path

# Add src directory to system path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from exam_engine import (
    load_all_questions,
    get_bank_statistics,
    generate_mock_exam,
    grade_exam,
    load_history,
    MODULE_NAMES,
)

st.set_page_config(
    page_title="Luyện Thi AI Thực Chiến VinUni - Khóa V (240 Câu Hỏi Chuẩn)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f4f8;
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 4px solid #1a56db;
    }
    .badge-easy { background-color: #def7ec; color: #03543f; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .badge-medium { background-color: #fef08a; color: #713f12; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .badge-hard { background-color: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# App Title & Header
st.title("🎓 Hệ Thống Luyện Thi Đánh Giá Năng Lực Đầu Vào - Khóa V")
st.subheader("Chương Trình Đào Tạo Nhân Tài AI Thực Chiến (Vingroup phối hợp Đại học VinUni)")

# Sidebar
stats = get_bank_statistics()
with st.sidebar:
    st.image("https://vinuni.edu.vn/wp-content/uploads/2021/04/Logo-VinUni.png", width=180)
    st.header("📌 Thông Tin Kỳ Thi")
    st.info("""
    - **Thời gian thi:** Ngày 3 & 4 tháng 10 năm 2026
    - **Địa điểm:** Đại học VinUni, KĐT Vinhomes Ocean Park, Gia Lâm, Hà Nội
    - **Hạn chót đăng ký:** Trước 10:00 sáng ngày 30/9/2026
    - **Thời lượng thi:** 90 phút (Thang điểm 100)
    """)

    st.markdown("### 📊 Ngân Hàng Đề Thi Thực Chiến")
    st.write(f"Tổng số câu hỏi: **{stats['total_questions']} câu**")
    for m, info in stats["by_module"].items():
        st.write(f"- **{m}:** {info['count']} câu ({info['mc_count']} trắc nghiệm + {info['scenario_count']} tình huống)")

    st.divider()
    st.markdown("### 📞 Kênh Hỗ Trợ Tuyển Sinh")
    st.markdown("- **Email:** aithucchien@vinuni.edu.vn")
    st.markdown("- [Nhóm Zalo Khóa V (Đợt 1)](https://zalo.me/g/88ik4kbhfowwwrg6j2pj)")
    st.markdown("- [Cộng đồng AI Thực Chiến Facebook](https://www.facebook.com/share/g/1YAT9gnfeF/)")
    st.markdown("- **Hotline:** 0979489846 | 0388339478 (C Thảo)")

# Main Tabs
tab_mock, tab_practice, tab_analytics, tab_docs, tab_announcement = st.tabs([
    "🏆 Thi Thử 90 Phút (100 Điểm)",
    "🎯 Luyện Tập Từng Chuyên Đề",
    "📊 Phân Tích & Lịch Sử",
    "📚 Cẩm Nang & Bí Kíp Ôn Tập",
    "📄 Thông Báo Tuyển Sinh",
])

# -------------------------------------------------------------
# TAB 1: THI THỬ 90 PHÚT CHUẨN ĐẦU VÀO
# -------------------------------------------------------------
with tab_mock:
    st.subheader("Mô Phỏng Phòng Thi 90 Phút (20 Câu - 100 Điểm)")
    st.caption("Cấu trúc chuẩn: Mỗi Module gồm 4 câu trắc nghiệm + 1 bài tập tình huống thực tế (25 điểm/Module).")

    # Session State Init for Mock Exam
    if "mock_exam" not in st.session_state:
        st.session_state.mock_exam = generate_mock_exam("standard_100")
        st.session_state.mock_answers = {}
        st.session_state.mock_submitted = False
        st.session_state.mock_start_time = time.time()

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🔄 Đổi Đề Mới (Random)", use_container_width=True):
            st.session_state.mock_exam = generate_mock_exam("standard_100")
            st.session_state.mock_answers = {}
            st.session_state.mock_submitted = False
            st.session_state.mock_start_time = time.time()
            st.rerun()

    exam = st.session_state.mock_exam

    if not st.session_state.mock_submitted:
        # Timer calculation
        elapsed_sec = int(time.time() - st.session_state.mock_start_time)
        remaining_sec = max(0, 90 * 60 - elapsed_sec)
        mins = remaining_sec // 60
        secs = remaining_sec % 60

        answered_count = len([k for k, v in st.session_state.mock_answers.items() if v.strip()])
        progress_val = answered_count / len(exam)

        c_info, c_time = st.columns([3, 1])
        with c_info:
            st.write(f"Tiến độ hoàn thành: **{answered_count}/{len(exam)}** câu ({progress_val * 100:.0f}%)")
            st.progress(progress_val)
        with c_time:
            st.metric("⏳ Thời Gian Còn Lại", f"{mins:02d}:{secs:02d}")

        st.divider()

        # Render questions
        current_module = ""
        for idx, q in enumerate(exam, 1):
            if q["module"] != current_module:
                current_module = q["module"]
                st.markdown(f"### 🔹 {MODULE_NAMES[current_module]}")
                st.caption(f"Trọng số: 25 điểm (5 câu hỏi - 5 điểm/câu)")

            diff = q.get("difficulty", "Trung bình")
            badge_class = "badge-easy" if diff == "Cơ bản" else ("badge-medium" if diff == "Trung bình" else "badge-hard")

            with st.container():
                st.markdown(f"""
                **Câu {idx} [{q['id']}]** - *Chủ đề: {q.get('topic', '')}* &nbsp;
                <span class="{badge_class}">{diff}</span> &nbsp;
                *(5 điểm)*
                """, unsafe_allow_html=True)
                st.write(q["question"])

                if q["type"] == "multiple_choice":
                    opts = q["options"]
                    formatted_opts = [f"{k}. {v}" for k, v in opts.items()]
                    current_val = st.session_state.mock_answers.get(q["id"], None)
                    selected_idx = None
                    if current_val:
                        for i, k in enumerate(opts.keys()):
                            if k == current_val:
                                selected_idx = i
                                break

                    ans = st.radio(
                        f"Lựa chọn đáp án câu {idx}:",
                        options=formatted_opts,
                        index=selected_idx if selected_idx is not None else None,
                        key=f"mock_radio_{q['id']}",
                        label_visibility="collapsed",
                    )
                    if ans:
                        st.session_state.mock_answers[q["id"]] = ans.split(".")[0].strip()
                else:
                    ans = st.text_area(
                        f"Phương án trả lời câu {idx}:",
                        value=st.session_state.mock_answers.get(q["id"], ""),
                        key=f"mock_text_{q['id']}",
                        placeholder="Trình bày giải pháp kỹ thuật, phân tích ưu nhược điểm, phương án tối ưu...",
                        height=120,
                    )
                    st.session_state.mock_answers[q["id"]] = ans

                st.write("")

        st.divider()
        if st.button("🚀 NỘP BÀI THI & XEM ĐIỂM", type="primary", use_container_width=True):
            st.session_state.mock_submitted = True
            st.rerun()

    else:
        # Results View
        elapsed = time.time() - st.session_state.mock_start_time
        res = grade_exam(exam, st.session_state.mock_answers, elapsed_seconds=elapsed)

        st.header("🎯 KẾT QUẢ BÀI THI MÔ PHỎNG")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Tổng Điểm", f"{res['total_score']} / {res['max_score']}")
        r2.metric("Tỉ Lệ Đạt", f"{res['percentage']}%")
        r3.metric("Thời Gian Làm Bài", f"{res['elapsed_seconds'] // 60}m {res['elapsed_seconds'] % 60}s")
        res_label = "🎉 ĐẠT CHUẨN ĐẦU VÀO" if res["is_passed"] else "⚠️ CẦN ÔN TẬP THÊM"
        r4.metric("Đánh Giá Hội Đồng", res_label)

        st.subheader("Chi Tiết Điểm Số Theo 04 Module")
        cols = st.columns(4)
        for i, (m_code, m_data) in enumerate(res["module_scores"].items()):
            with cols[i]:
                pct = (m_data["earned"] / m_data["max"] * 100) if m_data["max"] > 0 else 0
                st.metric(f"{m_code} (Max {m_data['max']}đ)", f"{m_data['earned']} điểm", f"{pct:.0f}%")
                st.progress(pct / 100)

        if res["weak_modules"]:
            st.warning(f"⚠️ **Khuyến nghị ôn tập thêm:** Bạn cần rà soát lại các module: {', '.join(res['weak_modules'])}")
        if res["strong_modules"]:
            st.success(f"🌟 **Điểm mạnh:** Bạn hoàn thành xuất sắc các module: {', '.join(res['strong_modules'])}")

        st.divider()
        st.subheader("🔍 Lời Giải & Phân Tích Chi Tiết Từng Câu Hỏi")
        for item in res["details"]:
            status_icon = "✅" if item["is_correct"] else "❌"
            header = f"{status_icon} [{item['id']}] {item['module_name']} - {item['topic']} ({item['points_earned']}/{item['points_max']}đ)"
            with st.expander(header):
                st.markdown(f"**Câu hỏi:**\n{item['question']}")
                if item["type"] == "multiple_choice":
                    st.markdown(f"- **Bạn chọn:** `{item['user_answer'] or 'Chưa chọn'}`")
                    st.markdown(f"- **Đáp án đúng:** **`{item['correct_answer']}`**")
                else:
                    st.markdown(f"- **Câu trả lời của bạn:**\n>{item['user_answer'] or 'Trống'}")
                    st.markdown(f"- **Đáp án / Lời giải chuẩn:**\n```\n{item['sample_answer']}\n```")
                st.info(f"💡 **Giải thích chi tiết & Trực giác kỹ thuật:**\n\n{item['explanation']}")

# -------------------------------------------------------------
# TAB 2: LUYỆN TẬP TỪNG CHUYÊN ĐỀ (IMMEDIATE FEEDBACK)
# -------------------------------------------------------------
with tab_practice:
    st.subheader("🎯 Chế Độ Luyện Tập Từng Chuyên Đề (120 Câu Hỏi)")
    st.caption("Luyện theo từng module với phản hồi tức thì và giải thích chi tiết ngay sau mỗi câu.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        sel_module = st.selectbox(
            "Chọn Module Cần Ôn Luyện:",
            options=["A", "B", "C", "D"],
            format_func=lambda x: MODULE_NAMES[x],
        )
    with p_col2:
        sel_diff = st.selectbox(
            "Mức Độ Khó:",
            options=["Tất cả", "Cơ bản", "Trung bình", "Nâng cao"],
        )

    all_q = load_all_questions()
    mod_questions = all_q.get(sel_module, [])
    if sel_diff != "Tất cả":
        mod_questions = [q for q in mod_questions if q.get("difficulty") == sel_diff]

    st.write(f"Đang hiển thị **{len(mod_questions)} câu hỏi** thuộc {MODULE_NAMES[sel_module]}:")

    for i, q in enumerate(mod_questions, 1):
        diff = q.get("difficulty", "Trung bình")
        badge_class = "badge-easy" if diff == "Cơ bản" else ("badge-medium" if diff == "Trung bình" else "badge-hard")

        with st.expander(f"Câu {i} [{q['id']}]: {q['question'][:90]}..."):
            st.markdown(f"**Câu hỏi:** {q['question']}")
            st.markdown(f"*Chủ đề: {q.get('topic', '')}* | *Độ khó: <span class='{badge_class}'>{diff}</span>*", unsafe_allow_html=True)

            if q["type"] == "multiple_choice":
                opts = [f"{k}. {v}" for k, v in q["options"].items()]
                user_choice = st.radio("Chọn câu trả lời:", options=opts, key=f"practice_{q['id']}")
                if st.button("Kiểm tra đáp án", key=f"btn_{q['id']}"):
                    chosen_letter = user_choice.split(".")[0].strip()
                    if chosen_letter == q["correct_answer"]:
                        st.success(f"🎉 **Chính xác!** Đáp án là **{q['correct_answer']}**.")
                    else:
                        st.error(f"❌ **Chưa chính xác.** Bạn chọn {chosen_letter}, đáp án đúng là **{q['correct_answer']}**.")
                    st.info(f"💡 **Giải thích:** {q['explanation']}")
            else:
                st.write("**Bài tập Tình huống / Tự luận ngắn**")
                st.text_area("Nhập phương án của bạn:", key=f"practice_text_{q['id']}")
                if st.button("Xem hướng dẫn giải mẫu", key=f"btn_sc_{q['id']}"):
                    st.markdown(f"**Hướng dẫn đáp án mẫu:**\n```\n{q['sample_answer']}\n```")
                    st.info(f"💡 **Phân tích:** {q['explanation']}")

# -------------------------------------------------------------
# TAB 3: PHÂN TÍCH & LỊCH SỬ THI THỬ
# -------------------------------------------------------------
with tab_analytics:
    st.subheader("📊 Lịch Sử Làm Bài & Theo Dõi Tiến Trình")
    history = load_history()

    if not history:
        st.info("Chưa có lịch sử làm bài thi mô phỏng. Hãy hoàn thành ít nhất một bài thi trong Tab 'Thi Thử 90 Phút' để xem thống kê tiến độ!")
    else:
        st.write(f"Đã thực hiện **{len(history)} lượt thi thử**:")
        hist_table = []
        for idx, h in enumerate(reversed(history), 1):
            passed_str = " Đạt" if h.get("is_passed") else "❌ Chưa đạt"
            mins = h.get("elapsed_seconds", 0) // 60
            hist_table.append({
                "Lần": len(history) - idx + 1,
                "Thời gian": h.get("timestamp"),
                "Tổng Điểm": f"{h.get('total_score')}/{h.get('max_score')}",
                "Tỉ lệ": f"{h.get('percentage')}%",
                "Thời lượng": f"{mins} phút",
                "Kết quả": passed_str,
                "Module A": h.get("module_scores", {}).get("A", "-"),
                "Module B": h.get("module_scores", {}).get("B", "-"),
                "Module C": h.get("module_scores", {}).get("C", "-"),
                "Module D": h.get("module_scores", {}).get("D", "-"),
            })
        st.dataframe(hist_table, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: CẨM NANG & BÍ KÍP PHÒNG THI
# -------------------------------------------------------------
with tab_docs:
    st.subheader("📚 Kho Tài Liệu & Cẩm Nang Ôn Thi Toàn Diện")
    doc_options = {
        "Chiến Lược Phòng Thi 90 Phút & Checklist VinUni": "KINH_NGHIEM_THI_THUC_CHIEN_VINUNI.md",
        "Chuyên Đề Module A: Nền Tảng Toán Học & Định Lượng": "CHUYEN_DE_MODULE_A_TOAN_DINH_LUONG.md",
        "Chuyên Đề Module B: Kỹ Thuật Lập Trình & Xử Lý Dữ Liệu": "CHUYEN_DE_MODULE_B_LAP_TRINH_DU_LIEU.md",
        "Chuyên Đề Module C: Kiến Thức AI & Tư Duy Sản Phẩm": "CHUYEN_DE_MODULE_C_AI_SAN_PHAM.md",
        "Chuyên Đề Module D: Tư Duy Logic, Đạo Đức & Hành Vi": "CHUYEN_DE_MODULE_D_LOGIC_DAO_DUC.md",
    }
    sel_doc_label = st.selectbox("Chọn tài liệu ôn tập:", list(doc_options.keys()))
    target_file = Path(__file__).resolve().parent / "docs" / doc_options[sel_doc_label]
    if target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning(f"Không tìm thấy file: {target_file.name}")

# -------------------------------------------------------------
# TAB 5: THÔNG BÁO TUYỂN SINH CHÍNH THỨC
# -------------------------------------------------------------
with tab_announcement:
    st.subheader("📄 Thông Báo Đăng Ký Dự Thi Khóa V - Vòng 2")
    announcement_file = Path(__file__).resolve().parent / "docs" / "THONG_BAO_THI_TUYEN_KHOA_V.md"
    docx_file = Path(__file__).resolve().parent / "docs" / "THONG_BAO_THI_TUYEN_KHOA_V.docx"

    col_d1, col_d2 = st.columns([1, 4])
    with col_d1:
        if docx_file.exists():
            with open(docx_file, "rb") as f_doc:
                st.download_button(
                    label="📥 Tải File Word (.docx)",
                    data=f_doc.read(),
                    file_name="THONG_BAO_THI_TUYEN_KHOA_V.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

    if announcement_file.exists():
        with open(announcement_file, "r", encoding="utf-8") as f:
            st.markdown(f.read())
