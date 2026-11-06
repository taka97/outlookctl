---
title: "outlookctl fork: hoàn thành 7 phase sửa lỗi và contact group"
date: 2026-11-06
summary: "Đã sửa UTF-8, người nhận, reply/reply-all, folder đa store, giờ calendar và thêm contacts group; cài editable trên máy"
---

# outlookctl fork: hoàn thành 7 phase sửa lỗi và contact group

## What happened
- 7 commit trên nhánh `hoang/feat/fixes-and-contact-groups` (db0d51f..bf08de3), 100 test pass (từ 67).
- Thử nghiệm COM xác nhận chỉ gán "giờ địa phương gắn nhãn UTC" mới lưu đúng giờ; naive, pywintypes.Time và aware-local đều lệch 7h.
- Kiểm thử thật trên Outlook: reply/reply-all/forward giữ trích dẫn HTML, contacts group tạo/thêm/bớt/xóa, by-path qua store, calendar 09:00/10:00/all-day. Mọi draft/sự kiện/nhóm thử đã xóa (Deleted Items).

## Decision
- Pure helpers ở `src/outlookctl/utils.py` để test không cần COM.
- Reply: `--to/--cc/--bcc` thay thế theo loại; nội dung chèn sau thẻ `<body>`; forward dùng chung.
- Người nhận không resolve được thì không lưu, trừ `--allow-unresolved`.
- Cài fork editable thay bản `C:\Users\vanho\tools\outlookctl`.

## Next steps
- `docs/*.html` (GitHub Pages) chưa cập nhật.
- JSON output của calendar vẫn hiển thị giờ địa phương kèm `+00:00` (ngoài phạm vi).
- Chưa push/PR; thư mục `plans/` chưa commit.

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
