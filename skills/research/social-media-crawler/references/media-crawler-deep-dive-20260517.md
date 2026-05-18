# MediaCrawler 技术调研笔记 (2026-05-17)

## 项目概览
- **作者**: 程序员阿江 (NanmiCoder / Relakkes)
- **GitHub**: https://github.com/NanmiCoder/MediaCrawler
- **Stars**: 7.6K+
- **License**: 开源
- **核心原理**: Playwright浏览器自动化 + CDP连接已有Chrome
- **技术门槛**: 无需JS逆向，用JS表达式获取签名参数

## 支持平台
小红书、抖音、快手、B站、微博、百度贴吧、知乎

## 技术架构

### 登录方式
- QR扫码登录（APP扫码）
- CDP模式连接用户已有Chrome（复用Cookie/登录态）
- 登录态长期缓存

### 下载模式
- 关键词搜索爬取
- 指定帖子ID爬取
- 指定创作者主页爬取

### 数据存储
CSV / JSON / JSONL / Excel / SQLite / MySQL

## 代理方案
- 内置IP代理池支持
- 推荐：LegionProxy住宅代理（$0.60/GB起）
- 推荐：TikHub.io API接口（900+稳定接口）

## 对我们的借鉴

1. **CDP模式** — 服务器通过 ws:// 连接Keke本地Chrome的远程调试端口(9222)
2. **请求头模拟** — 完整浏览器指纹(User-Agent/Referer/等)
3. **随机延迟** — 模拟人类操作不规律性
4. **代理轮换** — 避免单IP被封

## 知乎40362反爬应对（来自项目博客）

原因：短时间内大量相同模式请求 + 缺少必要请求头 + 固定时间间隔 + 缺少签名参数
方案：
1. 添加完整浏览器标准请求头
2. 引入随机延迟
3. 使用代理池轮换IP
4. 分析前端JavaScript获取签名算法
5. 调整关键参数

## 部署方式

```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler
uv sync
# 或原生venv:
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
playwright install chromium
```

## 后续讨论要点
1. 是否直接安装MediaCrawler在服务器？
2. 是否需要购买住宅代理IP？
3. CDP模式（Keke的Chrome远程调试）是否可行？
4. 优先攻克哪个平台？
