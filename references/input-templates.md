# Input Templates

Use these files in two layers:

## 1) Blank-ish templates (start here)
- `template-profile-card.json` — only render 客户画像卡
- `template-allocation-path.json` — only render 配置建议路径图
- `template-client-pack.json` — render both together

## 2) Filled example
- `example-pack.json` — a real worked example based on the previously built 叶哥 materials

---

## Which template to choose

### A. 只做客户画像卡
Use `template-profile-card.json`

Render command:
```bash
python3 scripts/render_customer_profile_card.py \
  --input references/template-profile-card.json \
  --output /tmp/profile_card.png \
  --pdf /tmp/profile_card.pdf
```

### B. 只做配置建议路径图
Use `template-allocation-path.json`

Render command:
```bash
python3 scripts/render_allocation_path.py \
  --input references/template-allocation-path.json \
  --output /tmp/allocation_path.png \
  --pdf /tmp/allocation_path.pdf
```

### C. 两张一起出
Use `template-client-pack.json`

Render command:
```bash
python3 scripts/render_client_pack.py \
  --input references/template-client-pack.json \
  --output-dir /tmp/client_pack_out \
  --prefix client_name
```

---

## Field rules you should not guess

### 客户画像卡（profile_card）

#### Required enough to render cleanly
- `title`
- `profile`
- `preferences`
- `allocation.current`
- one of:
  - `allocation.recommended`, or
  - `allocation.recommended_preset`, or
  - `profile.style`
- `diagnostics`
- `behavior_lines`
- `actions`

#### Numeric rule
- `allocation.current` and `allocation.recommended` must use numeric values for `B0-B5`
- Use percentage points, not decimals
  - correct: `45`
  - wrong: `0.45`

#### Recommendation rule
If you do not want to hand-fill `allocation.recommended`, use one of these presets:
- `保守保值`
- `稳健增值`
- `平衡增长`
- `进取增长`

#### Holdings rule
If raw holdings are easier than bucket math, use:
- `allocation.raw_assets`

Example:
```json
"allocation": {
  "raw_assets": [
    {"name": "BTC", "percent": 60},
    {"name": "稳定币", "percent": 40}
  ],
  "recommended_preset": "进取增长"
}
```

---

### 配置建议路径图（allocation_path）

#### Required enough to render cleanly
- `title`
- `current_overview.bullets`
- `step1.items`
- `step2.segments`
- `step2.conclusion`
- `step3.cards`
- `step3.final_recommendation`

#### Step order is locked
Keep this business order:
1. 当前资产概况
2. 先满足客户明确点名需求
3. 重评估执行前两步后的工作版组合
4. 再对剩余待配置资金做分层补齐

#### Segment rule
In `step2.segments`, each segment should ideally contain:
- `title`
- `amount`
- `percent`
- `color`

`percent` should be numeric.

---

## Minimal workflow recommendation

### Fastest safe path
1. Copy `template-client-pack.json`
2. Replace customer-specific wording and numbers
3. Render both outputs
4. If only one chart is needed, delete the other section or use the single-purpose template

---

## File intent summary
- `template-*.json` = structure-first starting points
- `example-pack.json` = filled reference answer
- `customer-profile-schema.md` = house rules for the card
- `allocation-path-schema.md` = house rules for the path chart
