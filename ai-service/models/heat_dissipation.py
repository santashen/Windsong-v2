from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class PressureUnit(str, Enum):
    PA = "Pa"
    KPA = "kPa"
    MPA = "MPa"
    BAR = "bar"


class FlowRateUnit(str, Enum):
    KG_PER_S = "kg/s"
    L_PER_MIN = "L/min"
    M3_PER_H = "m3/h"
    M3_PER_H_SYMBOL = "m³/h"


class UnitValue(BaseModel):
    value: float
    unit: str = Field(min_length=1)

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        return value


class TemperatureRowInput(BaseModel):
    tinC: float
    toutC: float

    @field_validator("tinC", "toutC")
    @classmethod
    def temperature_must_be_finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("temperature must be finite")
        return value


class HeatDissipationRequest(BaseModel):
    fluid: str = Field(min_length=1, max_length=100)
    pressure: UnitValue
    flowRate: UnitValue
    rows: list[TemperatureRowInput]


class HeatDissipationResultRow(BaseModel):
    index: int = Field(ge=1)
    tinC: float
    toutC: float
    qW: float
    qDisplay: str


class HeatDissipationResponse(BaseModel):
    unit: str = "W"
    results: list[HeatDissipationResultRow]


class HeatDissipationFluidItem(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)


class HeatDissipationFluidListResponse(BaseModel):
    items: list[HeatDissipationFluidItem]
