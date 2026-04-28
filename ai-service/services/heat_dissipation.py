from __future__ import annotations

from dataclasses import dataclass

from models.heat_dissipation import FlowRateUnit, HeatDissipationRequest, PressureUnit, UnitValue


MAX_ROWS = 500


@dataclass(frozen=True)
class HeatDissipationError(Exception):
    code: str
    message: str
    row_index: int | None = None


PRESSURE_TO_PA = {
    PressureUnit.PA.value: 1.0,
    PressureUnit.KPA.value: 1_000.0,
    PressureUnit.MPA.value: 1_000_000.0,
    PressureUnit.BAR.value: 100_000.0,
}

VOLUME_FLOW_TO_M3_PER_S = {
    FlowRateUnit.L_PER_MIN.value: 1.0 / 1000.0 / 60.0,
    FlowRateUnit.M3_PER_H.value: 1.0 / 3600.0,
    FlowRateUnit.M3_PER_H_SYMBOL.value: 1.0 / 3600.0,
}


class HeatDissipationService:
    def validate_request(self, payload: HeatDissipationRequest) -> None:
        fluid = payload.fluid.strip()
        if not fluid:
            raise HeatDissipationError("INVALID_FLUID", "请选择 CoolProp 支持的有效工质")
        if payload.pressure.value <= 0:
            raise HeatDissipationError("INVALID_PRESSURE", "压力必须大于 0")
        if payload.flowRate.value < 0:
            raise HeatDissipationError("INVALID_FLOW_RATE", "流量不能为负数")
        if len(payload.rows) == 0:
            raise HeatDissipationError("INVALID_ROWS", "请至少输入一组温度数据")
        if len(payload.rows) > MAX_ROWS:
            raise HeatDissipationError("INVALID_ROWS", f"单次最多支持 {MAX_ROWS} 组温度数据")
        self.convert_pressure_to_pa(payload.pressure)
        self.convert_flow_rate_to_kg_per_s(payload.flowRate, density_kg_per_m3=1.0)

    def convert_pressure_to_pa(self, pressure: UnitValue) -> float:
        multiplier = PRESSURE_TO_PA.get(pressure.unit)
        if multiplier is None:
            raise HeatDissipationError("INVALID_PRESSURE", "压力单位无效")
        value = pressure.value * multiplier
        if value <= 0:
            raise HeatDissipationError("INVALID_PRESSURE", "压力必须大于 0")
        return value

    def convert_temperature_c_to_k(self, temperature_c: float) -> float:
        return temperature_c + 273.15

    def convert_volume_flow_to_m3_per_s(self, flow_rate: UnitValue) -> float:
        multiplier = VOLUME_FLOW_TO_M3_PER_S.get(flow_rate.unit)
        if multiplier is None:
            raise HeatDissipationError("INVALID_FLOW_RATE", "体积流量单位无效")
        if flow_rate.value < 0:
            raise HeatDissipationError("INVALID_FLOW_RATE", "流量不能为负数")
        return flow_rate.value * multiplier

    def convert_flow_rate_to_kg_per_s(
        self,
        flow_rate: UnitValue,
        density_kg_per_m3: float | None = None,
    ) -> float:
        if flow_rate.value < 0:
            raise HeatDissipationError("INVALID_FLOW_RATE", "流量不能为负数")
        if flow_rate.unit == FlowRateUnit.KG_PER_S.value:
            return flow_rate.value
        if flow_rate.unit in VOLUME_FLOW_TO_M3_PER_S:
            if density_kg_per_m3 is None or density_kg_per_m3 <= 0:
                raise HeatDissipationError("INVALID_FLOW_RATE", "体积流量换算需要有效密度")
            return self.convert_volume_flow_to_m3_per_s(flow_rate) * density_kg_per_m3
        raise HeatDissipationError("INVALID_FLOW_RATE", "流量单位无效")
