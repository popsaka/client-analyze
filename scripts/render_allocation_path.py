#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = 1600
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
    def __init__(self, height=1800):
        regular, bold = get_font_paths()
        self.regular = regular
        self.bold = bold
        self.height = height
        self.img = Image.new('RGB', (W, height), BG)
        self.d = ImageDraw.Draw(self.img)

    def F(self, size, bold=False):
        return ImageFont.truetype(self.bold if bold else self.regular, size)

    def txt(self, x, y, s, size=24, bold=False, fill=TEXT, anchor=None):
        self.d.text((x, y), str(s), font=self.F(size, bold), fill=fill, anchor=anchor)

    def rounded(self, x1, y1, x2, y2, fill=WHITE, outline=LINE, width=2, r=24):
        self.d.rounded_rectangle((x1, y1, x2, y2), radius=r, fill=fill, outline=outline, width=width)

    def chip_size(self, s, size=18, padx=16, pady=8):
        font = self.F(size)
        bb = self.d.textbbox((0, 0), str(s), font=font)
        w = bb[2] - bb[0] + padx * 2
        h = bb[3] - bb[1] + pady * 2
        return w, h

    def chip(self, x, y, s, color='blue', size=18, fg='white', padx=16, pady=8):
        fill = COLOR_MAP.get(color, color)
        w, h = self.chip_size(s, size=size, padx=padx, pady=pady)
        self.d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill)
        self.d.text((x + padx, y + pady - 1), str(s), font=self.F(size), fill=fg)
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
        return lines or ['']

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


# ---------- measurement helpers ----------

def para_height(r, s, maxw, size=22, gap=8, bold=False, max_lines=None):
    lines = r.wrap(s, maxw, size, bold)
    if max_lines:
        lines = lines[:max_lines]
    return len(lines) * (size + gap)


def chip_flow_height(r, chips, max_width, size=18, gap_x=10, gap_y=10):
    if not chips:
        return 0
    x0 = 0
    cx = x0
    cy = 0
    row_h = 0
    for chip in chips:
        text = chip.get('text', '') if isinstance(chip, dict) else str(chip)
        w, h = r.chip_size(text, size=size)
        if cx != x0 and cx + w > x0 + max_width:
            cx = x0
            cy += row_h + gap_y
            row_h = 0
        row_h = max(row_h, h)
        cx += w + gap_x
    return cy + row_h


def item_block_height(r, item, body_width):
    title_h = para_height(r, item.get('title', ''), body_width - 142, size=28, gap=6, bold=True)
    body_h = para_height(r, item.get('body', ''), body_width, size=22, gap=4, max_lines=None)
    chip_h = r.chip_size(item.get('label', 'Step'), size=18)[1]
    top_h = max(title_h, chip_h)
    return top_h + 12 + body_h + 14


def step3_card_height(r, card, card_width):
    inner_w = card_width - 32
    title_h = para_height(r, card.get('title', ''), inner_w, size=24, gap=6, bold=True)
    amount_h = r.chip_size(card.get('amount', ''), size=17)[1] if card.get('amount') else 0
    body_h = para_height(r, card.get('body', ''), inner_w, size=20, gap=4)
    gap1 = 8 if amount_h else 4
    gap2 = 8 if body_h else 0
    return 16 + title_h + gap1 + amount_h + gap2 + body_h + 16


def step3_grid_height(r, cards, grid_width):
    card_w = (grid_width - 24 - 28) / 2
    row_gap = 18
    total = 0
    for row_idx in range(0, min(len(cards), 4), 2):
        row_cards = cards[row_idx:row_idx + 2]
        row_h = max(step3_card_height(r, c, card_w) for c in row_cards)
        total += row_h
        if row_idx + 2 < min(len(cards), 4):
            total += row_gap
    return total


# ---------- payload ----------

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


# ---------- render ----------

def render(payload):
    p = build_payload(payload)
    m = R(400)

    x = 32
    cw = W - 64
    content_w = cw - 48
    box_pad_x = 24
    box_pad_y = 18
    section_gap = 22
    arrow_gap = 48
    footer_gap = 64

    # header
    header_y = 26
    header_h = 128

    # overview dynamic height
    overview_bullets_h = sum(para_height(m, '• ' + str(b), content_w, size=23, gap=8) for b in p['current_overview']['bullets'][:4])
    overview_chip_h = chip_flow_height(m, p['current_overview']['chips'][:4], content_w, size=18)
    overview_h = box_pad_y + 40 + 20 + overview_bullets_h + 16 + overview_chip_h + 18
    overview_h = max(overview_h, 220)

    # step1 dynamic height
    step1_items = p['step1'].get('items', [])[:3]
    step1_items_h = 0
    for i, item in enumerate(step1_items):
        step1_items_h += item_block_height(m, item, content_w)
        if i < len(step1_items) - 1:
            step1_items_h += 14
    step1_h = box_pad_y + 42 + 18 + step1_items_h + 18
    step1_h = max(step1_h, 220)

    # step2 dynamic height
    step2_chip_h = chip_flow_height(m, p['step2'].get('chips', [])[:5], content_w, size=18)
    step2_conc_h = para_height(m, p['step2'].get('conclusion', ''), content_w, size=22, gap=4)
    bar_h = 76
    step2_h = box_pad_y + 42 + 18 + 30 + 16 + step2_chip_h + 18 + bar_h + 20 + step2_conc_h + 18
    step2_h = max(step2_h, 300)

    # step3 dynamic height
    step3_cards = p['step3'].get('cards', [])[:4]
    step3_grid_h = step3_grid_height(m, step3_cards, cw)
    step3_final_h = para_height(m, p['step3'].get('final_recommendation', ''), content_w, size=24, gap=4, bold=True)
    step3_h = box_pad_y + 42 + 18 + step3_grid_h + 18 + step3_final_h + 20
    step3_h = max(step3_h, 260)

    total_h = header_y + header_h + section_gap + overview_h + section_gap + step1_h + arrow_gap + step2_h + arrow_gap + step3_h + footer_gap
    r = R(total_h)
    d = r.d

    # header
    r.rounded(28, header_y, W - 28, header_y + header_h, fill=NAVY, outline=NAVY, r=28)
    r.txt(58, header_y + 18, p['title'], 50, True, 'white')
    r.txt(58, header_y + 74, p['subtitle'], 21, False, '#CBD5E1')

    # overview
    overview_y = header_y + header_h + section_gap
    r.rounded(x, overview_y, x + cw, overview_y + overview_h, fill='#EEF4FF', outline='#C7D2FE')
    r.txt(x + 22, overview_y + 18, '当前资产概况', 34, True, NAVY)
    yy = overview_y + 74
    for bullet in p['current_overview']['bullets'][:4]:
        yy += r.para(x + 26, yy, '• ' + str(bullet), content_w, 23, TEXT, False, 8)
    chip_y = yy + 10
    chip_x = x + 24
    row_h = 0
    for chip in p['current_overview']['chips'][:4]:
        color = chip.get('color', 'blue') if isinstance(chip, dict) else 'blue'
        text = chip.get('text', '') if isinstance(chip, dict) else str(chip)
        w, h = r.chip_size(text, size=18)
        if chip_x != x + 24 and chip_x + w > x + 24 + content_w:
            chip_x = x + 24
            chip_y += row_h + 10
            row_h = 0
        r.chip(chip_x, chip_y, text, color=color, size=18)
        chip_x += w + 10
        row_h = max(row_h, h)

    # step1
    step1_y = overview_y + overview_h + section_gap
    r.rounded(x, step1_y, x + cw, step1_y + step1_h)
    r.txt(x + 24, step1_y + 18, '第1步｜' + p['step1']['title'], 38, True, NAVY)
    iy = step1_y + 78
    for idx, item in enumerate(step1_items):
        tag = item.get('label', f'Step {idx+1}')
        color = item.get('color', 'blue')
        tag_w, tag_h = r.chip(x + 28, iy, tag, color=color, size=18)
        title_h = r.para(x + 170, iy - 2, item.get('title', ''), content_w - 142, 28, NAVY, True, 6)
        top_h = max(tag_h, title_h)
        body_y = iy + top_h + 8
        body_h = r.para(x + 28, body_y, item.get('body', ''), content_w, 22, MUTED, False, 4)
        iy = body_y + body_h + 14

    # arrow 1
    arrow1_y1 = step1_y + step1_h
    arrow1_y2 = arrow1_y1 + arrow_gap - 8
    r.down_arrow(W // 2, arrow1_y1 + 4, arrow1_y2)

    # step2
    step2_y = step1_y + step1_h + arrow_gap
    r.rounded(x, step2_y, x + cw, step2_y + step2_h)
    r.txt(x + 24, step2_y + 18, '第2步｜' + p['step2']['title'], 38, True, NAVY)
    r.txt(x + 26, step2_y + 72, p['step2'].get('subtitle', ''), 26, True, TEXT)

    chip_x = x + 24
    chip_y = step2_y + 110
    row_h = 0
    for chip in p['step2'].get('chips', [])[:5]:
        text = chip.get('text', '') if isinstance(chip, dict) else str(chip)
        color = chip.get('color', 'blue') if isinstance(chip, dict) else 'blue'
        w, h = r.chip_size(text, size=18)
        if chip_x != x + 24 and chip_x + w > x + 24 + content_w:
            chip_x = x + 24
            chip_y += row_h + 10
            row_h = 0
        r.chip(chip_x, chip_y, text, color=color, size=18)
        chip_x += w + 10
        row_h = max(row_h, h)
    chips_bottom = chip_y + row_h

    # stacked bar
    bx1, bx2 = x + 24, x + cw - 24
    by1 = chips_bottom + 18
    by2 = by1 + bar_h
    segments = p['step2'].get('segments', [])
    total = sum(float(seg.get('percent', 0) or 0) for seg in segments) or 100.0
    cur_x = bx1
    for i, seg in enumerate(segments):
        pct = float(seg.get('percent', 0) or 0)
        w = (bx2 - bx1) * pct / total
        nx = bx2 if i == len(segments) - 1 else cur_x + w
        fill = seg.get('color') or SEGMENT_DEFAULTS[i % len(SEGMENT_DEFAULTS)]
        r.rounded(cur_x, by1, nx, by2, fill=fill, outline=fill, width=1, r=14)
        seg_w = nx - cur_x
        mid = (cur_x + nx) / 2
        title_size = 24 if seg_w >= 180 else 20
        amount_size = 18 if seg_w >= 180 else 16
        title_lines = r.wrap(seg.get('title', ''), max(seg_w - 20, 50), size=title_size, bold=True)[:2]
        line_gap = 4
        text_y = by1 + 10
        for j, line in enumerate(title_lines):
            r.txt(mid, text_y + j * (title_size + line_gap), line, title_size, True, 'white', anchor='ma')
        amount = seg.get('amount')
        if amount and seg_w >= 120:
            r.txt(mid, by1 + 42, str(amount), amount_size, False, 'white', anchor='ma')
            if seg_w >= 140:
                r.txt(mid, by1 + 62, f'{pct:.1f}%', 16, False, 'white', anchor='ma')
        elif seg_w >= 120:
            r.txt(mid, by1 + 52, f'{pct:.1f}%', 16, False, 'white', anchor='ma')
        cur_x = nx

    concl_y = by2 + 18
    r.para(x + 24, concl_y, p['step2'].get('conclusion', ''), content_w, 22, MUTED, False, 4)

    # arrow 2
    arrow2_y1 = step2_y + step2_h
    arrow2_y2 = arrow2_y1 + arrow_gap - 8
    r.down_arrow(W // 2, arrow2_y1 + 4, arrow2_y2)

    # step3
    step3_y = step2_y + step2_h + arrow_gap
    r.rounded(x, step3_y, x + cw, step3_y + step3_h)
    r.txt(x + 24, step3_y + 18, '第3步｜' + p['step3']['title'], 38, True, NAVY)

    card_w = (cw - 24 - 28) / 2
    grid_y = step3_y + 76
    row_gap = 18
    cards = step3_cards
    current_y = grid_y
    for row_idx in range(0, len(cards), 2):
        row_cards = cards[row_idx:row_idx + 2]
        row_h = max(step3_card_height(r, c, card_w) for c in row_cards)
        for col, card in enumerate(row_cards):
            cx = x + 24 + col * (card_w + 28)
            cy = current_y
            tone = card.get('tone', 'blue')
            card_h = step3_card_height(r, card, card_w)
            r.rounded(cx, cy, cx + card_w, cy + row_h, fill=SOFT_MAP.get(tone, '#F8FAFC'), outline='#D7DEE8')
            ty = cy + 14
            title_h = r.para(cx + 16, ty, card.get('title', ''), card_w - 32, 24, NAVY, True, 6)
            ay = ty + title_h + 6
            if card.get('amount'):
                chip_color = 'red' if tone == 'green' else ('orange' if tone == 'orange' else ('purple' if tone == 'purple' else 'blue'))
                _, chip_h = r.chip(cx + 16, ay, card.get('amount', ''), color=chip_color, size=17)
                by = ay + chip_h + 8
            else:
                by = ay + 4
            r.para(cx + 16, by, card.get('body', ''), card_w - 32, 20, MUTED, False, 4)
        current_y += row_h + row_gap
    current_y -= row_gap if cards else 0

    final_y = current_y + 18
    r.para(x + 24, final_y, p['step3'].get('final_recommendation', ''), content_w, 24, TEXT, True, 4)

    r.txt(W // 2, total_h - 24, p['footer'], 18, False, MUTED, anchor='mm')
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
