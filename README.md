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

### 售货机机型图鉴

- 机器列表，支持按「全部 / 运作中 / 已停运」筛选
- 新增、编辑、删除售货机记录
- 字段：机型、地点、售卖品类、是否运作、照片描述

### 厂商品牌

- 厂商列表，支持按国家筛选（筛选项从全部数据提取，筛选后不会消失）
- 新增、编辑、删除厂商记录
- 字段：品牌名称、所属国家、成立年份、简介

### 维保记录

- 从售货机列表点击「维保」进入该机的维保历史；也可通过全局维保页面查看所有记录
- 全局维保列表页支持按售货机编号筛选
- 新增、编辑、删除维保记录
- 字段：关联售货机编号、维保日期、维保类型、经办人、维保说明

#### 页面

| 路径 | 说明 |
|------|------|
| `/manufacturers` | 厂商列表页 |
| `/manufacturers/new` | 新增厂商 |
| `/manufacturers/:id/edit` | 编辑厂商 |
| `/machines/:machineId/maintenances` | 某售货机的维保记录列表 |
| `/maintenances` | 全量维保记录列表（支持筛选） |
| `/maintenances/new` | 新增维保记录 |
| `/maintenances/:id/edit` | 编辑维保记录 |

## 未包含

登录、JWT、Redis、Docker、MySQL/PostgreSQL 等均未实现。

## API 概览

### 售货机

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/machines?operational=all\|true\|false` | 列表（运作状态筛选） |
| GET | `/api/machines/{id}` | 详情 |
| POST | `/api/machines` | 新增 |
| PUT | `/api/machines/{id}` | 更新 |
| DELETE | `/api/machines/{id}` | 删除 |

### 厂商

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/manufacturers?country=` | 列表（按国家筛选，空字符串表示全部） |
| GET | `/api/manufacturers/{id}` | 详情 |
| POST | `/api/manufacturers` | 新增 |
| PUT | `/api/manufacturers/{id}` | 更新 |
| DELETE | `/api/manufacturers/{id}` | 删除 |

厂商字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `brand_name` | string | 是 | 品牌名称 |
| `country` | string | 是 | 所属国家 |
| `founded_year` | integer | 是 | 成立年份（1800–2100） |
| `description` | string | 否 | 简介 |

### 维保记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/maintenances?machine_id=` | 列表（按售货机编号筛选，不传则返回全部） |
| GET | `/api/maintenances/{id}` | 详情 |
| POST | `/api/maintenances` | 新增 |
| PUT | `/api/maintenances/{id}` | 更新 |
| DELETE | `/api/maintenances/{id}` | 删除 |

维保记录字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `machine_id` | integer | 是 | 关联售货机编号 |
| `maintenance_date` | string | 是 | 维保日期（格式 YYYY-MM-DD） |
| `maintenance_type` | string | 是 | 维保类型（日常巡检 / 清洁保养 / 零部件更换 / 故障维修 / 系统升级 / 其他） |
| `handler` | string | 是 | 经办人 |
| `description` | string | 否 | 维保说明 |
