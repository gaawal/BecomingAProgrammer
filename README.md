# 程序员职场养成系统 MVP（Vue3 + Flask）

你说的“运行起来”，这里给到 **开箱即跑版本**：

- **方式 A（推荐）**：只启动 Flask，直接访问内置前端页面（无需 npm install）
- **方式 B**：使用独立 Vue3 + Vite 前端开发模式（需要 npm）

---

## 1) 一键跑通（无需 Node）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

启动后访问：

- 页面：`http://127.0.0.1:5000/`
- 健康检查：`http://127.0.0.1:5000/api/health`

> 这个页面是 `backend/static/index.html`，用 Vue3 CDN 渲染，保证在没法 `npm install` 的环境也能演示完整闭环。

---

## 2) 前后端分离开发（可选）

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

前端：

```bash
cd frontend
npm install
npm run dev
```

前端默认地址 `http://127.0.0.1:5173`，通过 Vite 代理访问 Flask `/api`。

---

## 3) MVP 功能覆盖

- 任务完成自动发积分：`POST /api/tasks/<task_id>/complete`
- 积分触发等级变化（伙伴状态联动）
- 奖励兑换：`POST /api/rewards/redeem`
- 团队协作数据：`GET /api/teams/<team_id>`
- 积分日志追踪：`GET /api/points/logs`

---

## 4) 下一步建议

1. 将内存数据替换为 MySQL/PostgreSQL + Redis。
2. 接入 SSO 与项目管理系统（Jira/禅道/企业内部系统）。
3. 增加防刷分策略：风控规则、审计日志、异常告警。
4. 企业微信内嵌登录与消息推送（任务完成、升级、兑换通知）。
