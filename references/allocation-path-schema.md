# Allocation Path Schema

Use this when the user asks for a **配置优化建议 / 配置建议路径图 / allocation path**.

## Output Goal
Render a deterministic path chart that answers three questions in order:
1. 当前资产长什么样
2. 先满足哪些明确需求
3. 完成点名需求后，剩余资金怎么继续补齐配置

## Minimal JSON Shape

```json
{
  "title": "叶哥配置建议路径（按需求顺序）",
  "subtitle": "基于：320 BTC + 2800万 USDT｜先满足明确需求，再重评估，再补完整配置",
  "current_overview": {
    "bullets": [
      "320 BTC ≈ 2269万 USD（约 44.8%）",
      "2800万 USDT（约 55.2%）"
    ],
    "chips": [
      {"text": "客户明确需求1：300万 USDT 配 BTDR", "color": "blue"},
      {"text": "客户明确需求2：BTC本位增强 3%左右", "color": "red"}
    ]
  },
  "step1": {
    "title": "先满足客户明确点名的需求",
    "items": [
      {
        "label": "Step 1A",
        "title": "买入 BTDR 300万 USDT 等值",
        "body": "定位：战术仓 / 客户指定仓，不视为分散配置。",
        "color": "blue"
      },
      {
        "label": "Step 1B",
        "title": "配置 BTC 本位增强（建议先上 200 BTC）",
        "body": "先上 100 BTC，观察 2-4 周后再补 100 BTC。",
        "color": "red"
      }
    ]
  },
  "step2": {
    "title": "完成以上两步后，先重新评估客户配置",
    "subtitle": "重新评估后的组合（工作版）",
    "chips": [
      {"text": "BTC现货 120个", "color": "blue"},
      {"text": "BTC增强 200个", "color": "red"},
      {"text": "BTDR 300万", "color": "gray"},
      {"text": "待配置 USDT 2500万", "color": "teal"}
    ],
    "segments": [
      {"title": "BTC现货", "amount": "120个", "percent": 16.8, "color": "#5B95E5"},
      {"title": "BTC增强", "amount": "200个", "percent": 28.0, "color": "#FF7A16"},
      {"title": "BTDR", "amount": "300万", "percent": 5.9, "color": "#334155"},
      {"title": "USDT待配置", "amount": "2500万", "percent": 49.3, "color": "#22C55E"}
    ],
    "conclusion": "重评估结论：执行完客户指定需求后，组合不再只是 BTC + USDT 两极结构，但仍有近一半 USDT 待配置。"
  },
  "step3": {
    "title": "继续做配置完善（针对剩余 2500万 USDT）",
    "cards": [
      {"title": "低波收益 / FI", "amount": "800万 USDT", "body": "先补稳定收益底仓。", "tone": "blue"},
      {"title": "套利 / 市场中性", "amount": "700万 USDT", "body": "增加非方向性收益来源。", "tone": "green"},
      {"title": "黄金 / 对冲层", "amount": "500万 USDT", "body": "补抗通胀与风险对冲层。", "tone": "orange"},
      {"title": "Balance+ / 战备现金", "amount": "500万 USDT", "body": "保留再平衡和后续战术空间。", "tone": "purple"}
    ],
    "final_recommendation": "一句话建议：先满足客户明确点名的 BTDR 和 BTC 增强需求；完成后立刻重评估，再把剩余 USDT 从闲置现金升级成多层结构。"
  },
  "footer": "注：以上为工作版配置建议路径，正式执行前需结合产品可得性、合规与执行 SLA 校正。"
}
```

## House Rules
- 顺序必须是：**当前资产 → 明确需求 → 重评估 → 剩余资金补齐**。
- 先满足客户点名需求，不要一上来就把全部闲置资金打散。
- Step 2 必须展示“执行前两步后的工作版组合”，避免客户误解成一次性终局配置。
- Step 3 必须只针对“剩余待配置资金”给出分层建议。
- 文案重点是**执行路径**，不是大而全的资产课堂。
- 如给出分配金额，优先同时给用途解释；不要只有数字没有逻辑。
