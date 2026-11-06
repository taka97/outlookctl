---
phase: 1
title: "Ép UTF-8 cho output CLI"
status: completed
priority: P1
effort: "0.5h"
dependencies: []
---

# Phase 1: Ép UTF-8 cho output CLI

## Goal
`outlookctl` in được tiếng Việt (subject, tên, nội dung) mà không cần `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`.

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\cli.py` — đầu `main()`
- Create: `D:\outlookctl\tests\test_output_encoding.py`

## Tasks & Steps
1. Thêm hàm `_force_utf8_stdio()` trong `cli.py`: với `sys.stdout` và `sys.stderr`, nếu có `reconfigure` thì gọi `reconfigure(encoding="utf-8", errors="replace")`. Gọi ở dòng đầu `main()`.
2. Kiểm tra đường đọc tham số: argv trên Windows đã là Unicode, không cần xử lý thêm. Ghi chú điều này trong docstring.
3. Test: thay `sys.stdout` bằng `io.TextIOWrapper(io.BytesIO(), encoding="cp1252")`, gọi `_force_utf8_stdio()`, in chuỗi "Báo cáo tuần - Team Kỹ thuật", đọc lại bytes và decode UTF-8 phải khớp.

## Verification
- `uv run pytest tests/test_output_encoding.py`
- Thủ công (PowerShell, không đặt biến môi trường): `outlookctl search --folder sent --query "Báo cáo tuần" --count 1` in đúng "Kỹ thuật".
