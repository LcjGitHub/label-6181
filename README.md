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

### 巡检打卡

- 巡检打卡页：选择售货机、巡检时间（精确到分钟）、巡检结果（正常/异常），异常时必填异常说明
- 巡检历史列表页：查看全部巡检记录，支持按巡检结果（全部/正常/异常）筛选
- 售货机列表操作列提供「巡检」快捷入口，自动带入售货机编号
- 启动时自动写入 5 条示例巡检数据

### 机型标签

- 标签管理页：维护标签名称与颜色标识（12 色预设 + 自定义颜色选择器），支持增删改查
- 标签与售货机多对多关联：一台售货机可绑定多个标签，标签可复用
- 售货机表单页：多选标签控件，选项带色块标识，空状态提示跳转标签管理
- 售货机列表页：新增「按标签筛选」下拉，操作与运作状态筛选联动；列表新增「标签」列展示彩色标签
- 售货机列表与售货机详情加载时：标签接口与售货机接口**并行请求**，分别捕获异常，互不阻塞
- 启动时自动写入 8 条示例标签与 13 条售货机标签关联数据

#### 页面

| 路径 | 说明 |
|------|------|
| `/tags` | 标签列表页（标签管理） |
| `/tags/new` | 新增标签 |
| `/tags/:id/edit` | 编辑标签 |
| `/manufacturers` | 厂商列表页 |
| `/manufacturers/new` | 新增厂商 |
| `/manufacturers/:id/edit` | 编辑厂商 |
| `/machines/:machineId/maintenances` | 某售货机的维保记录列表 |
| `/maintenances` | 全量维保记录列表（支持筛选） |
| `/maintenances/new` | 新增维保记录 |
| `/maintenances/:id/edit` | 编辑维保记录 |
| `/inspections` | 巡检历史列表页（支持按巡检结果筛选） |
| `/inspections/new` | 新增巡检打卡 |

## 未包含

登录、JWT、Redis、Docker、MySQL/PostgreSQL 等均未实现。

## API 概览

### 售货机

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/machines?operational=all\|true\|false&tag_id=` | 列表（运作状态筛选 + 标签筛选，`tag_id` 为可选整数） |
| GET | `/api/machines/{id}` | 详情（响应体包含关联的 `tags` 列表） |
| POST | `/api/machines` | 新增（请求体中 `tag_ids` 可选，省略时不设置标签） |
| PUT | `/api/machines/{id}` | 更新（请求体中 `tag_ids` 可选，省略时不修改现有标签） |
| PUT | `/api/machines/{id}/tags` | **为售货机设置标签（专用接口）**，传入 `{ tag_ids: [1,2,3] }`，空数组表示清除 |
| DELETE | `/api/machines/{id}` | 删除 |

售货机字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model_type` | string | 是 | 机型 |
| `location` | string | 是 | 地点 |
| `categories` | string | 是 | 售卖品类 |
| `is_operational` | boolean | 否 | 是否运作，默认 `true` |
| `photo_description` | string | 否 | 照片描述，默认空字符串 |
| `tag_ids` | number[] \| null | 否 | **仅用于创建/更新请求体**，关联标签 ID 列表；省略（null）时不操作标签 |
| `tags` | Tag[] | — | **仅用于响应体**，该售货机关联的完整标签列表（含 id / name / color） |

### 机型标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tags` | 获取全部标签列表 |
| GET | `/api/tags/{id}` | 获取单个标签 |
| POST | `/api/tags` | 新增标签（`name` 唯一） |
| PUT | `/api/tags/{id}` | 更新标签（`name` 唯一校验） |
| DELETE | `/api/tags/{id}` | 删除标签（售货机上的关联会被级联清除） |

标签字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 标签名称，1–50 字符，全局唯一 |
| `color` | string | 否 | 颜色标识（HEX 色值），默认 `#18a058` |

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

### 巡检记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/inspections?result=all\|正常\|异常` | 列表（按巡检结果筛选：全部 / 正常 / 异常） |
| POST | `/api/inspections` | 新增 |

巡检记录字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `machine_id` | integer | 是 | 售货机编号（外键关联 machines 表） |
| `inspection_time` | string | 是 | 巡检时间（格式 YYYY-MM-DD HH:mm，精确到分钟） |
| `result` | string | 是 | 巡检结果，仅允许：`正常` 或 `异常` |
| `remark` | string | 否 | 异常说明（结果为异常时建议填写） |
