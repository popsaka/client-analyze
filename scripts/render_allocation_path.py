#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1500
BG = '#F6F8FB'
NAVY = '#0F172A'
TEXT = '#1E293B'
MUTED = '#64748B'
LINE = '#D9E2EC'
WHITE = '#FFFFFF'
ARROW = '#94A3B8'

COLOR_MAP = {
    'blue': '#2563EB',
    'red': '#DC2626',
    'green': '#22C55E',
    'orange': '#F59E0B',
    'purple': '#8B5CF6',
    'gray': '#94A3B8',
    'teal': '#14B8A6',
}
SOFT_MAP = {
    'blue': '#DBEAFE',
    'red': '#FEE2E2',
    'green': '#DCFCE7',
    'orange': '#FEF3C7',
    'purple': '#EDE9FE',
    'gray': '#E5E7EB',
    'teal': '#CCFBF1',
}
SEGMENT_DEFAULTS = ['#5B95E5', '#FF7A16', '#334155', '#22C55E', '#8B5CF6']


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def get_font_paths():
    regular = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    bold = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    return regular, bold


class R:
    def __init__(self):
        regular, bold = get_font_paths()
        self.regular = regular
        self.bold = bold
        self.img = Image.new('RGB', (W, H), BG)
        self.d = ImageDraw.Draw(self.img)

    def F(self, size, bold=False):
        return ImageFont.truetype(self.bold if bold else self.regular, size)

    def txt(self, x, y, s, size=24, bold=False, fill=TEXT, anchor=None):
        self.d.text((x, y), str(s), font=self.F(size, bold), fill=fill, anchor=anchor)

    def rounded(self, x1, y1, x2, y2, fill=WHITE, outline=LINE, width=2, r=24):
        self.d.rounded_rectangle((x1, y1, x2, y2), radius=r, fill=fill, outline=outline, width=width)

    def chip(self, x, y, s, color='blue', size=18, fg='white', padx=16, pady=8):
        fill = COLOR_MAP.get(color, color)
        font = self.F(size)
        bb = self.d.textbbox((0, 0), str(s), font=font)
        w = bb[2] - bb[0] + padx * 2
        h = bb[3] - bb[1] + pady * 2
        self.d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill)
        self.d.text((x + padx, y + pady - 1), str(s), font=font, fill=fg)
        return w, h

    def wrap(self, s, maxw, size=22, bold=False):
        font = self.F(size, bold)
        lines, cur = [], ''
        for ch in str(s):
            test = cur + ch
            if self.d.textlength(test, font=font) <= maxw:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, maxw, size=22, fill=TEXT, bold=False, gap=8, max_lines=None):
        lines = self.wrap(s, maxw, size, bold)
        if max_lines:
            lines = lines[:max_lines]
        for i, line in enumerate(lines):
            self.txt(x, y + i * (size + gap), line, size, bold, fill)
        return len(lines) * (size + gap)

    def down_arrow(self, x, y1, y2):
        self.d.line((x, y1, x, y2 - 18), fill=ARROW, width=5)
        self.d.polygon([(x - 10, y2 - 22), (x + 10, y2 - 22), (x, y2)], fill=ARROW)


def build_payload(payload):
    payload.setdefault('title', '客户配置建议路径')
    payload.setdefault('subtitle', '按需求顺序：先满足明确需求，再重评估，再做补齐配置')
    payload.setdefault('current_overview', {})
    payload['current_overview'].setdefault('bullets', [])
    payload['current_overview'].setdefault('chips', [])
    payload.setdefault('step1', {'title': '先满足客户明确点名的需求', 'items': []})
    payload.setdefault('step2', {'title': '完成以上两步后，先重新评估客户配置', 'subtitle': '重新评估后的组合（工作版）', 'chips': [], 'segments': [], 'conclusion': ''})
    payload.setdefault('step3', {'title': '继续做配置完善', 'cards': [], 'final_recommendation': ''})
    payload.setdefault('footer', '注：以上为工作版配置建议路径，正式执行前需结合产品可得性、合规与执行 SLA 校正。')
    return payload


def render(payload):
    p = build_payload(payload)
    r = R()
    d = r.d

    # header
    r.rounded(28, 26, W - 28, 118, fill=NAVY, outline=NAVY, r=28)
    r.txt(58, 48, p['title'], 50, True, 'white')
    r.txt(58, 94, p['subtitle'], 23, False, '#CBD5E1')

    # overview
    y = 142
    x = 32
    cw = W - 64
    r.rounded(x, y, x + cw, y + 298, fill='#EEF4FF', outline='#C7D2FE')
    r.txt(x + 22, y + 18, '当前资产概况', 34, True, NAVY)
    oy = y + 74
    for i, bullet in enumerate(p['current_overview']['bullets'][:4]):
        r.txt(x + 26, oy + i * 32, '• ' + str(bullet), 23, False, TEXT)
    chip_x = x + 24
    chip_y = y + 236
    for chip in p['current_overview']['chips'][:4]:
        color = chip.get('color', 'blue') if isinstance(chip, dict) else 'blue'
        text = chip.get('text', '') if isinstance(chip, dict) else str(chip)
        w, _ = r.chip(chip_x, chip_y, text, color=color, size=18)
        chip_x += w + 10

    # step1
    y1 = 470
    r.rounded(x, y1, x + cw, y1 + 250)
    r.txt(x + 24, y1 + 18, '第1步｜' + p['step1']['title'], 38, True, NAVY)
    sy = y1 + 76
    for i, item in enumerate(p['step1']['items'][:3]):
        tag = item.get('label', f'Step {i+1}')
        color = item.get('color', 'blue')
        r.chip(x + 28, sy + i * 92, tag, color=color, size=18)
        r.txt(x + 170, sy - 2 + i * 92, item.get('title', ''), 28, True, NAVY)
        r.para(x + 28, sy + 34 + i * 92, item.get('body', ''), cw - 56, 22, MUTED, False, 4, 2)

    r.down_arrow(W // 2, y1 + 250, 770)

    # step2
    y2 = 770
    r.rounded(x, y2, x + cw, y2 + 338)
    r.txt(x + 24, y2 + 18, '第2步｜' + p['step2']['title'], 38, True, NAVY)
    r.txt(x + 26, y2 + 72, p['step2'].get('subtitle', ''), 26, True, TEXT)
    chip_x = x + 24
    chip_y = y2 + 110
    for chip in p['step2'].get('chips', [])[:5]:
        text = chip.get('text', '') if isinstance(chip, dict) else str(chip)
        color = chip.get('color', 'blue') if isinstance(chip, dict) else 'blue'
        w, _ = r.chip(chip_x, chip_y, text, color=color, size=18)
        chip_x += w + 10

    # stacked bar
    bx1, by1, bx2, by2 = x + 24, y2 + 160, x + cw - 24, y2 + 236
    segments = p['step2'].get('segments', [])
    total = sum(float(seg.get('percent', 0) or 0) for seg in segments) or 100.0
    cur_x = bx1
    for i, seg in enumerate(segments):
        pct = float(seg.get('percent', 0) or 0)
        w = (bx2 - bx1) * pct / total
        if i == len(segments) - 1:
            nx = bx2
        else:
            nx = cur_x + w
        fill = seg.get('color') or SEGMENT_DEFAULTS[i % len(SEGMENT_DEFAULTS)]
        r.rounded(cur_x, by1, nx, by2, fill=fill, outline=fill, width=1, r=14)
        mid = (cur_x + nx) / 2
        r.txt(mid, by1 + 16, seg.get('title', ''), 24, True, 'white', anchor='ma')
        amount = seg.get('amount')
        if amount:
            r.txt(mid, by1 + 44, str(amount), 18, False, 'white', anchor='ma')
            r.txt(mid, by1 + 66, f"{pct:.1f}%", 18, False, 'white', anchor='ma')
        else:
            r.txt(mid, by1 + 54, f"{pct:.1f}%", 18, False, 'white', anchor='ma')
        cur_x = nx
    r.para(x + 24, y2 + 258, p['step2'].get('conclusion', ''), cw - 48, 22, MUTED, False, 4, 2)

    r.down_arrow(W // 2, y2 + 338, 1130)

    # step3
    y3 = 1130
    r.rounded(x, y3, x + cw, y3 + 286)
    r.txt(x + 24, y3 + 18, '第3步｜' + p['step3']['title'], 38, True, NAVY)
    cards = p['step3'].get('cards', [])
    card_w = (cw - 24 - 28) / 2
    for i, card in enumerate(cards[:4]):
        col = i % 2
        row = i // 2
        cx = x + 24 + col * (card_w + 28)
        cy = y3 + 74 + row * 118
        tone = card.get('tone', 'blue')
        r.rounded(cx, cy, cx + card_w, cy + 102, fill=SOFT_MAP.get(tone, '#F8FAFC'), outline='#D7DEE8')
        r.txt(cx + 16, cy + 10, card.get('title', ''), 24, True, NAVY)
        if card.get('amount'):
            r.chip(cx + 16, cy + 42, card.get('amount', ''), color='red' if tone == 'green' else ('orange' if tone == 'orange' else 'blue'), size=17)
        r.para(cx + 16, cy + 70, card.get('body', ''), card_w - 32, 20, MUTED, False, 4, 2)
    r.para(x + 24, y3 + 246, p['step3'].get('final_recommendation', ''), cw - 48, 24, TEXT, True, 4, 2)

    r.txt(W // 2, H - 22, p['footer'], 18, False, MUTED, anchor='mm')
    return r.img


def main():
    parser = argparse.ArgumentParser(description='Render private-banking allocation path from structured JSON.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--pdf')
    args = parser.parse_args()

    payload = load_json(Path(args.input))
    img = render(payload)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    if args.pdf:
        pdf = Path(args.pdf)
        pdf.parent.mkdir(parents=True, exist_ok=True)
        img.convert('RGB').save(pdf, 'PDF', resolution=150.0)
    print(out)
    if args.pdf:
        print(args.pdf)


if __name__ == '__main__':
    main()
