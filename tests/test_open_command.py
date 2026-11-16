"""Tests for the open command."""


class TestOpenResult:
    def test_to_dict(self):
        from outlookctl.models import OpenResult

        result = OpenResult(
            message="Item opened in Outlook",
            subject="RE: [BCT] - Báo cáo tuần",
            message_class="IPM.Note",
        )
        assert result.to_dict() == {
            "version": "1.0",
            "success": True,
            "message": "Item opened in Outlook",
            "subject": "RE: [BCT] - Báo cáo tuần",
            "message_class": "IPM.Note",
        }


class TestOpenItem:
    def test_displays_non_modal_and_returns_subject(self, monkeypatch):
        from outlookctl import outlook_com

        calls = []

        class FakeItem:
            Subject = "Draft"
            MessageClass = "IPM.Note"

            def Display(self, modal):
                calls.append(modal)

        monkeypatch.setattr(outlook_com, "get_message_by_id", lambda *a: FakeItem())
        assert outlook_com.open_item(None, "e", "s") == ("Draft", "IPM.Note")
        assert calls == [False]
