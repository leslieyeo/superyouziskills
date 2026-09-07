"""生成当前页面所需的网页字体子集。依赖：pip install fonttools brotli
用法：python3 scripts/build_font.py /path/to/LXGWWenKaiScreen.ttf
字体来源与授权见 assets/fonts/README.md。
"""
from pathlib import Path
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]

def build(source):
    pages = [ROOT / 'index.html', *sorted((ROOT / 'sales/样报').glob('*.html'))]
    text = ''.join(p.read_text(encoding='utf-8') for p in pages)
    font = TTFont(source)
    # 衍生字体使用新名称；版权、来源与许可证记录保持不变。
    names = {1: 'Superyouzi Reading', 3: 'SuperyouziReading-Web-1.522',
             4: 'Superyouzi Reading Regular', 6: 'SuperyouziReading-Regular',
             16: 'Superyouzi Reading', 18: 'Superyouzi Reading Regular',
             21: 'Superyouzi Reading', 25: 'SuperyouziReading'}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    opts = subset.Options()
    opts.name_IDs = ['*']
    opts.name_legacy = True
    opts.name_languages = ['*']
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = 'woff2'
    out = ROOT / 'assets/fonts/superyouzi-reading.woff2'
    font.save(out)
    print(f'{out}: {out.stat().st_size:,} bytes')

if __name__ == '__main__':
    build(sys.argv[1])
