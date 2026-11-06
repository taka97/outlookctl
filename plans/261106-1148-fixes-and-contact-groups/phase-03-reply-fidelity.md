---
phase: 3
title: "Reply/reply-all giữ trích dẫn, nhận To/CC/BCC/đính kèm"
status: completed
priority: P1
effort: "3h"
dependencies: [2]
---

# Phase 3: Reply và reply-all đầy đủ

## Goal
`draft --reply-to-id … [--reply-all]` nhận `--to/--cc/--bcc/--attach/--subject`, chèn nội dung mới lên trên phần trích dẫn mà vẫn giữ định dạng HTML, và không xóa subject "RE: …".

## Hành vi mới (cần ghi vào docs ở phase 7)
- Reply và reply-all dùng chung một hàm `create_reply(outlook_app, entry_id, store_id, reply_all, to, cc, bcc, body_text, body_html, attachments, subject)`.
- `--to`, `--cc`, `--bcc` khi đi kèm reply: **thay thế** toàn bộ người nhận của loại đó trong draft (không cộng thêm). Không truyền thì giữ người nhận mà Outlook tự điền.
- `--subject` chỉ ghi đè khi được truyền; mặc định giữ subject "RE: …" của Outlook.
- `--body-text`: escape HTML, đổi `\n` thành `<br>`, bọc trong `<div>` cùng font với thư (Calibri 11pt), rồi chèn ngay sau thẻ `<body …>` của `HTMLBody`. `--body-html`: chèn nguyên văn ở cùng vị trí. Nếu thư gốc là plain text (`BodyFormat == 1`) thì chèn vào đầu `Body`.
- `--attach` thêm file như thư mới; báo lỗi nếu file không tồn tại, trước khi `Save()`.
- Dùng `add_recipients` và `check_resolved` của phase 2.

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\outlook_com.py` — thay `create_reply_all` và nhánh reply trong `create_draft` bằng `create_reply`; thêm hàm thuần `insert_into_html_body(html, fragment)` và `text_to_html_fragment(text)`
- Modify: `D:\outlookctl\src\outlookctl\cli.py` — `cmd_draft` gọi `create_reply` khi có `--reply-to-id`; bỏ điều kiện bỏ qua recipient khi reply-all
- Create: `D:\outlookctl\tests\test_reply_body.py`

## Tasks & Steps
1. Viết `text_to_html_fragment` và `insert_into_html_body` (tìm `<body[^>]*>` không phân biệt hoa thường; không có thẻ body thì chèn vào đầu).
2. Viết `create_reply`: `Reply()` hoặc `ReplyAll()` → thay người nhận theo loại được truyền → chèn body → subject nếu có → đính kèm → `check_resolved` → `Save()`.
3. Sửa `cmd_draft`: mọi trường hợp có `--reply-to-id` đều đi qua `create_reply`; reply (không all) cũng không bắt buộc `--to`.
4. Giữ tương thích: lệnh cũ `draft --reply-all --reply-to-id … --body-text …` vẫn chạy, chỉ khác là phần trích dẫn giữ HTML.
5. Unit test: chèn vào HTML có `<body lang=EN-US link=…>`, HTML không có body, text có ký tự `<`, `&`, xuống dòng, tiếng Việt.

## Verification
- `uv run pytest tests/test_reply_body.py`
- Thủ công: reply-all email báo cáo tuần gần nhất trong Sent Items với `--to "trang.do@tsp.com.vn" --cc "Technical Team" --attach <file> --body-text "Dear Trang,\n..."`. Mở draft trong Outlook: To 1 người, CC là nhóm, có đính kèm, phần trích dẫn còn định dạng, subject còn "RE:". Xóa draft thử (chuyển vào Deleted Items).
- Thủ công: reply thường không truyền `--subject`, subject vẫn là "RE: …" và phần trích dẫn còn nguyên.
