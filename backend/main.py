"""老式自动售货机机型图鉴 API。"""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from schemas import (
    Page,
    TagCreate, TagOut, TagUpdate,
    MachineCreate, MachineOut, MachineUpdate, MachineTagSet,
    ManufacturerCreate, ManufacturerOut, ManufacturerUpdate,
    MaintenanceCreate, MaintenanceOut, MaintenanceUpdate,
    InspectionCreate, InspectionOut,
    StatisticsOut, LocationStats, CategoryStats,
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


def row_to_tag(row) -> TagOut:
  """
   * 将数据库行转为标签响应模型。
   * @param {sqlite3.Row} row
   * @returns {TagOut}
  """
  return TagOut(
      id=row["id"],
      name=row["name"],
      color=row["color"],
  )


def get_machine_tags(conn, machine_id: int) -> list[TagOut]:
  """获取售货机关联的标签列表。"""
  rows = conn.execute(
      """
      SELECT t.id, t.name, t.color
      FROM tags t
      JOIN machine_tags mt ON t.id = mt.tag_id
      WHERE mt.machine_id = ?
      ORDER BY t.id ASC
      """,
      (machine_id,),
  ).fetchall()
  return [row_to_tag(row) for row in rows]


def row_to_machine(row, conn=None) -> MachineOut:
  """
   * 将数据库行转为响应模型。
   * @param {sqlite3.Row} row
   * @param {sqlite3.Connection | None} conn
   * @returns {MachineOut}
   """
  tags = []
  if conn is not None:
    tags = get_machine_tags(conn, row["id"])
  return MachineOut(
      id=row["id"],
      model_type=row["model_type"],
      location=row["location"],
      categories=row["categories"],
      is_operational=bool(row["is_operational"]),
      photo_description=row["photo_description"],
      manufacturing_year=row["manufacturing_year"],
      tags=tags,
  )


def set_machine_tags(conn, machine_id: int, tag_ids: list[int]) -> None:
  """设置售货机关联的标签。"""
  conn.execute("DELETE FROM machine_tags WHERE machine_id = ?", (machine_id,))
  for tag_id in tag_ids:
    tag_row = conn.execute("SELECT id FROM tags WHERE id = ?", (tag_id,)).fetchone()
    if tag_row is None:
      raise HTTPException(status_code=400, detail=f"标签 ID {tag_id} 不存在")
    conn.execute(
        "INSERT OR IGNORE INTO machine_tags (machine_id, tag_id) VALUES (?, ?)",
        (machine_id, tag_id),
    )


@app.get("/api/health")
def health() -> dict:
  """健康检查。"""
  return {"status": "ok"}


@app.get("/api/tags", response_model=list[TagOut])
def list_tags() -> list[TagOut]:
  """获取标签列表。"""
  conn = get_connection()
  try:
    rows = conn.execute("SELECT * FROM tags ORDER BY id ASC").fetchall()
    return [row_to_tag(row) for row in rows]
  finally:
    conn.close()


@app.get("/api/tags/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int) -> TagOut:
  """获取单个标签。"""
  conn = get_connection()
  try:
    row = conn.execute(
        "SELECT * FROM tags WHERE id = ?", (tag_id,)
    ).fetchone()
    if row is None:
      raise HTTPException(status_code=404, detail="标签不存在")
    return row_to_tag(row)
  finally:
    conn.close()


@app.post("/api/tags", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate) -> TagOut:
  """新增标签。"""
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM tags WHERE name = ?", (payload.name,)
    ).fetchone()
    if existing is not None:
      raise HTTPException(status_code=400, detail="标签名称已存在")
    cursor = conn.execute(
        """
        INSERT INTO tags (name, color)
        VALUES (?, ?)
        """,
        (payload.name, payload.color),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM tags WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_tag(row)
  finally:
    conn.close()


@app.put("/api/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, payload: TagUpdate) -> TagOut:
  """更新标签。"""
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM tags WHERE id = ?", (tag_id,)
    ).fetchone()
    if existing is None:
      raise HTTPException(status_code=404, detail="标签不存在")
    duplicate = conn.execute(
        "SELECT id FROM tags WHERE name = ? AND id != ?",
        (payload.name, tag_id),
    ).fetchone()
    if duplicate is not None:
      raise HTTPException(status_code=400, detail="标签名称已存在")
    conn.execute(
        """
        UPDATE tags
        SET name = ?, color = ?
        WHERE id = ?
        """,
        (payload.name, payload.color, tag_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM tags WHERE id = ?", (tag_id,)
    ).fetchone()
    return row_to_tag(row)
  finally:
    conn.close()


@app.delete("/api/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int) -> None:
  """删除标签。"""
  conn = get_connection()
  try:
    cursor = conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    conn.commit()
    if cursor.rowcount == 0:
      raise HTTPException(status_code=404, detail="标签不存在")
  finally:
    conn.close()


@app.get("/api/machines", response_model=Page[MachineOut])
def list_machines(
    operational: Literal["all", "true", "false"] = Query(
        "all", description="运作状态筛选：all / true / false"
    ),
    tag_id: int | None = Query(None, description="按标签 ID 筛选，None 表示全部"),
    keyword: str = Query("", description="关键词搜索，按机型、地点、售卖品类、照片描述模糊匹配"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
) -> Page[MachineOut]:
  """获取售货机列表，支持运作状态筛选、标签筛选、关键词搜索和分页。"""
  conn = get_connection()
  try:
    params: list = []
    conditions: list[str] = []

    if keyword.strip():
      kw = f"%{keyword.strip()}%"
      conditions.append("(m.model_type LIKE ? OR m.location LIKE ? OR m.categories LIKE ? OR m.photo_description LIKE ?)")
      params.extend([kw, kw, kw, kw])

    if operational == "true":
      conditions.append("m.is_operational = 1")
    elif operational == "false":
      conditions.append("m.is_operational = 0")

    where_clause = ""
    if conditions:
      where_clause = " WHERE " + " AND ".join(conditions)

    if tag_id is not None:
      base_sql = "SELECT DISTINCT m.* FROM machines m JOIN machine_tags mt ON m.id = mt.machine_id"
      tag_conditions = ["mt.tag_id = ?"]
      params.insert(0, tag_id)
      remaining_conditions = conditions
      if remaining_conditions:
        tag_conditions.extend(remaining_conditions)
      where_clause = " WHERE " + " AND ".join(tag_conditions)
    else:
      base_sql = "SELECT m.* FROM machines m"

    count_sql = base_sql.replace("m.*", "COUNT(DISTINCT m.id)", 1) + where_clause
    total_row = conn.execute(count_sql, params).fetchone()
    total = total_row[0] if total_row else 0

    offset = (page - 1) * page_size
    data_sql = base_sql + where_clause + " ORDER BY m.id ASC LIMIT ? OFFSET ?"
    data_params = params + [page_size, offset]
    rows = conn.execute(data_sql, data_params).fetchall()

    items = [row_to_machine(row, conn) for row in rows]
    return Page[MachineOut](items=items, total=total, page=page, page_size=page_size)
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
    return row_to_machine(row, conn)
  finally:
    conn.close()


@app.post("/api/machines", response_model=MachineOut, status_code=201)
def create_machine(payload: MachineCreate) -> MachineOut:
  """新增售货机。若 tag_ids 为 None 则不设置标签。"""
  conn = get_connection()
  try:
    cursor = conn.execute(
        """
        INSERT INTO machines (model_type, location, categories, is_operational, photo_description, manufacturing_year)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            payload.model_type,
            payload.location,
            payload.categories,
            int(payload.is_operational),
            payload.photo_description,
            payload.manufacturing_year,
        ),
    )
    machine_id = cursor.lastrowid
    if payload.tag_ids is not None:
      set_machine_tags(conn, machine_id, payload.tag_ids)
    conn.commit()
    row = conn.execute(
        "SELECT * FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    return row_to_machine(row, conn)
  finally:
    conn.close()


@app.put("/api/machines/{machine_id}", response_model=MachineOut)
def update_machine(machine_id: int, payload: MachineUpdate) -> MachineOut:
  """更新售货机。若 tag_ids 为 None 则不修改现有标签。"""
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
            is_operational = ?, photo_description = ?, manufacturing_year = ?
        WHERE id = ?
        """,
        (
            payload.model_type,
            payload.location,
            payload.categories,
            int(payload.is_operational),
            payload.photo_description,
            payload.manufacturing_year,
            machine_id,
        ),
    )
    if payload.tag_ids is not None:
      set_machine_tags(conn, machine_id, payload.tag_ids)
    conn.commit()
    row = conn.execute(
        "SELECT * FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    return row_to_machine(row, conn)
  finally:
    conn.close()


@app.put("/api/machines/{machine_id}/tags", response_model=list[TagOut])
def set_machine_tags_endpoint(machine_id: int, payload: MachineTagSet) -> list[TagOut]:
  """
  为售货机设置标签（专用接口）。
  传入标签编号列表，空数组表示清除所有标签。
  返回设置完成后该售货机关联的全部标签。
  """
  conn = get_connection()
  try:
    existing = conn.execute(
        "SELECT id FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()
    if existing is None:
      raise HTTPException(status_code=404, detail="售货机不存在")
    set_machine_tags(conn, machine_id, payload.tag_ids)
    conn.commit()
    return get_machine_tags(conn, machine_id)
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


def row_to_inspection(row) -> InspectionOut:
  """
   * 将数据库行转为巡检记录响应模型。
   * @param {sqlite3.Row} row
   * @returns {InspectionOut}
  """
  return InspectionOut(
      id=row["id"],
      machine_id=row["machine_id"],
      inspection_time=row["inspection_time"],
      result=row["result"],
      remark=row["remark"],
  )


@app.get("/api/inspections", response_model=list[InspectionOut])
def list_inspections(
    result: Literal["all", "正常", "异常"] = Query(
        "all", description="巡检结果筛选：all / 正常 / 异常"
    ),
) -> list[InspectionOut]:
  """获取巡检记录列表，支持按巡检结果筛选。"""
  conn = get_connection()
  try:
    sql = "SELECT * FROM inspections"
    params: list = []
    if result == "正常":
      sql += " WHERE result = ?"
      params.append("正常")
    elif result == "异常":
      sql += " WHERE result = ?"
      params.append("异常")
    sql += " ORDER BY inspection_time DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    return [row_to_inspection(row) for row in rows]
  finally:
    conn.close()


@app.post("/api/inspections", response_model=InspectionOut, status_code=201)
def create_inspection(payload: InspectionCreate) -> InspectionOut:
  """新增巡检记录。"""
  conn = get_connection()
  try:
    if not _machine_exists(conn, payload.machine_id):
      raise HTTPException(status_code=404, detail="关联的售货机不存在")
    cursor = conn.execute(
        """
        INSERT INTO inspections (machine_id, inspection_time, result, remark)
        VALUES (?, ?, ?, ?)
        """,
        (
            payload.machine_id,
            payload.inspection_time,
            payload.result,
            payload.remark,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM inspections WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_inspection(row)
  finally:
    conn.close()


@app.get("/api/statistics", response_model=StatisticsOut)
def get_statistics() -> StatisticsOut:
  """获取数据统计看板的聚合数据。"""
  conn = get_connection()
  try:
    total_row = conn.execute(
        "SELECT COUNT(*) as total FROM machines"
    ).fetchone()
    total_machines = total_row["total"] if total_row else 0

    operational_row = conn.execute(
        "SELECT COUNT(*) as count FROM machines WHERE is_operational = 1"
    ).fetchone()
    operational_count = operational_row["count"] if operational_row else 0

    out_of_service_count = total_machines - operational_count

    location_rows = conn.execute(
        """
        SELECT location, COUNT(*) as count
        FROM machines
        GROUP BY location
        ORDER BY count DESC, location ASC
        """
    ).fetchall()
    location_distribution = [
        LocationStats(location=row["location"], count=row["count"])
        for row in location_rows
    ]

    category_rows = conn.execute(
        "SELECT categories FROM machines"
    ).fetchall()
    category_counts: dict[str, int] = {}
    for row in category_rows:
      categories = row["categories"]
      if categories:
        for cat in categories.split("、"):
          cat = cat.strip()
          if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    sorted_categories = sorted(
        category_counts.items(),
        key=lambda x: (-x[1], x[0])
    )
    category_rankings = [
        CategoryStats(category=cat, count=count)
        for cat, count in sorted_categories
    ]

    return StatisticsOut(
        total_machines=total_machines,
        operational_count=operational_count,
        out_of_service_count=out_of_service_count,
        location_distribution=location_distribution,
        category_rankings=category_rankings,
    )
  finally:
    conn.close()
