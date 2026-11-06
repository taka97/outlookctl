---
phase: 7
title: "Cập nhật docs, skill, cài lại tool, gỡ workaround"
status: completed
priority: P1
effort: "1.5h"
dependencies: [1, 2, 3, 4, 5, 6]
---

# Phase 7: Docs, skill và triển khai lên máy

## Goal
Tài liệu và skill mô tả đúng hành vi mới; máy đang dùng bản fork; quy trình báo cáo tuần trong `D:\project\working_dir\CLAUDE.md` chuyển sang dùng `outlookctl` thay cho pywin32.

## Files to Create / Modify
- Modify: `D:\outlookctl\README.md` — lệnh `contacts group`, reply/reply-all mới, `by-path:` có store
- Modify: `D:\outlookctl\skills\outlook-automation\SKILL.md` và `reference\cli.md`, `reference\json-schema.md`
- Modify: `D:\outlookctl\docs\cli.html`, `docs\json-schema.html` (nếu đang được duy trì cùng README)
- Modify: `D:\project\working_dir\.claude\skills\outlook-automation\SKILL.md` — xóa các ghi chú lỗi đã sửa (charmap, by-path, giờ calendar, all-day); giữ ghi chú về lịch mặc định của người dùng
- Modify: `D:\project\working_dir\CLAUDE.md` — bước soạn email báo cáo tuần dùng `outlookctl draft --reply-all --to … --cc "Technical Team" --attach …`

## Tasks & Steps
1. Cập nhật README, SKILL.md và reference của repo.
2. Cài lại tool từ fork: `uv tool install --force --editable D:\outlookctl` (hoặc không `--editable` nếu muốn bản cố định); chạy `outlookctl --version` và `outlookctl doctor`.
3. Chạy kiểm thử chấp nhận cuối trong `plan.md`; xóa draft thử.
4. Cập nhật skill và CLAUDE.md của `D:\project\working_dir`.
5. Commit theo từng phase trên nhánh `hoang/feat/fixes-and-contact-groups`; chỉ push hoặc mở PR khi người dùng yêu cầu.

## Verification
- `uv run pytest` toàn bộ xanh.
- `outlookctl doctor` pass.
- Kiểm thử chấp nhận cuối trong `plan.md` đạt.
