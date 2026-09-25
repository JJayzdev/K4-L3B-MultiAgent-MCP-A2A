# Day09 public contracts

Đây là nguồn chuẩn duy nhất cho các contract công khai của Day09 V2. Nội dung
trong thư mục này được phát hành kèm repo học viên và được dùng bởi API, MCP
gateway và submission validator.

Contract công khai gồm:

- registry của hai variant `l3a` và `l3b`;
- cấu trúc submission manifest;
- output schema của từng variant;
- MCP evidence envelope;
- observable trace event;
- public scoring policy, weights, hard gates and feedback visibility.

Contract không chứa case manifest chính thức, public/private membership,
constraint oracle, reference output, case-level private report hoặc generator seed.

Mỗi release phải giữ nguyên file đã phát hành. Khi cần thay đổi breaking,
tạo schema version mới thay vì sửa ý nghĩa của version cũ.

## Khóa schema và kiểm tra tuân thủ

`schema-lock.json` lưu SHA-256 của năm schema đã phát hành, gồm cả L3A vì L3B
tham chiếu các `$defs` của L3A. Hash dùng JSON chuẩn hóa nên không phụ thuộc
indentation hoặc CRLF/LF. `tests/test_contract_lock.py` phát hiện thay đổi nội dung,
thiếu/thừa schema và kiểm tra các trường hợp vi phạm contract.

Chạy từ root repo:

```powershell
.venv\Scripts\python.exe -m pytest -q tests/test_contract_lock.py
```

CI hiện chạy `pytest -q`, nên tự động bao gồm các kiểm tra khóa contract.
Không sửa lock để bỏ qua lỗi; thay đổi contract cần release/version có chủ đích.

Không thêm field ngoài schema. Riêng MCP `data` và trace `attributes` có độ mở
được schema quy định: không được tự ý đóng hoặc mở rộng chúng. Envelope hợp lệ
không thay thế kiểm tra domain payload, provenance và tính đúng nghiệp vụ.

Các điểm validate runtime hiện có: `EvidenceGateway.call` cho MCP envelope,
`TraceWriter.emit` cho từng trace event, CLI cho output và submission validator
cho output/trace/manifest khi đóng gói. Thiết kế Verifier trong `ARCHITECTURE.md`
bổ sung kiểm tra trước khi `solve_case()` trả kết quả ở bước triển khai sau.
