---
title: "outlookctl fork: plan sửa lỗi và thêm contact group"
date: 2026-11-06
summary: Lập plan 7 phase cho fork outlookctl dựa trên lỗi gặp khi làm quy trình email báo cáo tuần
---

# outlookctl fork: plan sửa lỗi và thêm contact group

## What happened
- Khi làm quy trình email báo cáo tuần (06/11/2026), `outlookctl draft --reply-all` bỏ qua `--cc`/`--attach` và gán `Body` làm mất định dạng HTML phần trích dẫn (`outlook_com.py` `create_reply_all`). Phải dùng pywin32 để tạo draft.
- Reply thường ghi đè body và subject (`create_draft`).
- Không có lệnh contact group; nhóm "Technical Team" được điền bằng pywin32.
- Ghi chú skill trên máy còn các lỗi: charmap với tiếng Việt, `by-name/by-path` chỉ tìm store 1, `calendar create` lệch 7h, `--all-day` lỗi kiểu `date`.

## Decision
- Plan tại `plans/261106-1148-fixes-and-contact-groups/` gồm 7 phase: UTF-8 output, chuẩn hóa/kiểm tra người nhận, reply fidelity, `contacts group`, folder đa store, giờ calendar, docs và triển khai.
- Reply: `--to/--cc/--bcc` thay thế người nhận theo loại; body chèn sau thẻ `<body>`.
- Ngoài phạm vi: M365 Groups, Categories, chọn store cho lịch mặc định.

## Next steps
- Người dùng duyệt plan và trả lời câu hỏi mở, rồi chạy `/ak:cook` trên `plan.md`.

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
