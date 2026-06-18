"""老式自动售货机机型图鉴 API。"""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import (
    MachineCreate, MachineOut, MachineUpdate,
    ManufacturerCreate, ManufacturerOut, ManufacturerUpdate,
    MaintenanceCreate, MaintenanceOut, MaintenanceUpdate,
)
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


def row_to_manufacturer(row) -> ManufacturerOut:
  return ManufacturerOut(
      id=row["id"],
      brand_name=row["brand_name"],
      country=row["country"],
      founded_year=row["founded_year"],
      description=row["description"],
  )


@app.get("/api/manufacturers", response_model=list[ManufacturerOut])
def list_manufacturers(
    country: str = Query("", description="按国家筛选，空字符串表示全部"),
) -> list[ManufacturerOut]:
  """获取厂商列表，支持按国家筛选。"""
  conn = get_connection()
  try:
    sql = "SELECT * FROM manufacturers"
    params: list = []
    if country:
      sql += " WHERE country = ?"
      params.append(country)
    sql += " ORDER BY id ASC"
    rows = conn.execute(sql, params).fetchall()
    return [row_to_manufacturer(row) for row in rows]
  finally:
    conn.close()


@app.get("/api/manufacturers/{manufacturer_id}", response_model=ManufacturerOut)
def get_manufacturer(manufacturer_id: int) -> ManufacturerOut:
  """获取单个厂商。"""
  conn = get_connection()
  try:
    row = conn.execute(
        "SELECT * FROM manufacturers WHERE id = ?", (manufacturer_id,)
    ).fetchone()
    if row is None:
      raise HTTPException(status_code=404, detail="厂商不存在")
    return row_to_manufacturer(row)
  finally:
    conn.close()


@app.post("/api/manufacturers", response_model=ManufacturerOut, status_code=201)
def create_manufacturer(payload: ManufacturerCreate) -> ManufacturerOut:
  """新增厂商。"""
  conn = get_connection()
  try:
    cursor = conn.execute(
        """
        INSERT INTO manufacturers (brand_name, country, founded_year, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            payload.brand_name,
            payload.country,
            payload.founded_year,
            payload.description,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM manufacturers WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_manufacturer(row)
  finally:
    conn.close()


@app.put("/api/manufacturers/{manufacturer_id}", response_model=ManufacturerOut)
def update_manufacturer(manufacturer_id: int, payload: ManufacturerUpdate) -> ManufacturerOut:
  """更新厂商。"""
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM manufacturers WHERE id = ?", (manufacturer_id,)
    ).fetchone()
    if existing is None:
      raise HTTPException(status_code=404, detail="厂商不存在")
    conn.execute(
        """
        UPDATE manufacturers
        SET brand_name = ?, country = ?, founded_year = ?, description = ?
        WHERE id = ?
        """,
        (
            payload.brand_name,
            payload.country,
            payload.founded_year,
            payload.description,
            manufacturer_id,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM manufacturers WHERE id = ?", (manufacturer_id,)
    ).fetchone()
    return row_to_manufacturer(row)
  finally:
    conn.close()


@app.delete("/api/manufacturers/{manufacturer_id}", status_code=204)
def delete_manufacturer(manufacturer_id: int) -> None:
  """删除厂商。"""
  conn = get_connection()
  try:
    cursor = conn.execute("DELETE FROM manufacturers WHERE id = ?", (manufacturer_id,))
    conn.commit()
    if cursor.rowcount == 0:
      raise HTTPException(status_code=404, detail="厂商不存在")
  finally:
    conn.close()


def row_to_maintenance(row) -> MaintenanceOut:
  """
   * 将数据库行转为维保记录响应模型。
   * @param {sqlite3.Row} row
   * @returns {MaintenanceOut}
  """
  return MaintenanceOut(
      id=row["id"],
      machine_id=row["machine_id"],
      maintenance_date=row["maintenance_date"],
      maintenance_type=row["maintenance_type"],
      handler=row["handler"],
      description=row["description"],
  )


def _machine_exists(conn, machine_id: int) -> bool:
  """检查售货机是否存在。"""
  row = conn.execute("SELECT id FROM machines WHERE id = ?", (machine_id,)).fetchone()
  return row is not None


@app.get("/api/maintenances", response_model=list[MaintenanceOut])
def list_maintenances(
    machine_id: int | None = Query(None, description="按售货机编号筛选，None 表示全部"),
) -> list[MaintenanceOut]:
  """获取维保记录列表，支持按售货机编号筛选。"""
  conn = get_connection()
  try:
    sql = "SELECT * FROM maintenances"
    params: list = []
    if machine_id is not None:
      sql += " WHERE machine_id = ?"
      params.append(machine_id)
    sql += " ORDER BY maintenance_date DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    return [row_to_maintenance(row) for row in rows]
  finally:
    conn.close()


@app.get("/api/maintenances/{maintenance_id}", response_model=MaintenanceOut)
def get_maintenance(maintenance_id: int) -> MaintenanceOut:
  """获取单条维保记录。"""
  conn = get_connection()
  try:
    row = conn.execute(
        "SELECT * FROM maintenances WHERE id = ?", (maintenance_id,)
    ).fetchone()
    if row is None:
      raise HTTPException(status_code=404, detail="维保记录不存在")
    return row_to_maintenance(row)
  finally:
    conn.close()


@app.post("/api/maintenances", response_model=MaintenanceOut, status_code=201)
def create_maintenance(payload: MaintenanceCreate) -> MaintenanceOut:
  """新增维保记录。"""
  conn = get_connection()
  try:
    if not _machine_exists(conn, payload.machine_id):
      raise HTTPException(status_code=404, detail="关联的售货机不存在")
    cursor = conn.execute(
        """
        INSERT INTO maintenances (machine_id, maintenance_date, maintenance_type, handler, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            payload.machine_id,
            payload.maintenance_date,
            payload.maintenance_type,
            payload.handler,
            payload.description,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM maintenances WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_maintenance(row)
  finally:
    conn.close()


@app.put("/api/maintenances/{maintenance_id}", response_model=MaintenanceOut)
def update_maintenance(maintenance_id: int, payload: MaintenanceUpdate) -> MaintenanceOut:
  """更新维保记录。"""
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM maintenances WHERE id = ?", (maintenance_id,)
    ).fetchone()
    if existing is None:
      raise HTTPException(status_code=404, detail="维保记录不存在")
    if not _machine_exists(conn, payload.machine_id):
      raise HTTPException(status_code=404, detail="关联的售货机不存在")
    conn.execute(
        """
        UPDATE maintenances
        SET machine_id = ?, maintenance_date = ?, maintenance_type = ?,
            handler = ?, description = ?
        WHERE id = ?
        """,
        (
            payload.machine_id,
            payload.maintenance_date,
            payload.maintenance_type,
            payload.handler,
            payload.description,
            maintenance_id,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM maintenances WHERE id = ?", (maintenance_id,)
    ).fetchone()
    return row_to_maintenance(row)
  finally:
    conn.close()


@app.delete("/api/maintenances/{maintenance_id}", status_code=204)
def delete_maintenance(maintenance_id: int) -> None:
  """删除维保记录。"""
  conn = get_connection()
  try:
    cursor = conn.execute("DELETE FROM maintenances WHERE id = ?", (maintenance_id,))
    conn.commit()
    if cursor.rowcount == 0:
      raise HTTPException(status_code=404, detail="维保记录不存在")
  finally:
    conn.close()
