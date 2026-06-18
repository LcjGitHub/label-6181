# 老式自动售货机机型图鉴

收录经典自动售货机机型信息：机型、地点、售卖品类、运作状态与照片描述。前后端分离 MVP，支持列表筛选与基础 CRUD。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Naive UI + VueUse + axios（端口 **3101**） |
| 后端 | FastAPI + SQLite `./backend/data/vending.db`（端口 **3000**） |

## 目录结构

```
├── backend/          # FastAPI 后端
├── frontend/         # Vue 3 前端
└── README.md
```

## 启动方式

### 1. 后端（一条命令）

在项目根目录执行：

```bash
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && python -m uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

> **macOS / Linux** 将 `.venv\Scripts\activate` 换为 `source .venv/bin/activate`。

首次启动会自动创建数据库并写入 **5 条** seed 数据。API 文档：http://localhost:3000/docs

### 2. 前端

另开终端，在项目根目录执行：

```bash
cd frontend && npm install && npm run dev
```

浏览器访问：http://localhost:3101

## 功能范围（MVP）

- 机器列表，支持按「全部 / 运作中 / 已停运」筛选
- 新增、编辑、删除售货机记录
- 字段：机型、地点、售卖品类、是否运作、照片描述

## 未包含

登录、JWT、Redis、Docker、MySQL/PostgreSQL 等均未实现。

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/machines?operational=all\|true\|false` | 列表（运作状态筛选） |
| GET | `/api/machines/{id}` | 详情 |
| POST | `/api/machines` | 新增 |
| PUT | `/api/machines/{id}` | 更新 |
| DELETE | `/api/machines/{id}` | 删除 |
