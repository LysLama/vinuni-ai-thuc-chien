# 🤖 CHUYÊN ĐỀ ÔN THI MODULE C: KIẾN THỨC AI & TƯ DUY SẢN PHẨM AI
### Chương Trình Đào Tạo Nhân Tài AI Thực Chiến (Vingroup - Đại Học VinUni)

Module C kiểm tra độ hiểu biết sâu sắc về các công nghệ AI hiện đại nhất (Machine Learning, Deep Learning, Generative AI, LLM, RAG, AI Agents) và tư duy sản phẩm định hướng giá trị kinh doanh (Business ROI, Khung SFIA, MLOps, Guardrails).

---

## 1. Nền Tảng Machine Learning & Deep Learning

### 1.1. Tradeoff Thiên Kiến & Phương Sai (Bias - Variance Tradeoff)
- **High Bias (Underfitting):** Mô hình quá đơn giản, không học được quy luật dữ liệu (lỗi cao trên cả Train và Test). $\implies$ Khắc phục: Tăng độ phức tạp mô hình, thêm đặc trưng (feature engineering).
- **High Variance (Overfitting):** Mô hình học vẹt cả nhiễu của tập Train (lỗi Train rất thấp nhưng lỗi Test rất cao). $\implies$ Khắc phục: Bổ sung dữ liệu, Early Stopping, Regularization (L1/L2), Dropout.

### 1.2. Thước Đo Đánh Giá Phù Hợp Thực Chiến
- **Accuracy:** Chỉ dùng khi tập dữ liệu cân bằng (Balanced Classes). Tuyệt đối không dùng khi dữ liệu mất cân bằng nghiêm trọng (Fraud, Y tế, Lỗi sản xuất).
- **Precision:** Tỉ lệ trong số các ca mô hình báo dương tính thì có bao nhiêu ca thực sự dương tính:
  $$\text{Precision} = \frac{TP}{TP + FP}$$
- **Recall (Độ nhạy):** Tỉ lệ trong số các ca thực tế dương tính thì mô hình bắt trọn được bao nhiêu ca:
  $$\text{Recall} = \frac{TP}{TP + FN}$$
- **F1-Score:** Trung bình điều hòa giữa Precision và Recall: $F_1 = 2 \cdot \frac{P \cdot R}{P + R}$.
- **PR-AUC:** Đo lường diện tích dưới đường cong Precision-Recall, là chỉ số tiêu chuẩn vàng khi dữ liệu có tỉ lệ dương tính cực thấp.

---

## 2. Kỷ Nguyên Generative AI & Large Language Models (LLM)

### 2.1. Căn Chỉnh Mô Hình & Vòng Đời LLM
1. **Pre-training:** Huấn luyện trên hàng nghìn tỷ tokens từ internet để nén tri thức thế giới (chi phí hàng triệu USD).
2. **SFT (Supervised Fine-Tuning):** Tinh chỉnh có giám sát theo định dạng đối thoại câu hỏi - câu trả lời chất lượng cao.
3. **Alignment (Căn chỉnh giá trị con người):**
   - **RLHF:** Huấn luyện mô hình phần thưởng (Reward Model) và tối ưu hóa bằng giải thuật PPO.
   - **DPO (Direct Preference Optimization):** Tối ưu hóa trực tiếp trên cặp dữ liệu sở thích (Chosen vs Rejected) bằng hàm mất mát khép kín, không cần Reward Model phức tạp.

### 2.2. Tinh Chỉnh Tiết Kiệm Tham Số: PEFT & LoRA
- Thay vì cập nhật toàn bộ hàng tỷ tham số của mô hình gốc, **LoRA (Low-Rank Adaptation)** phân rã ma trận cập nhật $\Delta W$ thành tích của hai ma trận hạng thấp:
  $$W = W_0 + \frac{\alpha}{r} (B \cdot A)$$
  - Giảm tới 99% tham số cần huấn luyện, giúp huấn luyện mô hình 7B-14B trên card đồ họa đơn lẻ.

### 2.3. Lượng Tử Hóa Mô Hình (Quantization: FP16 $\to$ INT8 $\to$ INT4)
- Giảm kích thước bộ nhớ VRAM của mô hình gấp 2-4 lần.
- Kỹ thuật QLoRA cho phép fine-tune mô hình đã lượng tử hóa 4-bit với chất lượng xấp xỉ 16-bit gốc.

---

## 3. Kiến Trúc RAG Tiên Tiến (Advanced RAG Architecture)

### 3.1. Các Thành Phần Trọng Yếu
```
User Query ---> Query Transformation (Rewrite / Sub-queries)
                    |
                    v
    Hybrid Retrieval (Dense Vector HNSW + Sparse BM25)
                    |
                    v
    Re-Ranking (Cross-Encoder / Cohere / BGE)
                    |
                    v
    Context Window Management (Small-to-Big / Parent Document)
                    |
                    v
    LLM Generator (with Guardrails) ---> Grounded Answer
```

### 3.2. Triệt Tiêu Ảo Giác (Hallucination Mitigation)
- **Tách bạch System Prompt và Context:** Ép mô hình chỉ trích dẫn nội dung có trong văn bản (`Faithfulness`).
- **NLI Verification (Natural Language Inference):** Kiểm tra xem từng câu trả lời có được suy diễn trực tiếp từ các đoạn văn trích dẫn hay không.
- **Reranker:** Đưa các đoạn tài liệu có độ liên quan cao nhất lên đầu context để tránh hiện tượng "Lost in the Middle".

---

## 4. Tác Tử AI Thông Minh (AI Agents & Multi-Agent)

- **Mô hình ReAct (Reasoning + Acting):**
  - **Thought:** Tác tử lập luận về tình trạng hiện tại và mục tiêu cần đạt.
  - **Action:** Tác tử quyết định gọi công cụ ngoại vi (Tool Call / Search / API).
  - **Observation:** Tác tử đọc kết quả trả về từ công cụ và suy luận tiếp bước tiếp theo.
- **Multi-Agent Collaboration:** Phân chia các vai trò chuyên biệt (Researcher, Coder, Critic/Reviewer) giúp nâng cao độ chính xác lên gấp nhiều lần so với một prompt đơn lẻ.

---

## 5. Khung Năng Lực SFIA & Định Vị Nhân Tài AI Thực Chiến

| Cấp độ SFIA | Tên gọi | Đặc điểm năng lực cốt lõi |
| :--- | :--- | :--- |
| **Level 3** | **Apply** | Thực thi công việc dưới sự hướng dẫn chung; áp dụng thành thạo các kỹ thuật chuẩn (xử lý dữ liệu, tinh chỉnh mô hình, kiểm thử); có tính tự chủ trong các bài toán đã xác định. |
| **Level 4** | **Enable** | Làm việc hoàn toàn độc lập; tự lựa chọn và áp dụng các kỹ thuật AI/ML phù hợp nhất; dẫn dắt và giải quyết các sự cố kỹ thuật phức tạp trong nhóm. |
| **Level 5** | **Ensure & Advise**| Cấp độ Chuyên gia/Trưởng dự án; định hướng kiến trúc công nghệ; tư vấn chiến lược cho ban lãnh đạo; thiết lập tiêu chuẩn kỹ thuật chất lượng cho toàn tổ chức. |

> **Nguyên tắc "Làm Được Việc" của Vingroup:** Công nghệ chỉ có giá trị khi giải quyết bài toán kinh doanh cụ thể, triển khai nhanh chóng (Fast Time-to-Market), chi phí vận hành hợp lý và mang lại ROI (Return on Investment) thực chất.
