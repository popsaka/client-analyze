# MP Product Registry v1

This registry is transcribed from the confirmed image:
- `MP资产在12格中的定位（风险 × 流动性） | v4（仅资产，含区间估算）`

## Scope
- This map only includes **investment products / assets**.
- It explicitly excludes: transaction, execution, lending and other service lines.
- Return / volatility / MDD are **experience-based ranges**, not sales promises.

## Current Coverage (11 items)
- C-L1: `Balance+`
- C-L2: `Fixed Income`
- B-L1: `套利策略（Arbitrage）`
- B-L2: `Dual Currency`, `Daily Dual Currency`
- A-L1: `多空策略（Long-Short）`
- A-L2: `Snowball`, `Seagull`, `Sharkfin`
- A-L3: `Structured OTC（定制）`
- A+-L1: `趋势策略（Trend/CTA）`

## Important limitation
This registry is **not** the full MP asset universe. It is only the subset shown in the confirmed v4 asset map.

That means some things discussed elsewhere (for example equities, bonds via broker, spot gold custody, etc.) are **not present in this v4 chart**, so do not pretend they came from this source.

## How to use it in `client-analyze`
When refining an allocation path into concrete MP products:
1. Start with the client constraint set
   - risk budget
   - liquidity / lock-up tolerance
   - whether path-dependent structures are allowed
2. Prefer products whose risk/liquidity cell matches the target bucket
3. If a generic recommendation cannot be mapped cleanly to this chart, say so explicitly
   - e.g. “current confirmed MP v4 map does not show a pure gold/hedge layer product”
4. Use `mp_products` on step items / step3 cards to show suggested MP products

## Optional mapping heuristic
- `低波收益层` -> `Balance+`, `Fixed Income`
- `非方向性收益层` -> `套利策略（Arbitrage）`, `多空策略（Long-Short）`
- `期权增强层` -> `Dual Currency`, `Daily Dual Currency`, `Sharkfin`, `Seagull`, `Snowball`
- `高波进攻层` -> `趋势策略（Trend/CTA）`
- `低流动定制层` -> `Structured OTC（定制）`

Use the JSON registry for machine-readable fields:
- `mp-product-registry-v1.json`
