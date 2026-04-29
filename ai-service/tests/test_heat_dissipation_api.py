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

    def test_invalid_fluid_returns_business_error(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "NotAFluid",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [{"tinC": 25, "toutC": 35}],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "INVALID_FLUID")
        self.assertEqual(response.json()["detail"]["message"], "请选择 CoolProp 支持的有效工质")

    def test_empty_rows_returns_business_error(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "INVALID_ROWS")
        self.assertEqual(response.json()["detail"]["message"], "请至少输入一组温度数据")

    def test_too_many_rows_returns_business_error(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [{"tinC": 25, "toutC": 35} for _ in range(501)],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "INVALID_ROWS")

    def test_property_range_error_returns_business_error_with_row_index(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [{"tinC": -300, "toutC": -290}],
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "PROPERTY_RANGE_ERROR")
        self.assertEqual(response.json()["detail"]["message"], "抱歉，当前温度或压力超出了该工质的物性库数据范围")
        self.assertEqual(response.json()["detail"]["rowIndex"], 1)

    def test_calculate_batch_rows(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 0.1, "unit": "kg/s"},
                "rows": [
                    {"tinC": 25, "toutC": 35},
                    {"tinC": 26, "toutC": 36},
                    {"tinC": 27, "toutC": 37},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["results"]), 3)
        self.assertEqual([row["index"] for row in body["results"]], [1, 2, 3])

    def test_calculate_with_volume_flow(self):
        response = self.client.post(
            "/api/heat-dissipation/calculate",
            json={
                "fluid": "Water",
                "pressure": {"value": 101.325, "unit": "kPa"},
                "flowRate": {"value": 60, "unit": "L/min"},
                "rows": [{"tinC": 25, "toutC": 35}],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["results"][0]["qW"], 0)

    def test_search_fluids_by_query(self):
        response = self.client.get("/api/heat-dissipation/fluids", params={"query": "wat"})

        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.json()["items"]]
        self.assertIn("Water", names)

    def test_search_fluids_empty_query_returns_limited_items(self):
        response = self.client.get("/api/heat-dissipation/fluids", params={"limit": 5})

        self.assertEqual(response.status_code, 200)
        items = response.json()["items"]
        self.assertGreater(len(items), 0)
        self.assertLessEqual(len(items), 5)


if __name__ == "__main__":
    unittest.main()
