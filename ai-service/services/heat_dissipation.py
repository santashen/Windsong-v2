from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from CoolProp.CoolProp import PropsSI, get_global_param_string

from models.heat_dissipation import (
    FlowRateUnit,
    HeatDissipationFluidItem,
    HeatDissipationFluidListResponse,
    HeatDissipationRequest,
    HeatDissipationResponse,
    HeatDissipationResultRow,
    PressureUnit,
    UnitValue,
)


MAX_ROWS = 500
DEFAULT_FLUID_LIMIT = 20
MAX_FLUID_LIMIT = 50
COMMON_FLUIDS = ["Water", "Air", "R134a", "R22", "R32", "R410A", "R1234yf", "Ammonia", "CO2"]


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
    def search_fluids(
        self,
        query: str | None = None,
        limit: int = DEFAULT_FLUID_LIMIT,
    ) -> HeatDissipationFluidListResponse:
        normalized_query = (query or "").strip().lower()
        normalized_limit = min(max(limit, 1), MAX_FLUID_LIMIT)
        fluids = self.get_supported_fluids()

        if normalized_query:
            matches = [fluid for fluid in fluids if normalized_query in fluid.lower()]
        else:
            common = [fluid for fluid in COMMON_FLUIDS if fluid in fluids]
            remaining = [fluid for fluid in fluids if fluid not in common]
            matches = common + remaining

        return HeatDissipationFluidListResponse(
            items=[
                HeatDissipationFluidItem(name=fluid, aliases=[fluid.lower()])
                for fluid in matches[:normalized_limit]
            ]
        )

    @lru_cache(maxsize=1)
    def get_supported_fluids(self) -> tuple[str, ...]:
        fluids = get_global_param_string("fluids_list").split(",")
        cleaned_fluids = [fluid.strip() for fluid in fluids if fluid.strip()]
        return tuple(sorted(cleaned_fluids, key=str.lower))

    def calculate(self, payload: HeatDissipationRequest) -> HeatDissipationResponse:
        fluid = self.validate_request(payload)
        pressure_pa = self.convert_pressure_to_pa(payload.pressure)
        results = []

        for index, row in enumerate(payload.rows, start=1):
            tin_k = self.convert_temperature_c_to_k(row.tinC)
            tout_k = self.convert_temperature_c_to_k(row.toutC)
            mass_flow_kg_per_s = self.get_mass_flow_kg_per_s(
                payload.flowRate,
                fluid,
                tin_k,
                pressure_pa,
                index,
            )
            h_in = self.get_enthalpy_j_per_kg(fluid, tin_k, pressure_pa, index)
            h_out = self.get_enthalpy_j_per_kg(fluid, tout_k, pressure_pa, index)
            q_w = mass_flow_kg_per_s * (h_out - h_in)
            results.append(
                HeatDissipationResultRow(
                    index=index,
                    tinC=row.tinC,
                    toutC=row.toutC,
                    qW=q_w,
                    qDisplay=self.format_q_display(q_w),
                )
            )

        return HeatDissipationResponse(results=results)

    def validate_request(self, payload: HeatDissipationRequest) -> str:
        fluid = payload.fluid.strip()
        if not fluid:
            raise HeatDissipationError("INVALID_FLUID", "请选择 CoolProp 支持的有效工质")
        canonical_fluid = self.normalize_fluid(fluid)
        if payload.pressure.value <= 0:
            raise HeatDissipationError("INVALID_PRESSURE", "压力必须大于 0")
        if payload.flowRate.value < 0:
            raise HeatDissipationError("INVALID_FLOW_RATE", "流量不能为负数")
        if len(payload.rows) == 0:
            raise HeatDissipationError("INVALID_ROWS", "请至少输入一组温度数据")
        if len(payload.rows) > MAX_ROWS:
            raise HeatDissipationError("INVALID_ROWS", f"单次最多支持 {MAX_ROWS} 组温度数据")
        self.convert_pressure_to_pa(payload.pressure)
        if payload.flowRate.unit == FlowRateUnit.KG_PER_S.value:
            self.convert_flow_rate_to_kg_per_s(payload.flowRate)
            return canonical_fluid
        if payload.flowRate.unit in VOLUME_FLOW_TO_M3_PER_S:
            self.convert_volume_flow_to_m3_per_s(payload.flowRate)
            return canonical_fluid
        raise HeatDissipationError("INVALID_FLOW_RATE", "流量单位无效")

    def normalize_fluid(self, fluid: str) -> str:
        normalized = fluid.strip()
        supported_by_lower = {item.lower(): item for item in self.get_supported_fluids()}
        canonical = supported_by_lower.get(normalized.lower())
        if canonical is None:
            raise HeatDissipationError("INVALID_FLUID", "请选择 CoolProp 支持的有效工质")
        return canonical

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

    def get_mass_flow_kg_per_s(
        self,
        flow_rate: UnitValue,
        fluid: str,
        tin_k: float,
        pressure_pa: float,
        row_index: int | None = None,
    ) -> float:
        if flow_rate.unit == FlowRateUnit.KG_PER_S.value:
            return self.convert_flow_rate_to_kg_per_s(flow_rate)
        density_kg_per_m3 = self.get_density_kg_per_m3(fluid, tin_k, pressure_pa, row_index)
        return self.convert_flow_rate_to_kg_per_s(flow_rate, density_kg_per_m3)

    def get_enthalpy_j_per_kg(
        self,
        fluid: str,
        temperature_k: float,
        pressure_pa: float,
        row_index: int | None = None,
    ) -> float:
        try:
            return float(PropsSI("H", "T", temperature_k, "P", pressure_pa, fluid))
        except ValueError as exc:
            if "key" in str(exc).lower() or "fluid" in str(exc).lower():
                raise HeatDissipationError("INVALID_FLUID", "请选择 CoolProp 支持的有效工质", row_index) from exc
            raise HeatDissipationError(
                "PROPERTY_RANGE_ERROR",
                "抱歉，当前温度或压力超出了该工质的物性库数据范围",
                row_index,
            ) from exc

    def get_density_kg_per_m3(
        self,
        fluid: str,
        temperature_k: float,
        pressure_pa: float,
        row_index: int | None = None,
    ) -> float:
        try:
            return float(PropsSI("D", "T", temperature_k, "P", pressure_pa, fluid))
        except ValueError as exc:
            if "key" in str(exc).lower() or "fluid" in str(exc).lower():
                raise HeatDissipationError("INVALID_FLUID", "请选择 CoolProp 支持的有效工质", row_index) from exc
            raise HeatDissipationError(
                "PROPERTY_RANGE_ERROR",
                "抱歉，当前温度或压力超出了该工质的物性库数据范围",
                row_index,
            ) from exc

    def format_q_display(self, q_w: float) -> str:
        if abs(q_w) >= 1000:
            return f"{q_w / 1000:.2f} kW"
        return f"{q_w:.2f} W"
