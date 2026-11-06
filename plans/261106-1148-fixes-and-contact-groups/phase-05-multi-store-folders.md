---
phase: 5
title: "Tìm folder trên mọi store"
status: completed
priority: P2
effort: "1.5h"
dependencies: []
---

# Phase 5: Tìm folder trên mọi store

## Goal
`--folder by-name:<tên>` và `--folder by-path:<đường dẫn>` tìm được folder trong mọi store (ví dụ Inbox/Care-HRM của `hoang.ho@tsp.com.vn`), không chỉ store đầu tiên.

## Hành vi mới
- `by-path:` nhận thêm dạng có tên store ở đầu: `by-path:hoang.ho@tsp.com.vn/Inbox/Care-HRM`. Nếu phần đầu khớp `DisplayName` của một store thì đi từ root của store đó.
- `by-path:` không có tên store: thử store chứa Inbox mặc định trước (`GetDefaultFolder(6).Parent`), rồi lần lượt các store còn lại.
- `by-name:`: tìm ở store mặc định trước, rồi các store còn lại. Có nhiều kết quả trùng tên ở nhiều store thì lấy kết quả ở store mặc định và ghi `warning` ra stderr kèm các đường dẫn khác.
- Giữ nguyên hành vi các folder mặc định (`inbox`, `sent`, `drafts`…).

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\outlook_com.py` — `get_folder_by_name`, `get_folder_by_path`; thêm `iter_stores_default_first(namespace)` và hàm thuần `split_store_prefix(path, store_names)`
- Create: `D:\outlookctl\tests\test_folder_spec.py`

## Tasks & Steps
1. Viết `split_store_prefix` (so tên store không phân biệt hoa thường) và test.
2. Viết `iter_stores_default_first`.
3. Sửa hai hàm tìm folder dùng các helper trên; bọc lỗi COM ở từng store để store lỗi (ví dụ PST ngắt kết nối) không chặn store khác.

## Verification
- `uv run pytest tests/test_folder_spec.py`
- Thủ công: `outlookctl list --folder "by-path:Inbox/Care-HRM" --count 3` và `outlookctl list --folder "by-path:hoang.ho@tsp.com.vn/Inbox/Care-HRM" --count 3` trả về thư; `--folder sent` không đổi kết quả.
