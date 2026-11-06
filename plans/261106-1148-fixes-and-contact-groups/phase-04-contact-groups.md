---
phase: 4
title: "Lệnh contacts group"
status: completed
priority: P1
effort: "3h"
dependencies: [1]
---

# Phase 4: Lệnh `contacts group`

## Goal
Quản lý contact group (Outlook DistListItem) bằng CLI: liệt kê, xem, tạo, thêm/bớt thành viên, xóa.

## Thiết kế lệnh

```
outlookctl contacts group list                          # mọi nhóm trên mọi store
outlookctl contacts group show   --name "Technical Team" [--store "Outlook Data File"]
outlookctl contacts group create --name "X" --members "a@b,c@d" [--store ...]
outlookctl contacts group add    --name "X" --members "a@b"
outlookctl contacts group remove --name "X" --members "a@b"
outlookctl contacts group delete --name "X" --confirm YES
```

- Tìm nhóm: duyệt `GetDefaultFolder(10)` (Contacts) của từng store trong `namespace.Stores`, lấy item có `Class == 69` (olDistributionList), so `DLName` không phân biệt hoa thường. Trùng tên ở nhiều store thì báo lỗi và yêu cầu `--store`.
- `create` mặc định tạo ở danh bạ mặc định (`namespace.GetDefaultFolder(10)`, trên máy này là `\\hoang.ho@tsp.com.vn\Contacts (This computer only)`, nơi đang chứa "Technical Team" từ 06/11/2026); `--store` để chọn store khác. Báo lỗi nếu tên đã tồn tại trên store đó.
- `add`/`remove`: dùng `CreateRecipient` + `Resolve()`; bỏ qua (và báo trong `skipped`) thành viên đã có khi add hoặc không có khi remove. Chuẩn hóa địa chỉ bằng `normalize_recipient` của phase 2 nếu phase 2 đã xong.
- `delete`: `item.Delete()` (chuyển vào Deleted Items, không xóa vĩnh viễn), bắt buộc `--confirm YES` như quy ước safety.
- Output JSON: `{name, store, members: [{name, email}], member_count}`; `list` trả mảng các object đó.

## Files to Create / Modify
- Modify: `D:\outlookctl\src\outlookctl\outlook_com.py` — `list_contact_groups`, `get_contact_group`, `create_contact_group`, `add_group_members`, `remove_group_members`, `delete_contact_group`, hằng `OL_FOLDER_CONTACTS = 10`, `OL_DISTRIBUTION_LIST = 69`
- Modify: `D:\outlookctl\src\outlookctl\models.py` — dataclass `ContactGroup`, `GroupMember` có `to_dict()`
- Modify: `D:\outlookctl\src\outlookctl\cli.py` — subparser `contacts` → `group` với các lệnh trên
- Create: `D:\outlookctl\tests\test_contact_group_models.py`

## Tasks & Steps
1. Thêm model và test `to_dict()`.
2. Thêm các hàm COM; hàm tìm nhóm dùng chung cho show/add/remove/delete.
3. Thêm subparser và handler, theo đúng mẫu xử lý lỗi/JSON của các lệnh hiện có (`output_json`, `output_error`).
4. Kiểm tra `Recipients.Add("Technical Team")` trong draft resolve ra nhóm (đã xác nhận bằng pywin32 ngày 06/11/2026: `AddressEntryUserType == 11`).

## Verification
- `uv run pytest tests/test_contact_group_models.py`
- Thủ công: `contacts group list` thấy "Technical Team" với 4 thành viên; `create --name "Zz Test"` → `add` → `show` → `remove` → `delete --confirm YES`; nhóm "Technical Team" không bị thay đổi.
