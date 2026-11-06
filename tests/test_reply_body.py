"""Tests for inserting new content above quoted mail bodies."""

from outlookctl.utils import insert_into_html_body, text_to_html_fragment


class TestTextToHtmlFragment:
    def test_escapes_and_keeps_line_breaks(self):
        fragment = text_to_html_fragment("a < b & c\nline 2")
        assert "a &lt; b &amp; c<br>\nline 2" in fragment
        assert fragment.startswith("<div style=")

    def test_windows_newlines(self):
        assert "x<br>\ny" in text_to_html_fragment("x\r\ny")

    def test_vietnamese_text_kept(self):
        assert "Báo cáo tuần" in text_to_html_fragment("Báo cáo tuần")


class TestInsertIntoHtmlBody:
    def test_inserts_after_body_tag_with_attributes(self):
        doc = '<html><head></head><body lang=EN-US link="#0563C1"><p>quoted</p></body></html>'
        result = insert_into_html_body(doc, "<p>new</p>")
        assert result == '<html><head></head><body lang=EN-US link="#0563C1"><p>new</p><p>quoted</p></body></html>'

    def test_body_tag_case_insensitive(self):
        assert insert_into_html_body("<BODY><p>q</p></BODY>", "N") == "<BODY>N<p>q</p></BODY>"

    def test_does_not_match_tbody(self):
        doc = "<table><tbody><tr></tr></tbody></table>"
        assert insert_into_html_body(doc, "N") == "N" + doc

    def test_no_body_tag_prepends(self):
        assert insert_into_html_body("<p>q</p>", "N") == "N<p>q</p>"

    def test_empty_document(self):
        assert insert_into_html_body("", "N") == "N"
        assert insert_into_html_body(None, "N") == "N"
