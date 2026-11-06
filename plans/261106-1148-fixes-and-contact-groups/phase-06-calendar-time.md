---
phase: 6
title: "Sửa giờ calendar và sự kiện cả ngày"
status: completed
priority: P2
effort: "1.5h"
dependencies: []
---

# Phase 6: Sửa giờ calendar và sự kiện cả ngày

## Goal
`calendar create --start "2026-11-10 08:30"` lưu đúng 08:30 giờ địa phương; `--all-day` tạo được sự kiện cả ngày; `calendar update` dùng cùng cách chuyển đổi.

## Nguyên nhân
- pywin32 coi `datetime` naive là UTC khi gán vào thuộc tính COM, nên giờ lưu bị lệch theo múi giờ máy (UTC+7 → sớm 7 tiếng).
- `appt.Start = start.date()`: COM không nhận kiểu `date`.

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\outlook_com.py` — thêm hàm thuần `to_com_time(dt)`; dùng trong `create_event` và `update_event`
- Create: `D:\outlookctl\tests\test_com_time.py`

## Tasks & Steps
1. `to_com_time(dt)`: nhận `datetime` naive (giờ địa phương do người dùng nhập), trả về `datetime` cùng giờ-phút nhưng gắn `tzinfo=timezone.utc`. Đây là cách đã kiểm chứng trên máy này (ghi trong skill): Outlook hiển thị đúng giờ nhập và `StartUTC` lệch 7 tiếng so với `Start`. Ghi rõ lý do trong docstring.
2. Thử trước bằng script nhỏ trên máy để chốt cách nào đúng: (a) `to_com_time` như trên, (b) `pywintypes.Time(dt)` với dt naive. Chọn cách cho `Start` đúng giờ nhập; ghi kết quả vào docstring.
3. All-day: `appt.AllDayEvent = True`, `appt.Start = to_com_time(datetime.combine(start.date(), time.min))`, `appt.End` = ngày kế tiếp 00:00 nếu không truyền `--end`.
4. Áp dụng `to_com_time` cho `start`/`end` trong `update_event`.
5. Unit test cho `to_com_time` (giữ nguyên giờ-phút, có tzinfo UTC, dt đã có tzinfo thì đổi về giờ địa phương trước).

## Verification
- `uv run pytest tests/test_com_time.py`
- Thủ công: tạo sự kiện thử 09:00 ngày mai trong lịch mặc định, `calendar get` và Outlook đều hiển thị 09:00; tạo sự kiện `--all-day`; `calendar update --start` sang 10:00 đúng giờ. Xóa các sự kiện thử bằng `calendar delete`.
