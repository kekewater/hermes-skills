# 投资日报富文本Prompt模板

使用时将 {{DATE}}、{{DATA}} 等替换为实际数据，作为 gpt-image-2 的 prompt。

```
你是一个专业的投资日报信息图设计生成器。生成一张专业、精美、深色科技风格的投资日报图片。

标题：{{DATE}} | 投资日报
副标题：数据截止：{{DATE}}
风格：深蓝色科技K线底纹，淡蓝渐变蒙版，金色标题，白灰文字

===== 数据内容 =====

一、全球主要资产

美股（全线收跌，科技分化）：
道指 {{DJIA}} {{DJIA_CHANGE}}
标普500 {{SPX}} {{SPX_CHANGE}}
纳指 {{IXIC}} {{IXIC_CHANGE}}
{{US_HIGHLIGHTS}}

港股：
恒生指数 {{HSI_CHANGE}}
南下资金 {{SOUTHBOUND_FLOW}}

商品：
WTI原油 {{OIL_CHANGE}}
白银 {{SILVER_CHANGE}}

二、A股市场

上证指数 {{SH_COMP}} {{SH_CHANGE}}（全周{{SH_WEEK}}）
深证成指 {{SZ_COMP}} {{SZ_CHANGE}}
创业板指 {{CYB}} {{CYB_CHANGE}}（全周{{CYB_WEEK}}）
科创50 {{KC50_WEEK}}
成交：{{VOLUME_INFO}}

领涨行业：{{LEADING_SECTORS}}
领跌行业：{{LAGGING_SECTORS}}

三、重点事件
{{EVENTS}}

四、市场研判
{{INSTITUTIONAL_VIEWS}}

主线：{{MAIN_THEME}}
策略：{{STRATEGY}}

五、风险提示
{{RISKS}}

底部：仅供参考不构成投资建议 | 市场有风险投资需谨慎

风格：Bloomberg/Penny terminal风格，简洁大气，信息图，深色背景，金色点缀，专业金融数据可视化
```

## 使用示例

```bash
# 将填好的prompt用脚本生图
PY=~/.hermes/skills/financial/china-stock-data/.venv/bin/python3
echo "$(cat /tmp/filled_prompt.txt)" | $PY ~/.hermes/scripts/gpt_image_gen.py - /tmp/gpt_daily_report.png

# 或直接scp到VPS
scp -i ~/.ssh/id_vultr /tmp/filled_prompt.txt root@45.76.185.1:/tmp/prompt.txt
# 然后在VPS上跑curl
```
