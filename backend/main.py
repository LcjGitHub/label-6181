"""老式自动售货机机型图鉴 API。"""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import MachineCreate, MachineOut, MachineUpdate
from seed import seed_if_empty

app = FastAPI(title="老式自动售货机机型图鉴", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3101", "http://127.0.0.1:3101"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
  """启动时初始化数据库并 seed。"""
  init_db()
  seed_if_empty()


def row_to_machine(row) -> MachineOut:
  """
   * 将数据库行转为响应模型。
   * @param {sqlite3.Row} row
   * @returns {MachineOut}
   """
  return MachineOut(
      id=row["id"],
      model_type=row["model_type"],
      location=row["location"],
      categories=row["categories"],
      is_operational=bool(row["is_operational"]),
      photo_description=row["photo_description"],
  )


@app.get("/api/health")
def health() -> dict:
  """健康检查。"""
  return {"status": "ok"}


@app.get("/api/machines", response_model=list[MachineOut])
def list_machines(
    operational: Literal["all", "true", "false"] = Query(
        "all", description="运作状态筛选：all / true / false"
    ),
) -> list[MachineOut]:
  """获取售货机列表，支持运作状态筛选。"""
  conn = get_connection()
  try:
    sql = "SELECT * FROM machines"
    params: list = []
    if operational == "true":
      sql += " WHERE is_operational = 1"
    elif operational == "false":
      sql += " WHERE is_operational = 0"
    sql += " ORDER BY id ASC"
    rows = conn.execute(sql, params).fetchall()
    return [row_to_machine(row) for row in rows]
  finally:
    conn.close()


@app.get("/api/machines/{machine_id}", response_model=MachineOut)
def get_machine(machine_id: int) -> MachineOut:
  """获取单台售货机。"""
  conn = get_connection()
  try:
    row = conn.execute(
        "SELECT * FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    if row is None:
      raise HTTPException(status_code=404, detail="售货机不存在")
    return row_to_machine(row)
  finally:
    conn.close()


@app.post("/api/machines", response_model=MachineOut, status_code=201)
def create_machine(payload: MachineCreate) -> MachineOut:
  """新增售货机。"""
  conn = get_connection()
  try:
    cursor = conn.execute(
        """
        INSERT INTO machines (model_type, location, categories, is_operational, photo_description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            payload.model_type,
            payload.location,
            payload.categories,
            int(payload.is_operational),
            payload.photo_description,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM machines WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_machine(row)
  finally:
    conn.close()


@app.put("/api/machines/{machine_id}", response_model=MachineOut)
def update_machine(machine_id: int, payload: MachineUpdate) -> MachineOut:
  """更新售货机。"""
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    if existing is None:
      raise HTTPException(status_code=404, detail="售货机不存在")
    conn.execute(
        """
        UPDATE machines
        SET model_type = ?, location = ?, categories = ?,
            is_operational = ?, photo_description = ?
        WHERE id = ?
        """,
        (
            payload.model_type,
            payload.location,
            payload.categories,
            int(payload.is_operational),
            payload.photo_description,
            machine_id,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    return row_to_machine(row)
  finally:
    conn.close()


@app.delete("/api/machines/{machine_id}", status_code=204)
def delete_machine(machine_id: int) -> None:
  """删除售货机。"""
  conn = get_connection()
  try:
    cursor = conn.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
    conn.commit()
    if cursor.rowcount == 0:
      raise HTTPException(status_code=404, detail="售货机不存在")
  finally:
    conn.close()
