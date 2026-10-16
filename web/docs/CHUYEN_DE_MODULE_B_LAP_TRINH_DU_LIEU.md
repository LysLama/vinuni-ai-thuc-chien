# 💻 CHUYÊN ĐỀ ÔN THI MODULE B: KỸ THUẬT LẬP TRÌNH & XỬ LÝ DỮ LIỆU
### Chương Trình Đào Tạo Nhân Tài AI Thực Chiến (Vingroup - Đại Học VinUni)

Module B đánh giá năng lực lập trình Python thực chiến, tư duy cấu trúc dữ liệu - giải thuật, khả năng thao tác và tối ưu hóa xử lý dữ liệu lớn (Pandas, NumPy, Polars, SQL) dưới giới hạn tài nguyên tính toán.

---

## 1. Python Nâng Cao & Các "Cạm Bẫy" Cốt Lõi

### 1.1. Mutable Default Arguments (Đối số mặc định biến đổi)
```python
# SAI: Khởi tạo list/dict mặc định trong def-time
def add_item(val, items=[]):
    items.append(val)
    return items

# ĐÚNG: Sử dụng None và khởi tạo bên trong
def add_item(val, items=None):
    if items is None:
        items = []
    items.append(val)
    return items
```

### 1.2. Generators & Lazy Evaluation (Tránh Tràn RAM - OOM)
- Khi đọc file lớn hàng chục GB, thay vì tạo danh sách đầy đủ `[line for line in file]` gây tràn RAM, sử dụng Generator `(line for line in file)` hoặc hàm có từ khóa `yield`.
- Generator bảo toàn độ phức tạp không gian $O(1)$ bất kể dung lượng file nguồn.

### 1.3. Concurrency: Multi-Threading vs Multi-Processing & GIL
- **CPython GIL (Global Interpreter Lock):** Chỉ cho phép 1 luồng thực thi Python bytecode tại 1 thời điểm trên 1 tiến trình.
- **CPU-bound (Tính toán nặng, xử lý ma trận, huấn luyện):** Sử dụng `multiprocessing` hoặc các thư viện C/C++ (NumPy, PyTorch, C extension) để tận dụng đa lõi CPU.
- **I/O-bound (Gọi API LLM, tải dữ liệu mạng, đọc ổ đĩa):** Sử dụng `asyncio` hoặc `concurrent.futures.ThreadPoolExecutor`.

---

## 2. Thao Tác Dữ Liệu Thực Chiến: Pandas & NumPy

### 2.1. Phép Toán Vector Hóa (Vectorization) vs Vòng Lặp
- Tuyệt đối không dùng vòng lặp `for` với `df.loc[i]` trên hàng triệu dòng.
- Vectorization của NumPy/Pandas thực thi trên mảng C liên tục và tập chỉ thị SIMD phần cứng, cho tốc độ xử lý nhanh hơn 50 - 200 lần.

### 2.2. Nhóm Dữ Liệu: `.groupby().transform()` vs `.groupby().agg()`
- `.agg()`: Thu gọn số lượng dòng từ $N$ dòng ban đầu về $K$ dòng (với $K$ là số nhóm duy nhất).
- `.transform()`: Trả về Series có đúng $N$ dòng giữ nguyên chỉ mục (index) gốc, là kỹ thuật chuẩn để chuẩn hóa đặc trưng theo từng nhóm (ví dụ: trừ lương trung bình của phòng ban).

### 2.3. Tối Ưu Hóa Bộ Nhớ Pandas (Memory Downcasting)
```python
# Giảm 70-90% RAM cho bảng dữ liệu lớn
# 1. Chuyển chuỗi lặp lại sang category
df['city'] = df['city'].astype('category')

# 2. Hạ cấp số thực từ float64 xuống float32
float_cols = df.select_dtypes(include=['float64']).columns
df[float_cols] = df[float_cols].astype('float32')

# 3. Hạ cấp số nguyên sang int32 / int16
int_cols = df.select_dtypes(include=['int64']).columns
df[int_cols] = df[int_cols].astype('int32')
```

---

## 3. Kiến Trúc Pipeline Dữ Liệu Quy Mô Lớn

### 3.1. Xử Lý Tệp Lớn Bằng Kỹ Thuật Phân Khối (Chunking)
```python
import pandas as pd

# Đọc file 20GB trên máy tính 8GB RAM
chunk_size = 50_000
for chunk in pd.read_csv('massive_log.csv', chunksize=chunk_size):
    # Lọc và xử lý từng chunk trong RAM
    filtered = chunk[chunk['is_fraud'] == True]
    filtered.to_csv('output_fraud.csv', mode='a', header=False, index=False)
```

### 3.2. So Sánh Parquet vs CSV Trong Hạ Tầng AI
| Tiêu chí | CSV | Apache Parquet |
| :--- | :--- | :--- |
| **Mô hình lưu trữ** | Dạng dòng (Row-based) | Dạng cột (Columnar-based) |
| **Mức độ nén** | Kém (chiếm nhiều đĩa) | Rất cao (Snappy/Zstd nén 70-80%) |
| **Kiểu dữ liệu** | Phải parse lại từ string | Lưu sẵn schema metadata |
| **Tốc độ đọc chọn lọc cột** | Quét toàn bộ file | Chỉ nạp cột cần đọc (Column Pruning) |

---

## 4. SQL Nâng Cao & Cửa Sổ Dữ Liệu (Window Functions)

- **`ROW_NUMBER()`:** Đánh số thứ tự liên tục $1, 2, 3...$ không nhảy bậc.
- **`RANK()`:** Đồng hạng sẽ có số giống nhau, thứ hạng sau sẽ bị nhảy bước ($1, 2, 2, 4$).
- **`DENSE_RANK()`:** Đồng hạng số giống nhau nhưng không nhảy bước ($1, 2, 2, 3$).
- **Cú pháp chuẩn:**
  ```sql
  SELECT user_id, prompt_text,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as query_rank
  FROM user_queries;
  ```
