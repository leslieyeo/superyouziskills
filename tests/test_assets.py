from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FONT_CDN = "cdn.jsdelivr.net/gh/tw93/MiaoYan-NetNewsWire-Theme"
BROKEN_FONT_CDN = "AlfredoSequeworthy/TsangerJinKai02"


def test_html_templates_do_not_reference_broken_font_cdn():
    for rel in ("skill/report/report.html",):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert BROKEN_FONT_CDN not in text
        assert FONT_CDN in text
