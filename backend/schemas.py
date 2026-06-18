"""Pydantic 请求/响应模型。"""

from pydantic import BaseModel, Field


class MachineBase(BaseModel):
    """售货机公共字段。"""

    model_type: str = Field(..., min_length=1, description="机型")
    location: str = Field(..., min_length=1, description="地点")
    categories: str = Field(..., min_length=1, description="售卖品类")
    is_operational: bool = Field(True, description="是否运作")
    photo_description: str = Field("", description="照片描述")


class MachineCreate(MachineBase):
    """创建售货机。"""


class MachineUpdate(MachineBase):
    """更新售货机。"""


class MachineOut(MachineBase):
    """售货机响应。"""

    id: int

    model_config = {"from_attributes": True}


class ManufacturerBase(BaseModel):
    """厂商公共字段。"""

    brand_name: str = Field(..., min_length=1, description="品牌名称")
    country: str = Field(..., min_length=1, description="所属国家")
    founded_year: int = Field(..., ge=1800, le=2100, description="成立年份")
    description: str = Field("", description="简介")


class ManufacturerCreate(ManufacturerBase):
    """创建厂商。"""


class ManufacturerUpdate(ManufacturerBase):
    """更新厂商。"""


class ManufacturerOut(ManufacturerBase):
    """厂商响应。"""

    id: int

    model_config = {"from_attributes": True}


class MaintenanceBase(BaseModel):
    """维保记录公共字段。"""

    machine_id: int = Field(..., description="关联售货机编号")
    maintenance_date: str = Field(..., min_length=1, description="维保日期，格式 YYYY-MM-DD")
    maintenance_type: str = Field(..., min_length=1, description="维保类型")
    handler: str = Field(..., min_length=1, description="经办人")
    description: str = Field("", description="维保说明")


class MaintenanceCreate(MaintenanceBase):
    """创建维保记录。"""


class MaintenanceUpdate(MaintenanceBase):
    """更新维保记录。"""


class MaintenanceOut(MaintenanceBase):
    """维保记录响应。"""

    id: int

    model_config = {"from_attributes": True}


class InspectionBase(BaseModel):
    """巡检记录公共字段。"""

    machine_id: int = Field(..., description="售货机编号")
    inspection_time: str = Field(..., min_length=1, description="巡检时间，格式 YYYY-MM-DD HH:mm")
    result: str = Field(..., min_length=1, description="巡检结果：正常 或 异常")
    remark: str = Field("", description="异常说明")


class InspectionCreate(InspectionBase):
    """创建巡检记录。"""


class InspectionOut(InspectionBase):
    """巡检记录响应。"""

    id: int

    model_config = {"from_attributes": True}
