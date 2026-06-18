"""SQLite 数据库连接与初始化。"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "vending.db"


def get_connection() -> sqlite3.Connection:
    """
     * 获取 SQLite 连接，启用行字典模式。
     * @returns {sqlite3.Connection}
     """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
     * 创建售货机表与厂商表（若不存在）。
     """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT NOT NULL,
                location TEXT NOT NULL,
                categories TEXT NOT NULL,
                is_operational INTEGER NOT NULL DEFAULT 1,
                photo_description TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                country TEXT NOT NULL,
                founded_year INTEGER NOT NULL,
                description TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER NOT NULL,
                maintenance_date TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                handler TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER NOT NULL,
                inspection_time TEXT NOT NULL,
                result TEXT NOT NULL,
                remark TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#18a058'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS machine_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                UNIQUE(machine_id, tag_id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
