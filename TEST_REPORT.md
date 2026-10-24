# Báo cáo kiểm thử và đánh giá hệ thống gợi ý phim

## 1. Phạm vi và trạng thái thực tế

Bộ kiểm thử nằm tại `tests/test_recommendation.py`, dùng thư viện chuẩn
`unittest`, gồm 33 phương thức kiểm thử. Một số phương thức dùng `subTest`
để kiểm tra nhiều cặp tập hợp hoặc cả 25 người dùng.

Chỉ bổ sung bộ kiểm thử và báo cáo này. Không sửa `recommendation.py`,
`AGENTS.md` hoặc hai tệp JSON; không thay công thức và không thêm Streamlit.

**Sinh viên đã chạy bộ unittest bằng Python Interpreter trong PyCharm và
cung cấp kết quả thực tế như sau:**

```text
Ran 33 tests in 0.045s

OK
```

| Tổng số bài đã chạy | PASS | FAIL | ERROR | Thời gian |
| ---: | ---: | ---: | ---: | ---: |
| 33 | 33 | 0 | 0 | 0,045 giây |

Kết quả được ghi nhận từ output sinh viên cung cấp, không phải từ lần
chạy lại của trợ lý. Output kết thúc bằng `OK`, không báo bài bỏ qua hoặc
kết quả ngoại lệ. Thời gian 0,045 giây là thời gian chạy bộ kiểm thử, không
phải phép đo hiệu năng riêng của thuật toán gợi ý.

Lần thử trước trong Terminal của trợ lý không khởi động được Python do
môi trường `.venv` tham chiếu bản cài đặt bị thiếu. Đây là lỗi môi trường
của lần thử trước, không được tính thành một bài FAIL hoặc ERROR trong
lần chạy thành công tại PyCharm. Sinh viên chưa cung cấp phiên bản và
đường dẫn đầy đủ của interpreter hoặc lệnh chạy cụ thể; báo cáo không
tự bổ sung các thông tin này.

| Hạng mục | Công cụ thực sự đã chạy | Kết quả thực tế |
| --- | --- | --- |
| 33 bài unittest | Python Interpreter trong PyCharm; output do sinh viên cung cấp | 33 PASS, 0 FAIL, 0 ERROR |
| Đọc cú pháp JSON, 20 phim, 25 người | PowerShell `ConvertFrom-Json` và kiểm tra điều kiện | PASS |
| ID phim/người dùng duy nhất, ID tham chiếu hợp lệ | PowerShell và kiểm tra điều kiện | PASS |
| Mỗi người thích 4–7 phim, không lặp ID trong danh sách | PowerShell và kiểm tra điều kiện | PASS |
| Tính đối chiếu U01, U05, U10 | PowerShell tính kết quả mong đợi; unittest đối chiếu mã Python | Bài `test_known_results_for_three_targets` nằm trong bộ 33 bài đạt |

Không dùng kết quả PowerShell để thay cho kết quả thực thi mã Python.

## 2. Nội dung bộ kiểm thử

| Nhóm lớp | Số bài | Nội dung |
| --- | ---: | --- |
| `TestJaccard` | 7 | Tập giống nhau, không giao, giao một phần, hai tập rỗng, một tập rỗng, khoảng [0,1], tính đối xứng, chuyển sang set |
| `TestDataset` | 5 | Số lượng, ID và tên phim duy nhất, sở thích hợp lệ, nhãn giả lập, 5 nhóm × 5 người, hàm đọc trả đúng dữ liệu |
| `TestRecommendations` | 11 | Loại người mục tiêu, giới hạn hàng xóm, điểm dương, thứ tự và hòa điểm, kết quả đối chiếu, phim mới/không trùng/có tên, trường hợp rỗng, cấu hình k, ID không tồn tại |
| `TestUserSelection` | 3 | Chọn lần lượt U01–U25, hiển thị ID/tên, mặc định, chữ thường/khoảng trắng, thoát, nhập sai rồi nhập lại |
| `TestInvalidJson` | 7 | JSON sai cú pháp, thiếu tệp, ID phim không có, ID trùng, tên phim trùng, bản ghi sai hoặc thiếu ID, danh sách sở thích sai |
| Tổng | 33 | 33 PASS, 0 FAIL, 0 ERROR theo output PyCharm do sinh viên cung cấp |

`assertEqual` so sánh kết quả thực tế với kết quả mong đợi. `assertAlmostEqual`
so sánh số thập phân để tránh khác biệt nhỏ do biểu diễn số thực.
`assertRaises` kiểm tra chương trình có báo lỗi dữ liệu đúng tình huống.
`subTest` giúp chỉ ra chính xác người dùng hoặc trường hợp nào không đạt.

Phần khoảng [0,1] thử toàn bộ 64 cặp tạo từ 8 tập con của 3 phim. Đây là
kiểm thử hữu hạn, không phải chứng minh bằng thực nghiệm cho mọi tập hợp.
Về toán học, giao là tập con của hợp nên khi hợp khác rỗng,
`0 <= |A ∩ B| <= |A ∪ B|`; chia cho lực lượng của hợp cho kết quả trong [0,1].

Dữ liệu JSON sai chỉ được tạo trong thư mục tạm bằng `tempfile`, tự dọn sau
kiểm thử. Các trường hợp tập rỗng và sở thích khác thường dùng dữ liệu trong
bộ nhớ. Không sửa dữ liệu mẫu để tạo tình huống biên.

## 3. Kết quả đối chiếu cho ba người dùng

Các bảng sau được tính độc lập bằng PowerShell từ JSON hiện tại, theo quy tắc:
loại chính người mục tiêu, chỉ lấy điểm lớn hơn 0, sắp điểm giảm dần rồi ID
tăng dần và lấy tối đa 3 người. Các kết quả này đã được đưa vào bài
`test_known_results_for_three_targets` để đối chiếu khi chạy Python. Theo
kết quả 33 bài đạt do sinh viên cung cấp, bài kiểm thử này đã đạt: Top 3,
điểm Jaccard và danh sách ID phim trả về khớp các kết quả mong đợi bên dưới.

### U01 — An

| Thứ tự | Hàng xóm | Jaccard chính xác | Hiển thị |
| --- | --- | --- | ---: |
| 1 | U05 — Hà | 3/7 | 0,4286 |
| 2 | U21 — Thảo | 3/7 | 0,4286 |
| 3 | U02 — Bình | 3/8 | 0,3750 |

Phim gợi ý theo ID: M04 — Avatar; M09 — Titanic; M11 — La La Land;
M15 — Get Out; M17 — Avengers: Endgame; M19 — Your Name.

### U05 — Hà

| Thứ tự | Hàng xóm | Jaccard chính xác | Hiển thị |
| --- | --- | --- | ---: |
| 1 | U02 — Bình | 4/7 | 0,5714 |
| 2 | U12 — Mai | 4/7 | 0,5714 |
| 3 | U01 — An | 3/7 | 0,4286 |

Phim gợi ý theo ID: M03 — The Matrix; M04 — Avatar; M07 — The Dark Knight;
M10 — The Notebook; M11 — La La Land; M17 — Avengers: Endgame.

### U10 — Lan

| Thứ tự | Hàng xóm | Jaccard chính xác | Hiển thị |
| --- | --- | --- | ---: |
| 1 | U07 — Hân | 3/7 | 0,4286 |
| 2 | U06 — Hải | 3/8 | 0,3750 |
| 3 | U13 — Minh | 2/7 | 0,2857 |

Phim gợi ý theo ID: M01 — Inception; M03 — The Matrix;
M06 — Mad Max: Fury Road; M12 — Pride & Prejudice;
M17 — Avengers: Endgame; M18 — WALL-E; M20 — Train to Busan.

Thứ tự phim là thứ tự ID để hiển thị ổn định, không phải điểm chất lượng.
Thuật toán sắp hàng xóm theo điểm đầy đủ trước khi làm tròn để in.

## 4. Ví dụ tính tay để thuyết trình

Với U01 và U05:

```text
A = {M01, M02, M03, M07, M18}
B = {M01, M02, M09, M18, M19}
A ∩ B = {M01, M02, M18}                         → 3 phim
A ∪ B = {M01, M02, M03, M07, M09, M18, M19}     → 7 phim
J(A, B) = 3/7 ≈ 0,4286
```

Với Top 3 của U01, hợp sở thích của U05, U21 và U02 là:

```text
N = {M01, M02, M04, M07, M09, M11, M15, M17, M18, M19}
N − A = {M04, M09, M11, M15, M17, M19}
```

M03 không có trong hợp N. Các phim M01, M02, M07, M18 bị loại vì U01 đã
thích. Phép hợp tự loại phần tử trùng, nên một phim có nhiều hàng xóm cùng
thích vẫn chỉ xuất hiện một lần.

Nếu hai tập đều rỗng, quy ước Jaccard bằng 0 để tránh chia cho 0. Nếu chỉ
một tập rỗng, giao rỗng và hợp khác rỗng nên công thức cũng cho 0. Người
có điểm 0 không được dùng làm hàng xóm. Nếu không có hàng xóm, hoặc mọi
phim của hàng xóm đã có trong tập mục tiêu, kết quả gợi ý là danh sách rỗng.

## 5. Tính đúng đắn và chất lượng gợi ý

**Tính đúng đắn** nghĩa là chương trình làm đúng quy tắc đã chọn: tính đúng
Jaccard, chọn đúng hàng xóm, áp dụng đúng hợp và hiệu, không gợi ý lại phim
đã thích. Theo kết quả chạy trong PyCharm do sinh viên cung cấp, cả 33 bài
unittest đều đạt. Kết quả này xác nhận chương trình đáp ứng các trường hợp
đã kiểm thử, không chứng minh chương trình không thể có lỗi ở mọi đầu vào.

**Chất lượng gợi ý** nghĩa là người dùng có thật sự thích phim được đưa ra
hay không. Việc toàn bộ unittest đạt chưa chứng minh điều đó.
Dữ liệu gồm 25 người hư cấu và sở thích tạo thủ công; tên phim thật không
làm sở thích trở thành dữ liệu khảo sát. Chưa có phản hồi người thật, tập
kiểm tra độc lập hoặc thí nghiệm giấu phim để đánh giá chất lượng. Vì vậy
không báo cáo độ chính xác, precision, recall hoặc mức hài lòng giả định.

Ưu điểm:

- Công thức ngắn, dễ giải thích bằng các phép tập hợp của môn học.
- Có thể truy ra vì sao một phim xuất hiện: phim thuộc sở thích hàng xóm
  và chưa nằm trong tập của người mục tiêu.
- Quy tắc hòa điểm và thứ tự ID giúp kết quả có thể tái lập.
- Dữ liệu nhỏ, lưu cục bộ, không cần thư viện Machine Learning.

Hạn chế:

- Quy mô nhỏ và sở thích giả lập không đại diện cho hành vi ngoài thực tế.
- Người chưa chọn phim có điểm 0 với mọi người nên không nhận được gợi ý.
- Chỉ có phim yêu thích, không có lịch sử xem đầy đủ: phim đã xem nhưng
  không thích vẫn có thể được gợi ý.
- k = 3 là lựa chọn minh họa, chưa được tối ưu bằng đánh giá thực nghiệm.
- Mỗi phim trong hợp được xử lý như nhau; chưa dùng số người thích hoặc
  trọng số Jaccard để xếp hạng phim.
- Khi nhiều người bằng điểm, ID quyết định người được chọn; đây là quy
  tắc ổn định, không phải bằng chứng người có ID nhỏ phù hợp hơn.

## 6. Cách chạy bằng interpreter hoạt động trong PyCharm

1. Mở Settings → Project → Python Interpreter, xác định interpreter đang
   chạy được `recommendation.py` và ghi lại đường dẫn đầy đủ.
2. Tạo Run Configuration loại Python tests → Unittests. Chọn thư mục
   `tests` làm target, thư mục `project` làm Working directory, dùng đúng
   interpreter vừa xác định và bật thêm content root vào PYTHONPATH.
3. Chạy cấu hình này. Hoặc trong Terminal ở thư mục `project`, dùng đường
   dẫn interpreter đó thay cho lệnh `python` đang lỗi:

```powershell
& 'ĐƯỜNG_DẪN_PYTHON_ĐANG_HOẠT_ĐỘNG' -m unittest discover -s tests -v
```

Chỉ khi output thực tế báo đã chạy đủ 33 bài và kết thúc `OK` mới ghi PASS
cho bộ unittest. Nếu có `FAIL` hoặc `ERROR`, lưu tên bài và traceback.
Nếu lỗi thuộc `recommendation.py`, giải thích nguyên nhân và xin phép
sinh viên trước khi sửa. Chưa phát hiện lỗi thuật toán qua việc đọc mã;
điều này không thay thế kiểm thử thực thi.

Kết quả hiện được ghi nhận là 33 PASS, 0 FAIL, 0 ERROR trong 0,045 giây,
dựa trên output PyCharm sinh viên cung cấp. Khi cần tái lập lần chạy,
có thể bổ sung phiên bản Python, đường dẫn interpreter và cấu hình chạy
thực tế. Các thông tin môi trường chưa được cung cấp không làm thay đổi
số bài đạt, thất bại hoặc lỗi đã ghi nhận.
