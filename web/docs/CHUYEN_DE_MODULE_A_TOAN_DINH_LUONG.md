# 📐 CHUYÊN ĐỀ ÔN THI MODULE A: NỀN TẢNG TOÁN HỌC & TƯ DUY ĐỊNH LƯỢNG
### Chương Trình Đào Tạo Nhân Tài AI Thực Chiến (Vingroup - Đại Học VinUni)

Module A tập trung đánh giá nền tảng tư duy toán học ứng dụng và khả năng định lượng bài toán kỹ thuật, không yêu cầu chứng minh lý thuyết trừu tượng mà chú trọng vào khả năng tính toán, trực giác số học và tối ưu tài nguyên tính toán cho hệ thống AI.

---

## 1. Đại Số Tuyến Tính (Linear Algebra) Ứng Dụng Trong AI

### 1.1. Ma trận & Định thức (Determinant)
- **Định nghĩa & Tính chất:**
  - $\det(A \cdot B) = \det(A) \cdot \det(B)$
  - Với ma trận vuông cấp $n$: $\det(k \cdot A) = k^n \cdot \det(A)$ *(Bẫy rất hay gặp trong đề thi!)*
  - Ma trận $A$ khả nghịch khi và chỉ khi $\det(A) \neq 0$.
  - $\det(A^T) = \det(A)$ và $\det(A^{-1}) = \frac{1}{\det(A)}$.

### 1.2. Phép Nhân Ma Trận & Độ Phức Tạp
- Nhân ma trận $A \in \mathbb{R}^{M \times K}$ với $B \in \mathbb{R}^{K \times N}$ cho kết quả $C \in \mathbb{R}^{M \times N}$.
- **Số phép nhân vô hướng:** $M \times K \times N$.
- **Trong mạng nơ-ron:** Mỗi lớp Fully Connected (Dense) có đầu vào $X \in \mathbb{R}^{B \times D_{in}}$ và trọng số $W \in \mathbb{R}^{D_{in} \times D_{out}}$ tốn $B \times D_{in} \times D_{out}$ phép tính FLOPs.

### 1.3. Vector Embeddings & Độ Đo Tương Đồng
- **Tích vô hướng (Dot Product):** $\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^d u_i v_i = \|\mathbf{u}\| \|\mathbf{v}\| \cos(\theta)$.
- **Cosine Similarity:**
  $$\text{Cosine}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \cdot \|\mathbf{v}\|_2}$$
  - Khoảng giá trị: $[-1, 1]$. Bằng $1$ khi hai vector cùng hướng, bằng $0$ khi trực giao (orthogonal, không liên quan), bằng $-1$ khi ngược hướng hoàn toàn.
  - Khi vector đã được chuẩn hóa L2 ($\|\mathbf{u}\| = 1, \|\mathbf{v}\| = 1$), Cosine Similarity chính bằng tích vô hướng $\mathbf{u} \cdot \mathbf{v}$.

### 1.4. Giá Trị Riêng & Vector Riêng (Eigenvalues & Eigenvectors)
- Định nghĩa: $A \mathbf{v} = \lambda \mathbf{v}$ với $\mathbf{v} \neq \mathbf{0}$.
- Phương trình đặc trưng: $\det(A - \lambda I) = 0$.
- Vết ma trận (Trace): $\text{tr}(A) = \sum_{i} a_{ii} = \sum_{i} \lambda_i$.
- Định thức: $\det(A) = \prod_{i} \lambda_i$.

---

## 2. Giải Tích Đa Biến & Tối Ưu Hóa (Calculus & Optimization)

### 2.1. Đạo hàm & Quy tắc Dây chuyền (Chain Rule)
- Trong mạng nơ-ron, quy trình Lan truyền ngược (Backpropagation) dựa hoàn toàn trên Chain Rule:
  $$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial z} \cdot \frac{\partial z}{\partial w}$$
- **Hàm Sigmoid:** $\sigma(z) = \frac{1}{1 + e^{-z}} \implies \sigma'(z) = \sigma(z)(1 - \sigma(z))$. Cực đại của đạo hàm chỉ bằng $0.25$ tại $z=0$, dẫn tới hiện tượng Triệt tiêu gradient (Vanishing Gradient) khi xếp nhiều lớp.

### 2.2. Gradient Descent & Các Biến Thể
- **Công thức cập nhật cơ bản:**
  $$\mathbf{w}_{t+1} = \mathbf{w}_t - \alpha \nabla_{\mathbf{w}} L(\mathbf{w}_t)$$
  - $\alpha$: Hệ số học (Learning Rate). Nếu $\alpha$ quá lớn $\implies$ phân kỳ; nếu $\alpha$ quá nhỏ $\implies$ hội tụ rất chậm.
- **Gradient Descent with Momentum:**
  $$v_t = \beta v_{t-1} + (1 - \beta) g_t \implies w_{t+1} = w_t - \alpha v_t$$
  - Giúp tích lũy động lượng vượt qua các điểm yên ngựa (saddle points) và triệt tiêu dao động ngang hẻm núi hẹp.

---

## 3. Xác Suất & Thống Kê Ứng Dụng Trong AI

### 3.1. Định lý Bayes & Bẫy Tỉ Lệ Nền (Base Rate Fallacy)
- Công thức Bayes:
  $$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)} = \frac{P(B|A) \cdot P(A)}{P(B|A)P(A) + P(B|\neg A)P(\neg A)}$$
- **Ứng dụng thực chiến:** Khi tỉ lệ nền $P(A)$ rất nhỏ (ví dụ bệnh hiếm 0.1%, kẻ gian lận thẻ tín dụng 0.1%), dù hệ thống AI có độ chính xác 99% thì xác suất một cảnh báo thực sự là đúng (Precision) vẫn có thể dưới 10%!

### 3.2. Kỳ Vọng, Phương Sai & Chuẩn Hóa
- Tính chất nhân hằng số:
  - $E[c \cdot X] = c \cdot E[X]$
  - $\text{Var}(c \cdot X) = c^2 \cdot \text{Var}(X)$
  - $\text{Std}(c \cdot X) = |c| \cdot \text{Std}(X)$
- **Quy tắc thực nghiệm 68 - 95 - 99.7 của Phân phối chuẩn:**
  - $68.27\%$ giá trị nằm trong $[\mu - \sigma, \mu + \sigma]$.
  - $95.45\%$ giá trị nằm trong $[\mu - 2\sigma, \mu + 2\sigma]$.
  - $99.73\%$ giá trị nằm trong $[\mu - 3\sigma, \mu + 3\sigma]$.

### 3.3. Entropy Thông Tin & Cross-Entropy Loss
- **Shannon Entropy (đo độ bất định):**
  $$H(X) = - \sum_{i=1}^k p_i \log_2(p_i)$$
  - Phân phối đồng đều cho entropy cực đại.
- **Binary Cross-Entropy Loss:**
  $$\mathcal{L} = - [y \log(p) + (1 - y) \log(1 - p)]$$

---

## 4. Tư Duy Định Lượng & Ước Lượng Thực Chiến (Quantitative Thinking)

### 4.1. Bài toán Tối ưu Chi phí Kiến trúc Router (Cost Optimization)
- Khi vận hành sản phẩm AI lớn, không bao giờ gửi 100% queries vào mô hình lớn (GPT-4 / Claude 3.5 Sonnet / Llama 70B).
- **Mô hình Router:** Phân loại 70-80% câu hỏi đơn giản chuyển cho mô hình nhỏ SLM rẻ hơn 15 lần (ví dụ: 0.002 USD vs 0.03 USD/query), giúp cắt giảm 60-70% ngân sách điện toán hàng tháng.

### 4.2. Ước lượng Tài nguyên Vector Database
- Số byte mỗi vector float32: $d \times 4\text{ bytes}$ (với $d=1536 \implies 6144\text{ bytes} \approx 6\text{ KB}$).
- Với 10 triệu vectors: $10^7 \times 6144\text{ bytes} \approx 61.4\text{ GB RAM}$.
- Nén bằng Quantization xuống INT8 giảm $4\times$, xuống chỉ còn $\approx 15.3\text{ GB RAM}$.
