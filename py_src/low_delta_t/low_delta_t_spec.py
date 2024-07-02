from low_delta_t.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json

# See swagger docs at https://app.swaggerhub.com/apis/Cornell-BACSI/EMCS-portal/1.0.0

# normal_tons.json contains the response from the following JSON request body:
""" 
{
 "range": {"from": "2023-06-28", "to": "2024-06-27"},
 "targets": [{"target": "BiotechnologyBuilding.CW.FP/TONS", "payload": {"additional": ["aggH"]}}]
}

"""
normal_tons = open("low_delta_t/test_cases/normal_tons.json")
# normal_temps_flows.json contains the response from the following JSON request body:
"""
{
    "range": { "from": "2024-06-25", "to": "2024-06-27" },
    "targets": [
        { "target": "BiotechnologyBuilding.CW.FP/STEMP" },
        { "target": "BiotechnologyBuilding.CW.FP/RTEMP" },
        { "target": "BiotechnologyBuilding.CW.FP/FLOW" },
        { "target": "BiotechnologyBuilding.CW.FP/TONS" },
        { "target": "GameFarmRoadWeatherStation.TAVG_H_F" }
    ]
}
"""
normal_temps_flows = open("low_delta_t/test_cases/normal_temps_flows.json")

# anom_tons.json contains the response from the following JSON request body:
""" 
{
 "range": {"from": "2023-06-28", "to": "2024-06-27"},
 "targets": [{"target": "ClarkHall.CW.FP/TONS", "payload": {"additional": ["aggH"]}}]
}

"""
anom_tons = open("low_delta_t/test_cases/anom_tons.json")

# anom_temps_flows.json contains the response from the following JSON request body:
"""
{
    "range": { "from": "2024-06-25", "to": "2024-06-27" },
    "targets": [
        { "target": "ClarkHall.CW.FP/STEMP" }, 
        { "target": "ClarkHall.CW.FP/RTEMP" },
        { "target": "ClarkHall.CW.FP/FLOW" },
        { "target": "ClarkHall.CW.FP/TONS" },
        { "target": "GameFarmRoadWeatherStation.TAVG_H_F" }
    ]
}
"""
anom_temps_flows = open("low_delta_t/test_cases/anom_temps_flows.json")


def test_handle400(mocker):
    r = Response()
    r.status_code = 400
    r._content = b'{"error":"No data"}'
    mocker.patch("low_delta_t.handler.fetch_trends", side_effect=HTTPError(response=r))
    event = {"body": {"pointName": "foo/TONS"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "no data" in result.get("body")


def test_barf(mocker):
    r = Response()
    r.status_code = 400
    r._content = b"qwerty"
    mocker.patch("low_delta_t.handler.fetch_trends", side_effect=HTTPError(response=r))
    event = {"body": {"pointName": "foo/TONS"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "qwerty" in result.get("body")


def test_normal(mocker):
    event = {
        "body": {
            "pointName": "BiotechnologyBuilding.CW.FP/TONS",
            "timeStamp": "2024-06-27",
        }
    }

    normal_tons_data = json.load(normal_tons)
    normal_temps_flows_data = json.load(normal_temps_flows)
    mocker.patch(
        "low_delta_t.handler.fetch_trends",
        side_effect=[normal_tons_data, normal_temps_flows_data],
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body")


def test_anomaly(mocker):
    event = {
        "body": {
            "pointName": "ClarkHall.CW.FP/TONS",
            "timeStamp": "2024-06-27",
        }
    }
    anom_tons_data = json.load(anom_tons)
    anom_temps_flows_data = json.load(anom_temps_flows)
    mocker.patch(
        "low_delta_t.handler.fetch_trends",
        side_effect=[anom_tons_data, anom_temps_flows_data],
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "ClarkHall.CW.FP/TONS actual_dt" in result.get("body")
