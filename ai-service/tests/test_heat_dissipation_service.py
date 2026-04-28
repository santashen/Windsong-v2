import unittest

from CoolProp.CoolProp import PropsSI

from models.heat_dissipation import HeatDissipationRequest, TemperatureRowInput, UnitValue
from services.heat_dissipation import HeatDissipationError, HeatDissipationService


class HeatDissipationServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = HeatDissipationService()

    def test_convert_pressure_units_to_pa(self):
        cases = [
            (1, "Pa", 1),
            (101.325, "kPa", 101325),
            (0.101325, "MPa", 101325),
            (1.01325, "bar", 101325),
        ]

        for value, unit, expected in cases:
            with self.subTest(unit=unit):
                pressure = UnitValue(value=value, unit=unit)
                self.assertAlmostEqual(self.service.convert_pressure_to_pa(pressure), expected)

    def test_convert_temperature_c_to_k(self):
        self.assertAlmostEqual(self.service.convert_temperature_c_to_k(25), 298.15)

    def test_convert_flow_units_to_kg_per_s(self):
        self.assertAlmostEqual(
            self.service.convert_flow_rate_to_kg_per_s(UnitValue(value=0.1, unit="kg/s")),
            0.1,
        )
        self.assertAlmostEqual(
            self.service.convert_flow_rate_to_kg_per_s(UnitValue(value=60, unit="L/min"), 1000),
            1.0,
        )
        self.assertAlmostEqual(
            self.service.convert_flow_rate_to_kg_per_s(UnitValue(value=3.6, unit="m3/h"), 1000),
            1.0,
        )
        self.assertAlmostEqual(
            self.service.convert_flow_rate_to_kg_per_s(UnitValue(value=3.6, unit="m³/h"), 1000),
            1.0,
        )

    def test_rejects_invalid_pressure_and_flow(self):
        with self.assertRaises(HeatDissipationError) as pressure_error:
            self.service.convert_pressure_to_pa(UnitValue(value=0, unit="kPa"))
        self.assertEqual(pressure_error.exception.code, "INVALID_PRESSURE")

        with self.assertRaises(HeatDissipationError) as flow_error:
            self.service.convert_flow_rate_to_kg_per_s(UnitValue(value=-1, unit="kg/s"))
        self.assertEqual(flow_error.exception.code, "INVALID_FLOW_RATE")

    def test_validate_request_accepts_minimum_valid_payload(self):
        payload = HeatDissipationRequest(
            fluid="Water",
            pressure=UnitValue(value=101.325, unit="kPa"),
            flowRate=UnitValue(value=0.1, unit="kg/s"),
            rows=[TemperatureRowInput(tinC=25, toutC=35)],
        )

        self.service.validate_request(payload)

    def test_calculate_water_single_row_with_mass_flow(self):
        payload = HeatDissipationRequest(
            fluid="Water",
            pressure=UnitValue(value=101.325, unit="kPa"),
            flowRate=UnitValue(value=0.1, unit="kg/s"),
            rows=[TemperatureRowInput(tinC=25, toutC=35)],
        )

        response = self.service.calculate(payload)
        result = response.results[0]
        expected_q_w = 0.1 * (
            PropsSI("H", "T", 308.15, "P", 101325, "Water")
            - PropsSI("H", "T", 298.15, "P", 101325, "Water")
        )

        self.assertEqual(response.unit, "W")
        self.assertEqual(result.index, 1)
        self.assertAlmostEqual(result.qW, expected_q_w)


if __name__ == "__main__":
    unittest.main()
