# 📋 PHÂN TÍCH VÀ LỜI GIẢI CHI TIẾT ĐỀ MẪU THỰC TẾ (CANDIDATE DEBRIEF)
### Chương Trình Đào Tạo Nhân Tài AI Thực Chiến - Vingroup & Đại Học VinUni
*Tài liệu tổng hợp và giải mã từ đề thi mẫu thực tế của các ứng viên đi trước (Practice.docx)*

---

## PHẦN 1: CODING TỰ LUẬN (CHẮC CHẮN CÓ TRONG ĐỀ THI)

Trong đề thi tuyển sinh thực tế, có các bài tập yêu cầu ứng viên tự viết code Python từ đầu (hoặc bằng NumPy) để tính toán các ma trận chỉ số đánh giá mô hình phân loại (Evaluation Metrics).

### Dạng 1: Viết Code Python Thuần (Pure Python) Tính Accuracy, Precision, Recall, F1-Score
Yêu cầu: Không dùng thư viện scikit-learn, xử lý ngoại lệ độ dài không khớp và tránh lỗi chia cho 0 (`ZeroDivisionError`).

```python
def calculate_metrics(y_true, y_pred):
    """
    Tính toán Accuracy, Precision, Recall, F1-score bằng Python thuần.
    Hỗ trợ xử lý trường hợp chia cho 0 khi mẫu số bằng 0.
    """
    # 1. Kiểm tra hai danh sách có cùng số phần tử hay không
    if len(y_true) != len(y_pred):
        raise ValueError("y_true và y_pred phải có cùng số phần tử")

    # 2. Đếm các thành phần của Confusion Matrix
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    # 3. Accuracy = (TP + TN) / Tổng số mẫu
    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0

    # 4. Precision = TP / (TP + FP)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    # 5. Recall = TP / (TP + FN)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # 6. F1-score = 2 * Precision * Recall / (Precision + Recall)
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return accuracy, precision, recall, f1

# Kiểm thử với dữ liệu thực tế
if __name__ == "__main__":
    y_true = [1, 0, 1, 1, 0]
    y_pred = [1, 0, 0, 1, 1]
    acc, prec, rec, f1 = calculate_metrics(y_true, y_pred)
    print(f"Accuracy:  {acc:.4f}")  # 3/5 = 0.6000
    print(f"Precision: {prec:.4f}") # 2/3 ≈ 0.6667
    print(f"Recall:    {rec:.4f}")  # 2/3 ≈ 0.6667
    print(f"F1-score:  {f1:.4f}")   # 0.6667
```

---

### Dạng 2: Viết Code Tính Chỉ Số Sử Dụng Thư Viện NumPy (Vectorization)
Yêu cầu: Sử dụng mảng NumPy và các phép toán boolean logic để tối ưu hóa hiệu năng tính toán.

```python
import numpy as np

def calculate_metrics_numpy(y_true, y_pred):
    """
    Tính Accuracy, Precision, Recall, F1-score bằng NumPy Vectorization.
    """
    # 1. Chuyển đổi sang numpy array
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if y_true.shape != y_pred.shape:
        raise ValueError("y_true và y_pred phải có cùng kích thước")

    # 2. Tính nhanh các thành phần Confusion Matrix
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    # 3. Tính toán các chỉ số
    total_samples = len(y_true)
    accuracy = (tp + tn) / total_samples if total_samples > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return float(accuracy), float(precision), float(recall), float(f1)
```

---

## PHẦN 2: CÁC CÂU HỎI TRẮC NGHIỆM ĐẶC THÙ (MCQ)

### Module A: Toán Học & Xác Suất Thống Kê
1. **Bài toán chọn 2 ảnh từ 1.000 ảnh (Đề gốc trong Practice.docx):**
   - *Đề bài:* Tập dữ liệu 1.000 ảnh, mô hình đoán đúng 800 ảnh, đoán sai 200 ảnh. Chọn ngẫu nhiên đồng thời 2 ảnh. Xác suất để có ít nhất 1 ảnh được mô hình AI dự đoán chính xác là bao nhiêu?
   - *Lời giải:* 
     - Dùng biến cố đối $A'$: Cả 2 ảnh chọn ra đều bị mô hình dự đoán SAI.
     - Số cách chọn 2 ảnh bất kỳ: $C_{1000}^2 = \frac{1000 \times 999}{2} = 499,500$.
     - Số cách chọn 2 ảnh từ 200 ảnh đoán sai: $C_{200}^2 = \frac{200 \times 199}{2} = 19,900$.
     - Xác suất cả 2 ảnh đều sai: $P(A') = \frac{19,900}{499,500} = \frac{199}{4995} \approx 0.03984$.
     - Vậy xác suất có ít nhất 1 ảnh đúng: $P(A) = 1 - P(A') = 1 - 0.03984 = 0.96016$ (**xấp xỉ 96.02%**).

2. **Bài toán gieo xúc xắc 6 mặt cân đối:**
   - **Kỳ vọng:**
     $$E[X] = \frac{1+2+3+4+5+6}{6} = \frac{21}{6} = 3.5$$
   - **Phương sai:**
     $$\begin{aligned}
     \text{Var}(X) &= E[X^2] - (E[X])^2 \\
     &= \frac{1^2+2^2+3^2+4^2+5^2+6^2}{6} - (3.5)^2 \\
     &= \frac{91}{6} - 12.25 = \frac{35}{12} \approx 2.917
     \end{aligned}$$
   - **Độ lệch chuẩn:**
     $$\text{Std}(X) = \sqrt{\text{Var}(X)} = \sqrt{\frac{35}{12}} \approx 1.708$$

3. **Phân biệt Phân phối Poisson vs Phân phối Mũ (Exponential):**
   - *Poisson:* Biến ngẫu nhiên **rời rạc** đếm số lượng sự kiện xảy ra trong một khoảng thời gian cố định (ví dụ: số request gửi đến API AI mỗi giây).
   - *Phân phối Mũ:* Biến ngẫu nhiên **liên tục** đo lường khoảng thời gian chờ đợi giữa hai sự kiện Poisson liên tiếp.

4. **Tổng của nhiều phân phối Bernoulli xấp xỉ phân phối nào?**
   - Nếu xác suất thành công $p$ rất nhỏ ($p \to 0$, $n$ rất lớn, $\lambda = np$ cố định) $\implies$ xấp xỉ **Phân phối Poisson**.
   - Nếu $p \ge 0.1$ và $np \ge 5, n(1-p) \ge 5$ $\implies$ xấp xỉ **Phân phối chuẩn (Normal Distribution)** theo Định lý Giới hạn Trung tâm De Moivre-Laplace.

5. **Đại số tuyến tính:**
   - *Vector riêng (Eigenvector):* Vector không bị đổi hướng khi thực hiện phép biến đổi tuyến tính qua ma trận $A$, chỉ bị kéo dài hoặc co ngắn bởi hệ số giá trị riêng $\lambda$ ($A v = \lambda v$). Giúp ta hiểu bản chất và cấu trúc không gian của phép biến đổi.
   - *Tính độc lập tuyến tính:* Một tập vector $\{v_1, \dots, v_k\}$ độc lập tuyến tính khi phương trình $c_1 v_1 + \dots + c_k v_k = 0$ chỉ có nghiệm duy nhất $c_1 = \dots = c_k = 0$.

---

### Module B: Lập Trình Python & Dữ Liệu
1. **Bài toán tính số tham số LoRA (Câu phân loại học viên):**
   - *Đề bài:* Mô hình LLM có ma trận trọng số gốc $W_0 \in \mathbb{R}^{d \times k}$. Khi áp dụng LoRA với rank $r$, số lượng tham số cần huấn luyện là bao nhiêu?
   - *Công thức:* LoRA phân rã $\Delta W = B \times A$ với $B \in \mathbb{R}^{d \times r}$ và $A \in \mathbb{R}^{r \times k}$.
   - *Số tham số:* $r \times (d + k)$.
   - *Ví dụ:* Nếu $d = 4096, k = 4096, r = 8$:
     - Trọng số gốc: $4096 \times 4096 \approx 16.78$ triệu tham số.
     - LoRA: $8 \times (4096 + 4096) = 65,536$ tham số (tiết kiệm **99.6%** bộ nhớ huấn luyện!).

2. **Cạm bẫy Alias vs Shallow Copy vs Deep Copy trong Python:**
   - `b = a`: Chỉ tạo bí danh (alias) trỏ cùng vùng nhớ. Sửa `b` là `a` đổi theo.
   - `b = copy.copy(a)` (hoặc `a.copy()`): Sao chép nông danh sách ngoài, nhưng các danh sách con lồng bên trong vẫn trỏ chung vùng nhớ.
   - `b = copy.deepcopy(a)`: Sao chép độc lập hoàn toàn ở mọi tầng.

3. **Decorators Trong Python:**
   - `@property`: Biến một method thành getter thuộc tính (truy cập không cần dấu ngoặc tròn).
   - `@staticmethod`: Phương thức tĩnh, không nhận `self` hay `cls`.
   - `@classmethod`: Nhận `cls` làm đối số đầu tiên, dùng cho Factory Pattern.
   - `@abstractmethod`: Buộc các lớp con kế thừa phải override cài đặt.
   - `@functools.lru_cache`: Lưu cache kết quả hàm dựa trên tham số đầu vào.

---

### Module C: Kiến Thức AI & Mô Hình Học Máy
1. **Tại sao LSTM vượt trội hơn RNN truyền thống?**
   - RNN gặp vấn đề nghiêm trọng về **Triệt tiêu đạo hàm (Vanishing Gradient)** khi lan truyền ngược qua chuỗi thời gian dài, do các phép nhân liên tiếp với ma trận trọng số $W$.
   - LSTM khắc phục điều này nhờ đường cao tốc thông tin **Cell State** ($C_t = f_t * C_{t-1} + i_t * \tilde{C}_t$). Đạo hàm theo $C_{t-1}$ truyền qua phép cộng tuyến tính (Constant Error Carousel) có chứa cổng quên $f_t$, giúp giữ được thông tin ngữ cảnh qua hàng trăm bước thời gian mà không bị tắt gradient.

2. **Bảng trạng thái Bias & Variance:**
   - High Bias + Low Variance $\implies$ **Underfitting** (Mô hình quá đơn giản).
   - Low Bias + High Variance $\implies$ **Overfitting** (Mô hình học vẹt, nhạy cảm với nhiễu).
   - High Bias + High Variance $\implies$ Mô hình kém toàn diện.
   - Low Bias + Low Variance $\implies$ **Mô hình lý tưởng (Good fit)**.

---

## PHẦN 3: BÀI TẬP TÌNH HUỐNG THỰC TẾ (SHORT ANSWERS / CASE STUDIES)

Trong đề thi có 3 câu tự luận tình huống xoay quanh Agent, RAG, LLM và MLOps. Dưới đây là hướng dẫn giải đạt điểm tối đa theo đúng Bareme chấm thi:

### Tình Huống 1: Khi Deploy Hệ Thống Mà Độ Chính Xác Bị Giảm So Với Lúc Train?
*Đề bài:* Sau khi đưa mô hình AI lên production, bộ phận vận hành phản ánh độ chính xác giảm sút rõ rệt so với giai đoạn huấn luyện và kiểm thử. Bạn sẽ làm thế nào?

*Các từ khóa chấm điểm (Keywords) bắt buộc phải có:*
1. **Monitoring & Logging:** Thiết lập hệ thống giám sát toàn diện; ghi log đầy đủ dữ liệu đầu vào (input), đầu ra (prediction) và phản hồi thực tế (ground truth feedback từ người dùng/chuyên viên). Bắt lỗi có hệ thống để khoanh vùng chính xác điểm nghẽn.
2. **Kiểm tra Phân phối Dữ liệu (Data Drift / Covariate Shift):** So sánh phân phối thống kê của tập dữ liệu thực tế hiện tại với tập train/validation ban đầu. Tìm hiểu nguyên nhân (ví dụ: hành vi người dùng thay đổi, cảm biến mới, môi trường thay đổi).
3. **Thiết lập Pipeline Retraining & Active Learning:** Gom các mẫu dữ liệu thực tế mà mô hình có độ tin cậy thấp (Low Confidence) để chuyển cho con người gắn nhãn, tự động kích hoạt pipeline retrain và đánh giá lại trước khi deploy bản cập nhật.
4. **Hệ thống Metrics Kép:** Đo lường đồng thời **Offline Metrics** (Accuracy, Precision, Recall, F1) và **Business/Online Metrics** (Click-Through Rate, Conversion Rate, Tỷ lệ khiếu nại khách hàng).

---

### Tình Huống 2: Thiết Kế Hệ Thống AI Agent Giáo Dục Gợi Ý Giải Bài Tập Cho Học Sinh
*Đề bài:* Thiết kế một hệ thống AI Agent hỗ trợ học sinh giải bài tập. Nếu đưa ngay đáp án cuối cùng sẽ phản tác dụng giáo dục (học sinh lười suy nghĩ). Hãy đề xuất giải pháp kỹ thuật giải quyết bài toán này và tối ưu hóa hạ tầng?

*Các từ khóa chấm điểm (Keywords) bắt buộc phải có:*
1. **Phương pháp Socratic & Hướng dẫn Từng bước (Scaffolding / Step-by-step Hinting):**
   - Cấu hình System Prompt và cơ chế Agent chỉ đưa ra câu hỏi gợi mở hoặc gợi ý một bước trung gian tiếp theo, tuyệt đối không đưa ngay đáp án hoặc lời giải hoàn chỉnh.
   - Theo dõi tiến trình suy luận của học sinh qua đối thoại nhiều lượt (Multi-turn Conversation), chỉ mở khóa bước tiếp theo khi học sinh đã hiểu bước trước.
2. **Hạ tầng Caching Câu hỏi (Semantic Cache / Redis):**
   - Trong môi trường học đường, các bài tập khó thường sẽ có rất nhiều học sinh cùng hỏi trong cùng một thời điểm (kỳ thi, bài tập về nhà).
   - Thiết lập Semantic Cache (dùng Vector similarity kết hợp Redis): Nếu câu hỏi mới tương đồng trên 95% với câu hỏi đã có trong cache, tái sử dụng luồng gợi ý đã sinh trước đó $\implies$ Giảm tải 70-80% chi phí gọi GPU/LLM API và giảm độ trễ phản hồi xuống dưới 50ms.
3. **Đo lường Metrics:**
   - **Business Metrics:** Tỷ lệ học sinh tự giải được bài sau khi nhận gợi ý, thời gian tương tác trung bình, mức độ hài lòng của giáo viên/phụ huynh.
   - **Technical Metrics:** Cache Hit Rate, Latency (Time-to-first-token), Chi phí API trên mỗi học sinh.
