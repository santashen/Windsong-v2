import unittest

from fastapi.testclient import TestClient

from main import app


class HeatDissipationApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_calculate_water_single_row(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [{"tinC": 25, "toutC": 35}],
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["unit"], "W")
        self.assertEqual(len(body["results"]), 1)
        self.assertEqual(body["results"][0]["index"], 1)
        self.assertGreater(body["results"][0]["qW"], 0)

    def test_invalid_pressure_returns_business_error(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 0, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [{"tinC": 25, "toutC": 35}],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "INVALID_PRESSURE")
        self.assertEqual(response.json()["detail"]["message"], "压力必须大于 0")

    def test_negative_flow_returns_business_error(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": -0.1, "unit": "kg/s"},
                "rows": [{"tinC": 25, "toutC": 35}],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "INVALID_FLOW_RATE")
        self.assertEqual(response.json()["detail"]["message"], "流量不能为负数")


if __name__ == "__main__":
    unittest.main()
