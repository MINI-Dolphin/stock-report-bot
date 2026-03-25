# 云端股票报告推送方案

## 方案1：GitHub Actions（免费，推荐）

**原理**：GitHub 免费提供定时任务服务，每天自动运行脚本推送报告。

### 步骤

**1. 创建 GitHub 仓库**
- 访问 https://github.com/new
- 创建新仓库，如 `stock-report-bot`

**2. 上传以下文件到仓库**：
- `stock_report.py` - 股票数据获取脚本
- `.github/workflows/daily.yml` - 定时任务配置

**3. 配置企业微信 webhook**
- 在企业微信群 → 设置 → 添加群机器人
- 创建机器人后获取 Webhook 地址
- 在 GitHub 仓库 Settings → Secrets 添加：
  - `WECOM_WEBHOOK`: 你的Webhook地址

**4. 启用 Actions**
- 仓库创建后，Actions 会自动按定时运行

---

## 方案2：Railway + Python（免费）

**原理**：在 Railway 部署一个 Python 应用，定时运行推送。

### 步骤

1. 注册 https://railway.app
2. 连接 GitHub 仓库
3. 部署 Python 应用
4. 设置定时任务

---

## 方案3：最简单的替代方案

**电脑不开机时**：手动触发推送

我可以给您一个链接或命令，您点击后立即生成并推送报告。

---

## 需要您选择

1. **方案1（GitHub Actions）**：我帮您创建完整的仓库和代码，您上传到 GitHub
2. **方案3（手动触发）**：我给您一个备用方案，电脑不开机时手动发消息给我，我生成报告推送

您选哪个？