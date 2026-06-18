"""Pydantic 请求/响应模型。"""

from typing import Literal

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签公共字段。"""

    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: str = Field("#18a058", min_length=4, max_length=20, description="颜色标识")


class TagCreate(TagBase):
    """创建标签。"""


class TagUpdate(TagBase):
    """更新标签。"""


class TagOut(TagBase):
    """标签响应。"""

    id: int

    model_config = {"from_attributes": True}


class MachineBase(BaseModel):
    """售货机公共字段。"""

    model_type: str = Field(..., min_length=1, description="机型")
    location: str = Field(..., min_length=1, description="地点")
    categories: str = Field(..., min_length=1, description="售卖品类")
    is_operational: bool = Field(True, description="是否运作")
    photo_description: str = Field("", description="照片描述")


class MachineCreate(MachineBase):
    """创建售货机。"""

    tag_ids: list[int] = Field([], description="关联标签 ID 列表")


class MachineUpdate(MachineBase):
    """更新售货机。"""

    tag_ids: list[int] = Field([], description="关联标签 ID 列表")


class MachineOut(MachineBase):
    """售货机响应。"""

    id: int
    tags: list[TagOut] = Field([], description="关联标签列表")

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


InspectionResult = Literal["正常", "异常"]


class InspectionBase(BaseModel):
    """巡检记录公共字段。"""

    machine_id: int = Field(..., description="售货机编号")
    inspection_time: str = Field(..., min_length=1, description="巡检时间，格式 YYYY-MM-DD HH:mm")
    result: InspectionResult = Field(..., description="巡检结果：正常 或 异常")
    remark: str = Field("", description="异常说明")


class InspectionCreate(InspectionBase):
    """创建巡检记录。"""


class InspectionOut(InspectionBase):
    """巡检记录响应。"""

    id: int

    model_config = {"from_attributes": True}
