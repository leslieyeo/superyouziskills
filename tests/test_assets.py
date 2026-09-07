from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_report_fonts_resolve_offline():
    pages = [ROOT / 'skill/report/report.html', *sorted((ROOT / 'docs/examples').glob('*.html'))]
    for page in pages:
        text = page.read_text(encoding='utf-8')
        faces = re.findall(r'@font-face\s*\{(.*?)\}', text, re.S)
        assert faces, page
        for face in faces:
            for url in re.findall(r'url\("([^"]+)"\)', face):
                assert not url.startswith(('http:', 'https:', '//'))
                font = (page.parent / url).resolve()
                assert font.read_bytes()[:4] == b'\x00\x01\x00\x00'
                assert 'SIL OPEN FONT LICENSE' in (font.parent / 'OFL.txt').read_text()
