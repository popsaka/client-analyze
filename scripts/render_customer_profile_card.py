#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2860
BG = '#F6F8FB'
NAVY = '#0F172A'
TEXT = '#1E293B'
MUTED = '#64748B'
LINE = '#E2E8F0'
WHITE = '#FFFFFF'
BLUE = '#2563EB'
GREEN = '#16A34A'
ORANGE = '#EA580C'
RED = '#DC2626'
SOFT = '#FBFDFF'
BLUE_LIGHT = '#CBD5E1'

BUCKET_LABELS = {
    'B0': '现金管理',
    'B1': '低波收益',
    'B2': '中波增长',
    'B3': '高波增长',
    'B4': '超高波机会',
    'B5': '抗通胀对冲',
}

PRESETS = {
    '保守保值': {'B0': 35, 'B1': 35, 'B2': 15, 'B3': 5, 'B4': 0, 'B5': 10},
    '稳健增值': {'B0': 20, 'B1': 30, 'B2': 25, 'B3': 10, 'B4': 5, 'B5': 10},
    '平衡增长': {'B0': 12, 'B1': 18, 'B2': 35, 'B3': 20, 'B4': 5, 'B5': 10},
    '进取增长': {'B0': 7, 'B1': 7, 'B2': 15, 'B3': 50, 'B4': 15, 'B5': 6},
}

SEVERITY_COLOR = {
    '高': RED,
    '中': ORANGE,
    '低': GREEN,
    '红': RED,
    '橙': ORANGE,
    '绿': GREEN,
}

RAW_BUCKET_KEYWORDS = {
    'B0': ['现金', '稳定币', '货基', 'money market', 'cash', 'usdt', 'usdc'],
    'B1': ['固收', '债', '存款', '票息', '理财', 'bond', 'fixed income', 'treasury'],
    'B2': ['宽基', 'etf', '美股', '股票', '权益', 'equity', 'stock'],
    'B3': ['btc', 'eth', 'bitcoin', 'ethereum'],
    'B4': ['小币', '期权', '杠杆', '主题', 'alpha', 'sol', 'meme', 'derivative'],
    'B5': ['黄金', '商品', 'cta', '对冲', 'gold', 'commodity', 'hedge'],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def get_font_paths():
    regular = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    bold = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    return regular, bold


class CardRenderer:
    def __init__(self, height):
        regular, bold = get_font_paths()
        self.regular = regular
        self.bold = bold
        self.height = height
        self.img = Image.new('RGB', (W, height), BG)
        self.d = ImageDraw.Draw(self.img)

    def F(self, size, bold=False):
        return ImageFont.truetype(self.bold if bold else self.regular, size)

    def rounded(self, x1, y1, x2, y2, fill=WHITE, outline=LINE, width=2, r=24):
        self.d.rounded_rectangle((x1, y1, x2, y2), radius=r, fill=fill, outline=outline, width=width)

    def txt(self, x, y, s, size=24, bold=False, fill=TEXT, anchor=None):
        self.d.text((x, y), s, font=self.F(size, bold), fill=fill, anchor=anchor)

    def chip(self, x, y, s, color, fg='white', size=18, padx=16, pady=8):
        font = self.F(size)
        bb = self.d.textbbox((0, 0), s, font=font)
        w = bb[2] - bb[0] + padx * 2
        h = bb[3] - bb[1] + pady * 2
        self.d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=color)
        self.d.text((x + padx, y + pady - 1), s, font=font, fill=fg)
        return w, h

    def wrap(self, s, maxw, size=22):
        font = self.F(size)
        lines, cur = [], ''
        for ch in s:
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

    def draw_para(self, x, y, s, maxw, size=22, fill=TEXT, bold=False, gap=8, max_lines=None):
        lines = self.wrap(s, maxw, size)
        if max_lines:
            lines = lines[:max_lines]
        for i, line in enumerate(lines):
            self.txt(x, y + i * (size + gap), line, size, bold, fill)
        return len(lines) * (size + gap)


def normalize_alloc(values):
    out = {k: float(values.get(k, 0) or 0) for k in BUCKET_LABELS}
    return out


def map_raw_assets(raw_assets):
    acc = {k: 0.0 for k in BUCKET_LABELS}
    for item in raw_assets:
        name = str(item.get('name', '')).lower()
        pct = float(item.get('percent', 0) or 0)
        matched = None
        for bucket, words in RAW_BUCKET_KEYWORDS.items():
            if any(w in name for w in words):
                matched = bucket
                break
        if not matched:
            matched = 'B4'
        acc[matched] += pct
    return acc


def choose_recommended(payload, current):
    allocation = payload.setdefault('allocation', {})
    if allocation.get('recommended'):
        return normalize_alloc(allocation['recommended'])
    preset = allocation.get('recommended_preset') or payload.get('profile', {}).get('style')
    if preset and preset in PRESETS:
        return PRESETS[preset].copy()
    return PRESETS['进取增长'].copy()


def describe_structure(current, recommended):
    diffs = {k: round(current.get(k, 0) - recommended.get(k, 0), 1) for k in BUCKET_LABELS}
    overs = sorted([(k, v) for k, v in diffs.items() if v > 0.1], key=lambda x: x[1], reverse=True)
    unders = sorted([(k, -v) for k, v in diffs.items() if v < -0.1], key=lambda x: -x[1], reverse=True)
    over_txt = '、'.join([f"{k}（{BUCKET_LABELS[k]}）过配 +{int(v) if v.is_integer() else v}pct" for k, v in overs[:2]]) or '无明显过配'
    under_txt = '、'.join([f"{k}（{BUCKET_LABELS[k]}）缺口 {int(v) if v.is_integer() else v}pct" for k, v in unders[:3]]) or '无明显缺口'
    return f'结构结论：{over_txt}；{under_txt}。问题不只是激进，而是分层配置不足。'


def default_core_conclusion(payload):
    diagnostics = payload.get('diagnostics', [])
    risk_diag = next((d for d in diagnostics if '风险' in d.get('title', '')), None)
    current = risk_diag.get('current', '当前组合波动较高') if risk_diag else '当前组合波动较高'
    pref = risk_diag.get('preference', '风险预算偏低') if risk_diag else '风险预算偏低'
    return {
        'lines': [
            '客户行为并不矛盾，反而体现出较清晰的风险边界；',
            f'真正的错配在于当前组合特征（{current}）与其风险目标（{pref}）不一致。',
        ],
        'chips': [
            {'text': '行为纪律：基本一致', 'color': 'green'},
            {'text': '组合结构：明显错配', 'color': 'red'},
        ],
    }


def build_payload(payload):
    allocation = payload.setdefault('allocation', {})
    if not allocation.get('current') and allocation.get('raw_assets'):
        allocation['current'] = map_raw_assets(allocation['raw_assets'])
    allocation['current'] = normalize_alloc(allocation.get('current', {}))
    allocation['recommended'] = choose_recommended(payload, allocation['current'])
    allocation.setdefault('bucket_labels', BUCKET_LABELS.copy())
    allocation.setdefault('structure_conclusion', describe_structure(allocation['current'], allocation['recommended']))

    payload.setdefault('profile', {})
    payload['profile'].setdefault('tags', [])
    payload['profile'].setdefault('one_liner', '待补充')

    payload.setdefault('preferences', [])
    payload.setdefault('diagnostics', [])
    payload.setdefault('behavior_lines', [])
    payload.setdefault('actions', [])
    payload.setdefault('footer', '注：收益 / 回撤与推荐均衡配置为基于问卷回答的顾问粗估 / 模板示意，用于画像卡演示，不构成收益承诺。')
    payload.setdefault('title', '私行客户画像卡')
    payload.setdefault('subtitle', '基于问卷回答生成｜使用 draw-customer-profile-card skill')
    payload.setdefault('core_conclusion', default_core_conclusion(payload))
    return payload


def render(payload):
    payload = build_payload(payload)

    # pre-compute dynamic height so the last section never collides with the footer
    one_liner = str(payload.get('profile', {}).get('one_liner', '待补充'))
    tmp_r = CardRenderer(400)
    one_liner_lines = tmp_r.wrap(one_liner, 520, 22)[:3]
    s1_h = max(320, 252 + len(one_liner_lines) * 26 + 52)
    s2_h = max(220, 84 + len(payload.get('preferences', [])) * 26 + 26)
    s3_h = 610
    s4_h = 250
    diagnostics = payload.get('diagnostics', [])
    s5_h = 110 + max(1, len(diagnostics)) * 102
    behavior_lines = payload.get('behavior_lines', [])
    s6_h = max(180, 86 + len(behavior_lines) * 34 + 26)
    actions = payload.get('actions', [])
    s7_h = max(200, 88 + len(actions) * 50 + 26)
    total_height = 176 + (s1_h + 20) + (s2_h + 20) + (s3_h + 20) + (s4_h + 20) + (s5_h + 20) + (s6_h + 20) + (s7_h + 20) + 120
    render_h = max(H, total_height)

    r = CardRenderer(render_h)
    d = r.d

    # header
    r.rounded(34, 28, W - 34, 150, fill=NAVY, outline=NAVY, r=30)
    r.txt(68, 54, payload['title'], 50, True, 'white')
    r.txt(68, 108, payload.get('subtitle', ''), 24, False, '#CBD5E1')
    r.chip(W - 210, 66, payload.get('version', 'skill'), BLUE, size=22)

    x = 42
    cw = W - 84
    y = 176
    bottom_margin = 90

    def section(title_num, title_text, h):
        nonlocal y
        r.rounded(x, y, x + cw, y + h)
        r.txt(x + 26, y + 18, f'{title_num:02d} {title_text}', 34, True, NAVY)
        top = y
        y += h + 20
        return top

    # 01
    profile = payload['profile']
    one_liner = str(profile.get('one_liner', '待补充'))
    one_liner_lines = r.wrap(one_liner, 520, 22)[:3]
    s1 = section(1, '客户定位', s1_h)
    left = x + 28
    valx = x + 218
    simple_rows = [
        ('客户类型', profile.get('client_type', '待补充')),
        ('资产规模', profile.get('aum', '待补充')),
        ('投资经验', profile.get('experience', '待补充')),
        ('收入稳定性', profile.get('income_stability', '待补充')),
    ]
    for i, (k, v) in enumerate(simple_rows):
        yy = s1 + 78 + i * 32
        r.txt(left, yy, k + '：', 22, True)
        r.txt(valx, yy, str(v), 22, False, TEXT)
    sum_y = s1 + 210
    r.txt(left, sum_y, '一句话定位：', 22, True)
    r.draw_para(valx, sum_y, one_liner, 520, 22, MUTED, False, 4, 3)
    chip_y = sum_y + len(one_liner_lines) * 26 + 18
    chip_x = left
    for tag in profile.get('tags', [])[:4]:
        label = tag.get('text') if isinstance(tag, dict) else str(tag)
        color_key = tag.get('color') if isinstance(tag, dict) else 'blue'
        color = {'blue': BLUE, 'green': GREEN, 'orange': ORANGE, 'red': RED}.get(color_key, BLUE)
        w, _ = r.chip(chip_x, chip_y, label, color, size=20)
        chip_x += w + 10

    # 02
    preferences = payload.get('preferences', [])
    s2 = section(2, '偏好画像', s2_h)
    for i, item in enumerate(preferences):
        yy = s2 + 78 + i * 26
        r.txt(left, yy, str(item.get('label', '')) + '：', 22, True)
        r.txt(valx, yy, str(item.get('value', '')), 22, False, MUTED)

    # 03
    s3 = section(3, '当前配置 vs 推荐均衡配置', 610)
    r.txt(left, s3 + 66, '统一按大类资产对比，客户才看得出具体在哪些大类过配 / 欠配。', 21, False, MUTED)
    r.chip(left, s3 + 102, '当前配置', BLUE, size=18)
    r.chip(left + 126, s3 + 102, '推荐均衡配置', BLUE_LIGHT, fg=NAVY, size=18)

    cats = [(k, payload['allocation']['bucket_labels'][k], payload['allocation']['current'][k], payload['allocation']['recommended'][k]) for k in BUCKET_LABELS]
    plot_x1 = x + 44
    plot_x2 = x + cw - 34
    plot_y1 = s3 + 166
    plot_y2 = s3 + 434
    for val in [0, 20, 40, 60]:
        yy = plot_y2 - (plot_y2 - plot_y1) * val / 60
        d.line((plot_x1, yy, plot_x2, yy), fill='#E5E7EB', width=2)
        r.txt(plot_x1 - 22, yy - 10, str(val), 18, False, MUTED, anchor='ra')
    group_w = (plot_x2 - plot_x1) / len(cats)
    bar_w = 34
    for i, (code, name, cur, rec) in enumerate(cats):
        gx = plot_x1 + group_w * (i + 0.5)
        x_cur = gx - 40
        x_rec = gx + 8
        h_cur = (plot_y2 - plot_y1) * cur / 60
        h_rec = (plot_y2 - plot_y1) * rec / 60
        d.rounded_rectangle((x_cur, plot_y2 - h_cur, x_cur + bar_w, plot_y2), radius=8, fill=BLUE)
        d.rounded_rectangle((x_rec, plot_y2 - h_rec, x_rec + bar_w, plot_y2), radius=8, fill=BLUE_LIGHT)
        r.txt(x_cur + bar_w / 2, plot_y2 - h_cur - 24, f'{int(cur) if float(cur).is_integer() else cur}', 17, True, BLUE, anchor='ma')
        r.txt(x_rec + bar_w / 2, plot_y2 - h_rec - 24, f'{int(rec) if float(rec).is_integer() else rec}', 17, True, NAVY, anchor='ma')
        r.txt(gx, plot_y2 + 16, code, 18, True, TEXT, anchor='ma')
        r.txt(gx, plot_y2 + 40, name, 18, False, MUTED, anchor='ma')

    r.rounded(x + 22, s3 + 500, x + cw - 22, s3 + 576, fill='#EFF6FF', outline='#BFDBFE')
    r.draw_para(x + 42, s3 + 522, payload['allocation']['structure_conclusion'], cw - 84, 24, NAVY, True, 6, 2)

    # 04
    core = payload['core_conclusion']
    s4 = section(4, '核心结论', 250)
    for i, line_s in enumerate(core.get('lines', [])[:2]):
        r.txt(left, s4 + 82 + i * 40, str(line_s), 28, i == 1, RED if i == 1 else TEXT)
    chip_x = left
    for item in core.get('chips', [])[:3]:
        label = item.get('text', '')
        color = {'green': GREEN, 'red': RED, 'orange': ORANGE, 'blue': BLUE}.get(item.get('color', 'blue'), BLUE)
        w, _ = r.chip(chip_x, s4 + 176, label, color, size=21)
        chip_x += w + 12

    # 05
    diagnostics = payload.get('diagnostics', [])
    s5 = section(5, '偏差诊断', s5_h)
    r.txt(left, s5 + 66, '配置偏差主要靠图表达；这里仅保留真正关键的几类偏差。', 21, False, MUTED)

    def metric_row(y0, title, current, pref, diag, sev, color):
        row_h = 92
        r.d.rounded_rectangle((x + 24, y0, x + cw - 24, y0 + row_h), radius=18, fill=SOFT, outline=LINE, width=2)
        r.txt(x + 42, y0 + 14, title, 24, True)
        r.chip(x + cw - 110, y0 + 12, sev, color, size=16)
        colx = [x + 250, x + 650, x + 1030]
        headers = [('当前值', current), ('偏好值', pref), ('结论', diag)]
        for (lab, val), xx in zip(headers, colx):
            r.txt(xx, y0 + 14, lab, 17, True, MUTED)
            r.draw_para(xx, y0 + 42, val, 300, 20, TEXT, False, 4, 2)

    start = s5 + 106
    for i, row in enumerate(diagnostics):
        color = SEVERITY_COLOR.get(row.get('severity', '中'), ORANGE)
        metric_row(start + i * 102, row.get('title', ''), row.get('current', ''), row.get('preference', ''), row.get('conclusion', ''), row.get('severity', '中'), color)

    # 06
    behavior_lines = payload.get('behavior_lines', [])
    s6 = section(6, '行为画像', s6_h)
    for i, line_s in enumerate(behavior_lines):
        is_key = i == len(behavior_lines) - 1
        r.txt(left, s6 + 74 + i * 34, str(line_s), 24, is_key, RED if is_key else TEXT)

    # 07
    actions = payload.get('actions', [])
    s7 = section(7, '优先动作', s7_h)
    for i, a in enumerate(actions):
        yy = s7 + 72 + i * 50
        r.d.rounded_rectangle((left, yy + 4, left + 30, yy + 34), radius=8, fill='#DBEAFE')
        r.txt(left + 10, yy + 2, str(i + 1), 16, True, BLUE)
        r.draw_para(left + 48, yy, str(a), cw - 100, 22, TEXT, False, 4, 2)

    footer_y = max(render_h - 28, y + 30)
    if footer_y > render_h - 28:
        footer_y = render_h - 28
    r.txt(W // 2, footer_y, payload['footer'], 20, False, MUTED, anchor='mm')
    return r.img


def main():
    parser = argparse.ArgumentParser(description='Render private-banking customer profile card from structured JSON.')
    parser.add_argument('--input', required=True, help='Path to input JSON file')
    parser.add_argument('--output', required=True, help='Path to output PNG file')
    parser.add_argument('--pdf', help='Optional PDF output path')
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
