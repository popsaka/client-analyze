# client-analyze

Deterministic private-banking client analysis skill.

This repo packages a reusable OpenClaw skill that can render:

1. **客户画像卡** — fixed 7-section house style
2. **配置建议路径图** — step-by-step allocation / adjustment path
3. **两张一起出** — one combined client pack flow

---

## What this is for

Use this repo when you want to turn structured client information into repeatable visual outputs instead of redrawing slides by hand every time.

Typical use cases:
- 根据问卷/访谈信息生成客户画像卡
- 根据当前持仓 + 目标约束生成配置建议路径图
- 内部版先出逻辑，再逐步细化到 MP 具体产品
- 避免风格漂移，统一输出格式

---

## Repo structure

```text
client-analyze/
├── SKILL.md
├── scripts/
│   ├── render_customer_profile_card.py
│   ├── render_allocation_path.py
│   └── render_client_pack.py
└── references/
    ├── input-templates.md
    ├── template-profile-card.json
    ├── template-allocation-path.json
    ├── template-client-pack.json
    ├── example-pack.json
    ├── customer-profile-schema.md
    ├── allocation-path-schema.md
    ├── mp-product-registry-v1.md
    └── mp-product-registry-v1.json
```

---

## Quick start

### 1) Pick an input template

Start here:
- `references/template-profile-card.json` → only render 客户画像卡
- `references/template-allocation-path.json` → only render 配置建议路径图
- `references/template-client-pack.json` → render both together

If you want a fictional worked example, read:
- `references/example-pack.json`

Field-by-field notes live in:
- `references/input-templates.md`

---

### 2) Fill the template

You do **not** need to convert everything into B0-B5 by hand unless you want precise control.

For profile cards, at minimum fill:
- title / subtitle
- profile
- preferences
- allocation.current
- either:
  - allocation.recommended, or
  - allocation.recommended_preset, or
  - profile.style
- diagnostics
- behavior_lines
- actions

For allocation paths, at minimum fill:
- title / subtitle
- current_overview.bullets
- step1.items
- step2.segments
- step2.conclusion
- step3.cards
- step3.final_recommendation

---

### 3) Render

#### A. 客户画像卡
```bash
python3 scripts/render_customer_profile_card.py \
  --input references/template-profile-card.json \
  --output /tmp/profile_card.png \
  --pdf /tmp/profile_card.pdf
```

#### B. 配置建议路径图
```bash
python3 scripts/render_allocation_path.py \
  --input references/template-allocation-path.json \
  --output /tmp/allocation_path.png \
  --pdf /tmp/allocation_path.pdf
```

#### C. 两张一起出
```bash
python3 scripts/render_client_pack.py \
  --input references/template-client-pack.json \
  --output-dir /tmp/client_pack_out \
  --prefix client_name
```

Outputs will be:
- `client_name_profile_card.png`
- `client_name_profile_card.pdf`
- `client_name_allocation_path.png`
- `client_name_allocation_path.pdf`

---

## Input modes

### Mode 1 — Generic asset-bucket recommendation
Use the normal templates only.

### Mode 2 — Product-level MP mapping
If you want the path chart to name actual MP products, use:
- `references/mp-product-registry-v1.md`
- `references/mp-product-registry-v1.json`

Then add product hints like this:

```json
{
  "title": "低波收益层",
  "amount": "150万 U",
  "body": "先修结构，不先追求高复杂增强。",
  "tone": "blue",
  "mp_products": ["Balance+", "Fixed Income"]
}
```

Supported locations:
- `step1.items[].mp_products`
- `step3.cards[].mp_products`

---

## Important house rules

### 客户画像卡
- fixed 7-section order
- section 03 must show `当前配置 vs 推荐均衡配置`
- use unified `B0-B5` buckets
- keep diagnostics concise
- **纪律性退出 ≠ 高行为偏差**

### 配置建议路径图
- keep the path in business order:
  1. 当前资产概况
  2. 先满足明确需求
  3. 重评估前两步后的工作版组合
  4. 再补齐剩余待配置部分
- do not turn it into a generic asset-allocation lecture
- if mapping to MP products, do **not** claim a product exists unless it is in the confirmed registry or separately confirmed

---

## Privacy rule

Public examples in this repo are **fictional / synthetic**.

Do not put the following into public examples:
- real client names
- exact real holdings
- sensitive client constraints
- real internal-only notes

If you need a real case, create a private JSON outside this repo.

---

## Packaging as a `.skill`

If you want to package this repo as a distributable skill:

```bash
python3 /path/to/package_skill.py /path/to/client-analyze /tmp/output
```

The resulting file will be:
- `/tmp/output/client-analyze.skill`

---

## Current scope limits

This repo currently supports:
- deterministic rendering
- asset-bucket logic
- optional MP product mapping via the confirmed `v1` registry

It does **not** yet contain:
- full MP product operating manual
- exact sales/eligibility rules
- redemption / lock-up legal terms
- live pricing or suitability engine

Treat it as a **presentation + structuring tool**, not a full execution engine.

---

## Suggested workflow in practice

1. Use `template-client-pack.json`
2. Fill the customer facts
3. Render the first internal draft
4. Adjust wording / recommendation logic
5. If needed, map step3 into concrete MP products
6. Regenerate instead of editing slides manually
