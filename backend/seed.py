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


MANUFACTURER_SEED_DATA = [
    {
        "brand_name": "National",
        "country": "日本",
        "founded_year": 1925,
        "description": "松下电器旗下经典品牌，以家用与商用售货机闻名，红色机身是其标志",
    },
    {
        "brand_name": "Fuji Electric",
        "country": "日本",
        "founded_year": 1923,
        "description": "富士电机，日本老牌机电企业，生产的售货机以热饮与面食机型见长",
    },
    {
        "brand_name": "Sanden",
        "country": "日本",
        "founded_year": 1943,
        "description": "三电集团，最初从事汽车空调压缩机，后拓展至自动售货机领域",
    },
    {
        "brand_name": "Crane",
        "country": "美国",
        "founded_year": 1855,
        "description": "Crane 公司是全球最早的商用售货机制造商之一，螺旋出货机构为其专利",
    },
    {
        "brand_name": "Sanyo",
        "country": "日本",
        "founded_year": 1947,
        "description": "三洋电机，曾生产大量饮料售货机，蓝白配色为经典涂装",
    },
]

MAINTENANCE_SEED_DATA = [
    {
        "machine_id": 1,
        "maintenance_date": "2026-05-20",
        "maintenance_type": "日常巡检",
        "handler": "张伟",
        "description": "检查电源线及制冷系统运转正常，补货通道无阻塞",
    },
    {
        "machine_id": 1,
        "maintenance_date": "2026-06-10",
        "maintenance_type": "故障维修",
        "handler": "李强",
        "description": "投币口传感器失灵，更换全新传感器模块后恢复正常",
    },
    {
        "machine_id": 3,
        "maintenance_date": "2026-06-15",
        "maintenance_type": "清洁保养",
        "handler": "王芳",
        "description": "机身外观清洗、玻璃门抛光，内部灯管更换为LED灯条",
    },
]


def seed_if_empty() -> None:
    """
     * 若表为空则写入 seed 数据。
     """
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO machines (model_type, location, categories, is_operational, photo_description)
                VALUES (:model_type, :location, :categories, :is_operational, :photo_description)
                """,
                SEED_DATA,
            )

        mfr_count = conn.execute("SELECT COUNT(*) FROM manufacturers").fetchone()[0]
        if mfr_count == 0:
            conn.executemany(
                """
                INSERT INTO manufacturers (brand_name, country, founded_year, description)
                VALUES (:brand_name, :country, :founded_year, :description)
                """,
                MANUFACTURER_SEED_DATA,
            )

        mnt_count = conn.execute("SELECT COUNT(*) FROM maintenances").fetchone()[0]
        if mnt_count == 0:
            conn.executemany(
                """
                INSERT INTO maintenances (machine_id, maintenance_date, maintenance_type, handler, description)
                VALUES (:machine_id, :maintenance_date, :maintenance_type, :handler, :description)
                """,
                MAINTENANCE_SEED_DATA,
            )

        conn.commit()
    finally:
        conn.close()
