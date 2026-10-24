# Hệ Thống Gợi Ý Phím

Đồ án cuối kì môn Cấu trúc rời rạc: hệ thống gợi ý phim sử dụng tập hợp
và hệ số Jaccard, viết bằng Python với giao diện Streamlit tiếng Việt.

## 1. Dữ liệu và phạm vi

- 20 bộ phim có thật và 25 người dùng hư cấu, chia thành 5 nhóm sở thích.
- Sở thích hoàn toàn giả lập, tạo thủ công; không phải dữ liệu khảo sát.
- Không dùng Machine Learning, API phim, cơ sở dữ liệu hoặc tài khoản đăng nhập.
- Giao diện hiện chọn hồ sơ U01–U25; chưa có chức năng khách tự chọn phim.

## 2. Các tệp chính

| Tệp | Chức năng |
| --- | --- |
| `app.py` | Giao diện: chọn người, xem sở thích, Top 3, phim gợi ý và giải thích toán học |
| `requirements.txt` | Khai báo Streamlit; pip tự cài các phụ thuộc của Streamlit |
| `recommendation.py` | Đọc/kiểm tra JSON, chuyển set, tính Jaccard, chọn hàng xóm, gợi ý; có bản Terminal |
| `data/movies.json` | Danh mục ID và tên 20 phim |
| `data/users.json` | Danh sách 25 người và ID phim yêu thích, có nhãn dữ liệu giả lập |
| `tests/test_recommendation.py` | 33 bài unittest cho thuật toán, dữ liệu và lựa chọn người dùng |
| `TEST_REPORT.md` | Kết quả kiểm thử thuật toán và giới hạn đánh giá |

Giao diện import các hàm trong `recommendation.py`, không viết lại công thức
hay quy tắc chọn phim. Khối `if __name__ == "__main__"` của module thuật toán
giúp việc import không mở vòng nhập ID trong Terminal.

## 3. Cài và chạy trong PyCharm

### Chọn đúng Python Interpreter

1. Mở thư mục dự án trong PyCharm.
2. Vào Settings → Project → Python Interpreter, chọn interpreter đã chạy
   thành công `recommendation.py` và unittest.
3. Mở Terminal, chuyển đến thư mục `project` chứa `app.py`.
4. Kiểm tra lệnh `python` có dùng đúng interpreter đó không:

```powershell
python -c "import sys; print(sys.executable)"
```

Nếu đường dẫn khác interpreter đã chọn trong PyCharm hoặc báo thiếu Python,
dùng đường dẫn đầy đủ của interpreter đang hoạt động cho tất cả lệnh tiếp theo:

```powershell
& 'ĐƯỜNG_DẪN_PYTHON_ĐANG_HOẠT_ĐỘNG' -m pip install -r requirements.txt
& 'ĐƯỜNG_DẪN_PYTHON_ĐANG_HOẠT_ĐỘNG' -m streamlit run app.py
```

Chuỗi trong dấu nháy là chỗ cần thay bằng đường dẫn thực tế đến `python.exe`.
Không sửa `pyvenv.cfg` hoặc đổi interpreter chỉ để khớp ví dụ trong tài liệu.

### Cài phụ thuộc và chạy ứng dụng

Nếu `python` đã trỏ đúng interpreter:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Mở địa chỉ Local URL được in trong Terminal, thường là `http://localhost:8501`.
Dừng ứng dụng bằng Ctrl+C. Chạy bằng module `streamlit`, không chạy trực tiếp
`python app.py`. Cách cài và chạy tham khảo
[tài liệu cài Streamlit chính thức](https://docs.streamlit.io/get-started/installation/command-line).

### Tạo nút Run trong PyCharm

Trong Run → Edit Configurations → thêm cấu hình Python:

- Chọn **Module name** và nhập `streamlit`.
- Parameters: `run app.py`.
- Working directory: đường dẫn thư mục `project`.
- Python Interpreter: interpreter đã cài Streamlit bằng lệnh phía trên.

Sau đó bấm Run để khởi động máy chủ và mở Local URL trong trình duyệt.

## 4. Cách sử dụng

1. Chọn bất kỳ người dùng U01–U25 trong dropdown; nhãn gồm ID và tên.
2. Xem bảng tên và ID phim yêu thích của hồ sơ đã chọn.
3. Bấm **Gợi ý phim** để xem Top 3 và danh sách phim mới.
4. Mở phần bảng Jaccard để xem so sánh với 24 người còn lại.
5. Đọc phần công thức và ví dụ U01–U05 để hiểu giao, hợp và hiệu.
6. Đổi người dùng rồi bấm nút lần nữa. Kết quả cũ được ẩn khi đổi hồ sơ.

Ứng dụng báo lỗi tiếng Việt nếu thiếu tệp hoặc JSON không hợp lệ. Nếu không
có hàng xóm có điểm dương hoặc không có phim mới, ứng dụng thông báo thay
vì hiển thị danh sách kết quả giả.

## 5. Cách thuật toán hoạt động

Mỗi người có một tập ID phim yêu thích. Với hai tập A và B:

```text
J(A, B) = |A ∩ B| / |A ∪ B|
```

- `A & B`: phim cả hai cùng thích; `A | B`: tất cả phim, không lặp.
- `len(...)`: đếm số phần tử của tập hợp.
- Nếu hợp rỗng, quy ước Jaccard bằng 0.
- Loại chính người mục tiêu; lấy tối đa 3 người có điểm lớn hơn 0.
- Sắp điểm giảm dần; nếu bằng điểm, ID tăng dần.
- Phim gợi ý = hợp phim của các hàng xóm trừ phim người mục tiêu đã thích.
- Thứ tự phim theo ID là cách hiển thị ổn định, không phải xếp hạng chất lượng.

Ví dụ U01 thích `{M01, M02, M03, M07, M18}`, U05 thích
`{M01, M02, M09, M18, M19}`. Giao có 3 phim, hợp có 7 phim nên
Jaccard = 3/7 ≈ 0,4286.

## 6. Kiểm tra chương trình

Chạy bằng cùng interpreter đã cài Streamlit, từ thư mục `project`:

```powershell
python -m py_compile app.py
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

Nếu cần, thay `python` bằng đường dẫn đầy đủ và tiền tố `&` như phần cài đặt.
`py_compile` chỉ kiểm tra cú pháp; không xác nhận giao diện chạy đúng.

Kiểm tra trên trình duyệt:

- Dropdown có đủ U01–U25; chọn U01 rồi bấm nút.
- Top 3 U01 là U05 — Hà (0,4286), U21 — Thảo (0,4286), U02 — Bình (0,3750).
- Sáu phim U01: M04 Avatar, M09 Titanic, M11 La La Land, M15 Get Out,
  M17 Avengers: Endgame và M19 Your Name.
- Chuyển sang U05 hoặc U25: kết quả U01 biến mất, sở thích cập nhật;
  bấm nút để lấy kết quả mới. Có thể chọn lần lượt toàn bộ 25 hồ sơ.
- Kiểm tra tên/ID, công thức, bảng so sánh, độ dễ đọc trên cửa sổ hẹp.

**Trạng thái kiểm tra tại thời điểm tạo giao diện:** sinh viên đã cung cấp
kết quả 33 unittest đạt trong PyCharm ở giai đoạn trước, được ghi trong
`TEST_REPORT.md`. Đây chưa phải kết quả chạy lại sau khi thêm giao diện.
Terminal của trợ lý hiện không khởi động được Python vì `.venv` trỏ tới bản
Python 3.12 không có tại đường dẫn đã cấu hình. Vì vậy chưa xác nhận kiểm tra
cú pháp, chạy lại unittest hoặc chạy ứng dụng Streamlit thành công tại đây.
Không coi việc tạo xong mã là bằng chứng giao diện đã chạy được.

Hạn chế: chưa có lịch sử xem đầy đủ, nên chỉ loại phim đã thích; người chưa
có sở thích không có hàng xóm điểm dương; k = 3 chưa được tối ưu thực nghiệm;
chưa có đánh giá chất lượng bằng phản hồi người dùng thật.

Giao diện dùng các thành phần có sẵn như dropdown, bảng và container để mã
dễ đọc. Tham khảo [tài liệu bố cục Streamlit](https://docs.streamlit.io/develop/concepts/design/layouts-and-containers).
