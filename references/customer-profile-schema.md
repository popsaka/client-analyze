# Customer Profile Card Schema

This skill reuses the locked 7-section house style from the approved private-banking card template.

## Fixed Section Order
1. 客户定位
2. 偏好画像
3. 当前配置 vs 推荐均衡配置
4. 核心结论
5. 偏差诊断
6. 行为画像
7. 优先动作

## Non-Negotiable Rules
- Section 03 must use unified `B0-B5` buckets.
- Section 03 must show **当前配置 vs 推荐均衡配置** side by side.
- Section 03 must include a visible **结构结论**.
- Section 05 stays concise; let the chart carry most of the comparison burden.
- **纪律性退出 ≠ 高行为偏差**.
- Keep section 07 `优先动作`.

## Bucket Standard
- `B0` 现金管理：现金 / 稳定币 / 货基
- `B1` 低波收益：存款 / 债 / 固收 / 票息类
- `B2` 中波增长：核心股票 / 宽基 ETF / 核心权益
- `B3` 高波增长：BTC / ETH / 高 beta 增长资产
- `B4` 超高波机会：小币 / 主题机会 / 杠杆 / 期权
- `B5` 抗通胀对冲：黄金 / 商品 / CTA / 对冲仓

## Supported Recommendation Presets
- `保守保值`
- `稳健增值`
- `平衡增长`
- `进取增长`

## Practical Guidance
- If the user already has a house recommendation, pass explicit `allocation.recommended`.
- If not, use `allocation.recommended_preset` or `profile.style`.
- If only raw holdings are known, either normalize to `allocation.current` or pass `allocation.raw_assets`.
- Fix layout issues in the script, not by one-off manual image edits.

## Minimal Payload
Read `example-pack.json` and reuse `profile_card` as the fastest starting point.
