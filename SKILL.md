---
name: client-analyze
description: Build deterministic private-banking client materials from structured inputs, including a fixed-style 客户画像卡 and 配置优化建议 / 配置建议路径图. Use when the user asks to 做客户画像卡、生成一页式客户分析、出配置建议路径、把问卷答案转成客户卡+配置图、or package repeatable private-banking visual workflows into a reusable skill.
---

# Build Private Banking Client Pack

Use this skill when the deliverable is a **private-banking client pack**, not just freeform analysis text.

Current supported outputs:
1. **客户画像卡** — locked 7-section house style
2. **配置建议路径图** — deterministic step-by-step recommendation path

## Workflow

1. Normalize the source information into structured JSON.
2. If needed, read:
   - `references/input-templates.md`
   - `references/customer-profile-schema.md`
   - `references/allocation-path-schema.md`
3. Start from one of the template JSON files instead of writing the payload from scratch.
4. Build one combined input JSON containing one or both sections:
   - `profile_card`
   - `allocation_path`
4. Run the bundled renderer:

```bash
python3 scripts/render_client_pack.py \
  --input /tmp/client_pack.json \
  --output-dir /tmp/client_pack_out \
  --prefix yeg
```

5. Review the generated image(s) once before sending or publishing.
6. If layout bugs appear, patch the renderer script; do not hand-draw one-off replacements.

## Output Rules

### A. 客户画像卡
- Keep the fixed 7-section order.
- Use unified `B0-B5` buckets.
- Show **当前配置 vs 推荐均衡配置** in section 03.
- Keep diagnostics concise and chart-led.
- **纪律性退出 ≠ 高行为偏差**.
- Keep section 07 `优先动作`.

### B. 配置建议路径图
- Organize in business order, not asset-theory order.
- Preferred spine:
  1. 当前资产概况
  2. 先满足客户明确点名需求
  3. 重评估执行前两步后的工作版组合
  4. 再对剩余待配置资金做分层补齐
- The path chart should answer **what to do first / next / later**, not become a generic asset-allocation lecture.

## Practical Guidance

- If only the profile card is needed, provide `profile_card` only.
- If only the recommendation path is needed, provide `allocation_path` only.
- If both are needed, render both in one run.
- Use explicit numbers when known; otherwise keep labels qualitative but still ordered.
- For repeatability, keep sample inputs in JSON and re-render from scripts.

## References
- `references/input-templates.md`
- `references/template-profile-card.json`
- `references/template-allocation-path.json`
- `references/template-client-pack.json`
- `references/customer-profile-schema.md`
- `references/allocation-path-schema.md`
- `references/example-pack.json`

## Scripts
- `scripts/render_customer_profile_card.py`
- `scripts/render_allocation_path.py`
- `scripts/render_client_pack.py`
