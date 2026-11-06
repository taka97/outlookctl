---
title: "outlookctl: sửa lỗi reply/encoding/calendar/folder và thêm contact group"
description: "Sửa các lỗi đã gặp khi dùng outlookctl thực tế và bổ sung lệnh quản lý contact group, để quy trình email báo cáo tuần chạy hoàn toàn bằng CLI."
status: completed
priority: P1
effort: 13h
branch: hoang/feat/fixes-and-contact-groups
tags: [bugfix, feature, backend]
blockedBy: []
blocks: []
created: 2026-11-06
---

# outlookctl: sửa lỗi và thêm contact group

## Mục tiêu

Sau khi xong plan này, quy trình "chuẩn bị email báo cáo tuần" (reply all email cũ, thay CC bằng contact group, đính kèm file .xlsx, chèn nội dung giữ định dạng phần trích dẫn) chạy được chỉ bằng `outlookctl`, không cần script pywin32. Đồng thời sửa các lỗi đã ghi trong ghi chú skill trên máy (encoding, folder nhiều store, giờ calendar, sự kiện cả ngày).

## Bằng chứng (đã kiểm tra trong mã nguồn `src/outlookctl/`)

| Lỗi | Vị trí | Nguyên nhân |
|---|---|---|
| Lỗi "charmap" với tiếng Việt khi không đặt `PYTHONUTF8=1` | `cli.py` `main()` (dòng ~1589) | stdout dùng code page Windows; `json.dumps(ensure_ascii=False)` in ký tự ngoài cp1252 |
| `draft --reply-all` bỏ qua `--to/--cc/--bcc/--attach` | `cli.py:300`, `outlook_com.py:1265` `create_reply_all` | Hàm không nhận các tham số này |
| Thêm nội dung làm mất định dạng phần trích dẫn | `create_reply_all` (`reply.Body = body_text + …`) | Gán `Body` dạng text làm Outlook chuyển thư sang plain text |
| Reply thường xóa toàn bộ phần trích dẫn và subject "RE:" | `create_draft` (`mail.Body = body_text`, `mail.Subject = subject`) | Ghi đè body; luôn gán subject kể cả khi rỗng |
| `--folder by-name:/by-path:` chỉ tìm ở store đầu tiên | `get_folder_by_name`, `get_folder_by_path` (`namespace.Folders.Item(1)`) | Cứng store 1 ("Outlook Data File" trên máy này) |
| `calendar create` lưu giờ sớm 7 tiếng | `create_event` (`appt.Start = start`) | pywin32 coi datetime naive là UTC |
| `calendar create --all-day` lỗi kiểu dữ liệu | `create_event` (`appt.Start = start.date()`) | COM không nhận `datetime.date` |
| Không có lệnh contact group | — | Chưa có tính năng |

## Các phase

| # | Phase | Ưu tiên | Effort | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| 1 | [Ép UTF-8 cho output CLI](phase-01-utf8-output.md) | P1 | 0.5h | — | completed |
| 2 | [Chuẩn hóa và kiểm tra người nhận](phase-02-recipient-validation.md) | P1 | 2h | — | completed |
| 3 | [Reply/reply-all giữ trích dẫn, nhận To/CC/BCC/đính kèm](phase-03-reply-fidelity.md) | P1 | 3h | 2 | completed |
| 4 | [Lệnh `contacts group`](phase-04-contact-groups.md) | P1 | 3h | 1 | completed |
| 5 | [Tìm folder trên mọi store](phase-05-multi-store-folders.md) | P2 | 1.5h | — | completed |
| 6 | [Sửa giờ calendar và sự kiện cả ngày](phase-06-calendar-time.md) | P2 | 1.5h | — | completed |
| 7 | [Cập nhật docs, skill, cài lại tool, gỡ workaround](phase-07-docs-and-rollout.md) | P1 | 1.5h | 1–6 | completed |

Thứ tự đề xuất: 1 → 2 → 3 → 4 (đủ cho email báo cáo tuần) → 5 → 6 → 7.

## Nguyên tắc chung

- Giữ nguyên safety model: chỉ tạo draft, `send` vẫn bắt buộc `--confirm-send YES`. Không phase nào được gửi mail hay gửi lời mời họp.
- Logic thuần (chuẩn hóa địa chỉ, chèn HTML, chuyển đổi giờ, parse folder spec) tách thành hàm không phụ thuộc COM để viết unit test với `pytest`. Phần gọi COM kiểm thử thủ công trên máy có Classic Outlook theo checklist ở từng phase.
- Không đổi định dạng JSON output hiện có; chỉ thêm trường mới (ví dụ `unresolved`).
- Mỗi phase là một commit riêng, chạy `uv run pytest` trước khi commit.

## Ngoài phạm vi

- Microsoft 365 Groups và Categories (người dùng đã xác nhận chỉ cần contact group).
- Chọn store cho lịch mặc định: người dùng đã gom toàn bộ sự kiện vào "Calendar (This computer only)" và `calendar create` đã ghi đúng chỗ đó.
- Gửi PR ngược về upstream (có thể làm sau, không nằm trong plan).

## Kiểm thử chấp nhận cuối

Trên máy này, sau phase 7, chạy được (không đặt biến môi trường UTF-8):

```bash
outlookctl contacts group show --name "Technical Team"
outlookctl draft --reply-to-id <id> --reply-to-store <store> --reply-all \
  --to "trang.do@tsp.com.vn" --cc "Technical Team" \
  --attach "C:\Users\vanho\OneDrive\Documents\Weekly Reports\Báo Cáo Tuần-YYYYMMDD.xlsx" \
  --body-text "Dear Trang, ..."
```

Draft tạo ra có To đúng 1 địa chỉ sạch, CC là nhóm Technical Team, có file đính kèm, nội dung mới nằm trên phần trích dẫn còn nguyên định dạng HTML. Xóa draft thử sau khi kiểm tra.

## Câu hỏi còn mở

Xem cuối phần trả lời của Claude khi tạo plan; cập nhật lại plan sau khi người dùng trả lời.
