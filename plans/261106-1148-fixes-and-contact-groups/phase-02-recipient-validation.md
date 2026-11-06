---
phase: 2
title: "Chuẩn hóa và kiểm tra người nhận"
status: completed
priority: P1
effort: "2h"
dependencies: []
---

# Phase 2: Chuẩn hóa và kiểm tra người nhận

## Goal
Mọi lệnh tạo thư (`draft`, `send` thư mới, `forward`) làm sạch địa chỉ người nhận và báo lỗi rõ ràng khi Outlook không nhận ra người nhận, thay vì lưu draft có địa chỉ sai như `'an.nguyen@tsp.com.vn'`.

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\cli.py` — `parse_recipient_args`, thêm cờ `--allow-unresolved` cho `draft`, `send`, `forward`
- Modify: `D:\outlookctl\src\outlookctl\outlook_com.py` — thêm helper `add_recipients(mail, to, cc, bcc)` và `check_resolved(mail)`; dùng trong `create_draft`, `send_new_message`, `create_forward`
- Modify: `D:\outlookctl\src\outlookctl\models.py` — thêm trường tùy chọn `unresolved: list[str]` vào kết quả draft nếu cần
- Modify: `D:\outlookctl\tests\test_cli_helpers.py`

## Tasks & Steps
1. Hàm thuần `normalize_recipient(s: str) -> str`: bỏ khoảng trắng hai đầu, bỏ cặp nháy đơn/nháy kép bao ngoài, nếu dạng `Tên <a@b>` thì lấy `a@b`. Giữ nguyên chuỗi không phải email (tên contact group như "Technical Team").
2. `parse_recipient_args` gọi `normalize_recipient` cho từng phần tử, bỏ phần tử rỗng, khử trùng lặp không phân biệt hoa thường nhưng giữ thứ tự.
3. `add_recipients(mail, to, cc, bcc)`: gom đoạn `Recipients.Add(...).Type = …` đang lặp ở nhiều hàm vào một chỗ (DRY).
4. `check_resolved(mail) -> list[str]`: gọi `Recipients.ResolveAll()`, trả về tên các recipient có `Resolved == False`.
5. Trong `create_draft`/`send_new_message`/`create_forward`: nếu còn recipient chưa resolve và không có `--allow-unresolved` thì **không** `Save()`/`Send()`, ném `OutlookError` liệt kê các tên đó. Với `--allow-unresolved` thì lưu draft và trả về danh sách `unresolved` trong JSON.
6. Unit test cho `normalize_recipient` và `parse_recipient_args`: `'an.nguyen@tsp.com.vn'`, `"x@y.z"`, `Trang <trang.do@tsp.com.vn>`, `Technical Team`, chuỗi rỗng, trùng lặp khác hoa thường.

## Verification
- `uv run pytest tests/test_cli_helpers.py`
- Thủ công: `outlookctl draft --to "khong-ton-tai-xyz" --subject test --body-text test` báo lỗi unresolved và không có draft mới trong Drafts.
- Thủ công: `outlookctl draft --to "'trang.do@tsp.com.vn'" --subject test --body-text test` tạo draft có To là `trang.do@tsp.com.vn` không dính nháy; xóa draft thử.
