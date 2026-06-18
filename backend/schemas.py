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
