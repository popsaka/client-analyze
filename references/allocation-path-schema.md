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
  "title": "示例客户A配置建议路径（演示版）",
  "subtitle": "虚拟示例｜先满足明确约束，再重评估，再补完整配置",
  "current_overview": {
    "bullets": [
      "现金管理类占比偏高，长期闲置明显",
      "高波增长仓位占比偏高，收益来源集中"
    ],
    "chips": [
      {"text": "明确约束1：保留流动性备付", "color": "blue"},
      {"text": "明确约束2：保留核心增长仓", "color": "red"}
    ]
  },
  "step1": {
    "title": "先满足客户明确点名的需求",
    "items": [
      {
        "label": "Step 1A",
        "title": "先单列流动性备付仓",
        "body": "把阶段性必需现金从长期配置里剥离出来。",
        "color": "blue"
      },
      {
        "label": "Step 1B",
        "title": "保留核心增长仓，但控制高波集中度",
        "body": "先确认核心增长仓底线，再决定后续补低波层和对冲层的节奏。",
        "color": "red"
      }
    ]
  },
  "step2": {
    "title": "完成以上两步后，先重新评估客户配置",
    "subtitle": "重新评估后的组合（演示版）",
    "chips": [
      {"text": "流动性备付", "color": "blue"},
      {"text": "核心增长仓", "color": "orange"},
      {"text": "中波增长层", "color": "gray"},
      {"text": "待继续优化", "color": "green"}
    ],
    "segments": [
      {"title": "流动性备付", "amount": "15%", "percent": 15, "color": "#5B95E5"},
      {"title": "核心增长仓", "amount": "30%", "percent": 30, "color": "#FF7A16"},
      {"title": "中波增长层", "amount": "20%", "percent": 20, "color": "#334155"},
      {"title": "待继续优化", "amount": "35%", "percent": 35, "color": "#22C55E"}
    ],
    "conclusion": "重评估结论：先满足流动性与核心增长仓约束后，组合已经不再极端，但仍需继续补低波收益层与对冲层。"
  },
  "step3": {
    "title": "继续做配置完善（针对剩余待优化部分）",
    "cards": [
      {"title": "低波收益层", "amount": "10%-15%", "body": "补稳定收益底仓。", "tone": "blue"},
      {"title": "中波增长层", "amount": "10%-15%", "body": "提升长期增长质量。", "tone": "green"},
      {"title": "黄金 / 对冲层", "amount": "5%-10%", "body": "增强组合韧性。", "tone": "orange"},
      {"title": "战备现金", "amount": "5%-10%", "body": "保留后续再平衡空间。", "tone": "purple"}
    ],
    "final_recommendation": "一句话建议：先切流动性备付，再保留核心增长仓，之后把剩余仓位逐步补成更完整的多层结构。"
  },
  "footer": "注：本文件为虚拟示例，仅演示输入结构，不对应任何真实客户。"
}
```

## House Rules
- 顺序必须是：**当前资产 → 明确需求 → 重评估 → 剩余资金补齐**。
- 先满足客户点名需求，不要一上来就把全部闲置资金打散。
- Step 2 必须展示“执行前两步后的工作版组合”，避免客户误解成一次性终局配置。
- Step 3 必须只针对“剩余待配置资金”给出分层建议。
- 文案重点是**执行路径**，不是大而全的资产课堂。
- 如给出分配金额，优先同时给用途解释；不要只有数字没有逻辑。
- Public references must remain fictional / synthetic; real client examples should stay outside the repo.
