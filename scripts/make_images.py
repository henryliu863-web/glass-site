# -*- coding: utf-8 -*-
"""生成站点用到的占位图片（SVG）。换成真实图片时直接覆盖 static/img 下的同名文件，
或在后台给产品上传图片即可。运行：python scripts/make_images.py"""
import os
import random

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img")
FONT = "Arial, 'Microsoft YaHei', sans-serif"


def save(name, svg):
    path = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{rect}{body}</svg>')


METAL = ('<linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f5f7"/>'
         '<stop offset=".5" stop-color="#b9bdc4"/><stop offset="1" stop-color="#e6e8eb"/></linearGradient>')

# ---------------------------------------------------------------- banners
banner1 = svg(1000, 352, f"""
<defs>{METAL}</defs>
<rect width="1000" height="352" fill="#1d1d1d"/>
<polygon points="0,240 1000,120 1000,352 0,352" fill="#F7E300"/>
<g fill="#F7E300">{''.join(f'<polygon points="{330+i*46},352 {370+i*46},352 {470+i*46},250 {430+i*46},250"/>' for i in range(5))}</g>
<g fill="#fff" opacity=".9">{''.join(f'<polygon points="{560+i*60},250 {585+i*60},250 {640+i*60},190 {615+i*60},190"/>' for i in range(4))}</g>
<text x="58" y="112" font-family="Georgia, serif" font-weight="bold" font-style="italic" font-size="58" fill="#F7E300">GLASS DOOR</text>
<text x="104" y="160" font-family="Georgia, serif" font-weight="bold" font-size="26" fill="#F7E300" letter-spacing="2">CONTROL HARDWARE</text>
<text x="104" y="196" font-family="{FONT}" font-size="18" fill="#ddd" letter-spacing="6">玻璃门控五金 · 品质之选</text>
<g transform="translate(640 60)">
  <rect x="0" y="40" width="170" height="70" rx="8" fill="url(#m)" stroke="#888"/>
  <rect x="20" y="58" width="130" height="34" rx="4" fill="#d9dce0" stroke="#999"/>
  <circle cx="40" cy="75" r="6" fill="#777"/><circle cx="130" cy="75" r="6" fill="#777"/>
  <rect x="200" y="20" width="60" height="140" rx="30" fill="url(#m)" stroke="#888"/>
  <rect x="90" y="150" width="200" height="40" rx="6" fill="url(#m)" stroke="#888"/>
</g>""")

banner2 = svg(1000, 352, f"""
<defs>{METAL}<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef0f3"/><stop offset="1" stop-color="#9ea3aa"/></linearGradient></defs>
<rect width="1000" height="352" fill="url(#bg)"/>
<g transform="rotate(-18 500 176)">
  <rect x="80" y="150" width="820" height="56" rx="6" fill="url(#m)" stroke="#8a8f96"/>
  <rect x="120" y="162" width="300" height="32" rx="4" fill="#cfd3d8"/>
  <circle cx="860" cy="178" r="12" fill="#999"/><circle cx="170" cy="178" r="7" fill="#777"/>
</g>
<g transform="translate(40 40)"><rect width="170" height="120" rx="10" fill="url(#m)" stroke="#888"/><circle cx="60" cy="60" r="24" fill="#c4c8cd" stroke="#888"/></g>
<g transform="translate(700 150)"><rect width="230" height="110" rx="12" fill="url(#m)" stroke="#888"/><circle cx="190" cy="55" r="30" fill="#d0d3d7" stroke="#888"/></g>
<text x="60" y="320" font-family="{FONT}" font-size="26" font-weight="bold" fill="#333">玻璃切割工具 · 门控五金</text>
""")

about = svg(469, 200, f"""
<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfeefc"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<linearGradient id="a" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#1b5fae"/><stop offset="1" stop-color="#6db3f2"/></linearGradient></defs>
<rect width="469" height="200" fill="url(#s)"/>
<path d="M120 200 Q 260 170 330 70 L 310 62 L 370 30 L 365 96 L 346 82 Q 300 170 200 200 Z" fill="url(#a)"/>
<circle cx="250" cy="215" r="80" fill="#3c7fc2" opacity=".35"/>
<text x="18" y="38" font-family="{FONT}" font-size="20" font-weight="bold" fill="#222">跨越发展 ➤</text>
<text x="18" y="56" font-family="{FONT}" font-size="9" font-weight="bold" fill="#333">COMPANY DEVELOPMENT</text>
<text x="18" y="74" font-family="{FONT}" font-size="9" fill="#666">专注玻璃工具与五金配件</text>
<text x="18" y="88" font-family="{FONT}" font-size="9" fill="#666">诚信经营 · 品质为本</text>
<g fill="#444">{''.join(f'<path d="M{40+i*22} {150-i*6} q6 -6 12 0 q-6 -3 -12 0z"/>' for i in range(4))}</g>
""")

ad = svg(735, 122, f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2d3e8c"/><stop offset=".55" stop-color="#9aa9d9"/><stop offset="1" stop-color="#f3d9c7"/></linearGradient></defs>
<rect width="735" height="122" fill="url(#g)"/>
<g fill="#fff" opacity=".55"><ellipse cx="620" cy="40" rx="70" ry="18"/><ellipse cx="690" cy="90" rx="60" ry="14"/><ellipse cx="520" cy="100" rx="50" ry="10"/></g>
<text x="170" y="60" font-family="{FONT}" font-size="30" font-weight="bold" fill="#fff" letter-spacing="4">品质铸就品牌 / 服务赢得市场</text>
<text x="170" y="92" font-family="{FONT}" font-size="15" font-weight="bold" fill="#fff" letter-spacing="2">Quality Builds the Brand · Service Wins the Market</text>
<g transform="translate(28 18)" fill="#1b1b2a" opacity=".85"><rect x="0" y="40" width="110" height="46" rx="6"/><rect x="18" y="12" width="74" height="32" rx="4"/><circle cx="25" cy="88" r="10"/><circle cx="85" cy="88" r="10"/></g>
""")

save("banner1.svg", banner1)
save("banner2.svg", banner2)
save("about.svg", about)
save("ad.svg", ad)

# ---------------------------------------------------------------- 生产设备
for i, (label, color) in enumerate([("数控切割机", "#5b6b7a"), ("磨边机", "#6a5b4f"), ("钻孔机", "#4f6a5b"),
                                     ("包装生产线", "#5b4f6a")], 1):
    save(f"equip{i}.svg", svg(249, 162, f"""
<rect width="249" height="162" fill="#e9eaec"/>
<rect x="0" y="130" width="249" height="32" fill="#c9ccd0"/>
<rect x="34" y="52" width="180" height="80" rx="6" fill="{color}"/>
<rect x="48" y="64" width="70" height="40" rx="3" fill="#9fb4c6"/>
<rect x="132" y="64" width="66" height="10" fill="#F7E300"/>
<circle cx="150" cy="100" r="14" fill="#ddd" stroke="#333"/>
<rect x="60" y="28" width="12" height="26" fill="#777"/><rect x="40" y="22" width="120" height="10" fill="#888"/>
<text x="124" y="152" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#333">{label}</text>
"""))

# ---------------------------------------------------------------- 其他
random.seed(7)
cells = "".join(f'<rect x="{4+x*4}" y="{4+y*4}" width="4" height="4"/>' for x in range(13) for y in range(13)
                if random.random() > .55 and not (x < 4 and y < 4) and not (x > 8 and y < 4) and not (x < 4 and y > 8))
finder = "".join(f'<rect x="{x}" y="{y}" width="16" height="16" fill="none" stroke="#000" stroke-width="3"/>'
                 f'<rect x="{x+5}" y="{y+5}" width="6" height="6"/>' for x, y in [(4, 4), (40, 4), (4, 40)])
save("qrcode.svg", svg(60, 60, f'<g fill="#000">{cells}{finder}</g>', bg="#fff"))

save("service.svg", svg(110, 150, """
<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a3a"/><stop offset="1" stop-color="#151515"/></linearGradient></defs>
<path d="M0 150 Q 8 96 55 92 Q 102 96 110 150 Z" fill="url(#c)"/>
<path d="M44 92 L55 112 L66 92 Z" fill="#fff"/>
<circle cx="55" cy="58" r="26" fill="#f2d2bd"/>
<path d="M28 58 Q 26 26 55 24 Q 86 26 82 62 Q 78 40 55 38 Q 34 40 28 58 Z" fill="#2b1d16"/>
<path d="M27 60 Q 27 30 55 30 Q 83 30 83 60" fill="none" stroke="#333" stroke-width="3"/>
<rect x="22" y="54" width="8" height="14" rx="3" fill="#333"/><rect x="80" y="54" width="8" height="14" rx="3" fill="#333"/>
<path d="M26 68 Q 30 84 48 80" fill="none" stroke="#333" stroke-width="2"/>
"""))

save("noimg.svg", svg(122, 122, f'<text x="61" y="66" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#999">暂无图片</text>', bg="#f3f3f3"))

# ---------------------------------------------------------------- 产品图（8 类 × 3）
COLORS = ["#F2B705", "#2E86C1", "#C0392B"]


def product(kind, c):
    d = f"<defs>{METAL}</defs>"
    if kind == "cutter":   # 玻璃刀：塑柄 + 金属刀头
        b = (f'<g transform="rotate(-30 100 100)"><rect x="30" y="88" width="120" height="24" rx="10" fill="{c}" stroke="#555"/>'
             f'<rect x="146" y="91" width="30" height="18" rx="3" fill="url(#m)" stroke="#666"/>'
             f'<circle cx="178" cy="100" r="5" fill="#999" stroke="#555"/><rect x="40" y="95" width="60" height="4" fill="#fff" opacity=".5"/></g>')
    elif kind == "wheel":  # 刀轮
        b = (f'<circle cx="100" cy="100" r="58" fill="url(#m)" stroke="#666" stroke-width="2"/>'
             f'<circle cx="100" cy="100" r="40" fill="none" stroke="{c}" stroke-width="6"/>'
             f'<circle cx="100" cy="100" r="12" fill="#fff" stroke="#666" stroke-width="2"/>')
    elif kind == "sucker":  # 吸盘
        b = (f'<ellipse cx="60" cy="140" rx="40" ry="12" fill="#333"/><ellipse cx="140" cy="140" rx="40" ry="12" fill="#333"/>'
             f'<rect x="50" y="88" width="100" height="22" rx="6" fill="url(#m)" stroke="#666"/>'
             f'<rect x="56" y="110" width="8" height="26" fill="#888"/><rect x="136" y="110" width="8" height="26" fill="#888"/>'
             f'<rect x="70" y="70" width="60" height="18" rx="4" fill="{c}"/>')
    elif kind == "drill":  # 钻头
        b = (f'<rect x="92" y="20" width="16" height="70" fill="url(#m)" stroke="#666"/>'
             f'<path d="M86 90 L114 90 L112 160 L100 180 L88 160 Z" fill="{c}" stroke="#555"/>'
             f'<path d="M90 110 L110 120 M90 130 L110 140 M90 150 L110 158" stroke="#fff" stroke-width="2" opacity=".6"/>')
    elif kind == "spring":  # 地弹簧
        b = (f'<rect x="30" y="70" width="140" height="60" rx="6" fill="url(#m)" stroke="#666"/>'
             f'<rect x="40" y="82" width="120" height="36" rx="3" fill="#c9cdd2"/>'
             f'<circle cx="140" cy="100" r="12" fill="{c}" stroke="#555"/><rect x="134" y="50" width="12" height="22" fill="#777"/>')
    elif kind == "clip":  # 门夹
        b = (f'<rect x="40" y="70" width="120" height="60" rx="4" fill="url(#m)" stroke="#666"/>'
             f'<rect x="40" y="96" width="120" height="8" fill="{c}" opacity=".7"/>'
             f'<circle cx="60" cy="86" r="5" fill="#777"/><circle cx="140" cy="86" r="5" fill="#777"/>')
    elif kind == "lock":  # 门锁
        b = (f'<rect x="50" y="80" width="100" height="70" rx="6" fill="url(#m)" stroke="#666"/>'
             f'<path d="M70 80 V60 Q100 30 130 60 V80" fill="none" stroke="#666" stroke-width="8"/>'
             f'<circle cx="100" cy="110" r="9" fill="{c}"/><rect x="97" y="114" width="6" height="18" fill="{c}"/>')
    else:  # closer 闭门器
        b = (f'<rect x="20" y="60" width="120" height="40" rx="6" fill="url(#m)" stroke="#666"/>'
             f'<rect x="60" y="104" width="120" height="14" rx="5" fill="url(#m)" stroke="#666" transform="rotate(12 60 110)"/>'
             f'<circle cx="60" cy="108" r="9" fill="{c}" stroke="#555"/>')
    return svg(200, 200, d + b, bg="#ffffff")


for kind in ["cutter", "wheel", "sucker", "drill", "spring", "clip", "lock", "closer"]:
    for i, c in enumerate(COLORS, 1):
        save(f"products/{kind}-{i}.svg", product(kind, c))

print("images written to", ROOT)
