# 程序员职场养成系统 MVP（Vue3 + Flask）

这是一个可快速落地的公司内部养成系统 MVP，包含：

- 前端（Vue3 + Vite）：个人养成主页、任务完成、团队协作、奖励兑换。
- 后端（Flask）：用户/任务/团队/奖励 RESTful API，含积分结算、升级与兑换逻辑。

## 目录结构

```bash
backend/
  app.py
  requirements.txt
frontend/
  index.html
  package.json
  vite.config.js
  src/
```

## 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

后端默认启动在 `http://127.0.0.1:5000`。

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认启动在 `http://127.0.0.1:5173`，已通过 Vite 代理到 Flask 的 `/api`。

## MVP 覆盖点

- 任务完成自动发积分：`POST /api/tasks/<task_id>/complete`
- 积分触发等级变化：后端自动计算等级和伙伴状态
- 奖励兑换：`POST /api/rewards/redeem`
- 团队视图：`GET /api/teams/<team_id>`
- 运营可扩展：内存数据模型可替换成 MySQL/PostgreSQL + Redis

## 建议下一步

1. 接入公司统一认证（SSO）与项目管理系统 webhook。
2. 增加数据库与审计日志表，支持防刷分和追溯。
3. 前端增加 ECharts 看板、技术树节点动画、企业微信免登录。
