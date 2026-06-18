"""初始化示例数据。"""

from database import get_connection

SEED_DATA = [
    {
        "model_type": "National Vendo 44",
        "location": "东京涩谷站东口",
        "categories": "罐装饮料、咖啡",
        "is_operational": 1,
        "photo_description": "经典红色机身，玻璃前门可看到整排可乐罐",
    },
    {
        "model_type": "Fuji Electric FVR-30",
        "location": "大阪道顿堀步行街",
        "categories": "热饮、方便面",
        "is_operational": 1,
        "photo_description": "米白色外壳，顶部有富士电机铭牌，按键式选货",
    },
    {
        "model_type": "Sanden SD-40",
        "location": "京都祇园花见小路",
        "categories": "茶饮、矿泉水",
        "is_operational": 0,
        "photo_description": "机身褪色，玻璃门有裂纹，内部灯管已熄灭",
    },
    {
        "model_type": "Crane National 147",
        "location": "名古屋荣地下街",
        "categories": "零食、口香糖",
        "is_operational": 1,
        "photo_description": "螺旋式出货口，侧面贴有昭和风格广告画",
    },
    {
        "model_type": "Sanyo VM-2000",
        "location": "横滨红砖仓库附近",
        "categories": "果汁、运动饮料",
        "is_operational": 0,
        "photo_description": "蓝白配色，投币口生锈，显示屏数字残缺",
    },
]


def seed_if_empty() -> None:
    """
     * 若表为空则写入 5 条 seed 数据。
     """
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        if count > 0:
            return
        conn.executemany(
            """
            INSERT INTO machines (model_type, location, categories, is_operational, photo_description)
            VALUES (:model_type, :location, :categories, :is_operational, :photo_description)
            """,
            SEED_DATA,
        )
        conn.commit()
    finally:
        conn.close()
