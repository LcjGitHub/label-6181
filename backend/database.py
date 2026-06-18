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
     * 创建售货机表（若不存在）。
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
        conn.commit()
    finally:
        conn.close()
