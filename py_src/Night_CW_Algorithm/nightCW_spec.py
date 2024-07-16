from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json


anom_case = open('Night_CW_Algorithm/Testcases/decrease.json')
"""
decrease.json contains the reponse from the following JSON request body:
{
  "range": {
    "from": "2024-02-01T19:38:47.334Z",
    "to": "2024-05-30T19:38:47.334Z"
  },
  "interval": "30s",
  "intervalMs": 5500,
  "maxDataPoints": 50,
  "targets": [
    {
      "target": "BakerLab.CW.FP/TONS"
    }

  ]
}
"""

noanom_case = open('Night_CW_Algorithm/testcases/increase.json')
"""
increase.json contains the reponse from the following JSON request body:
{
  "range": {
    "from": "2022-03-01 20:06:08",
    "to": "2022-04-04 20:06:08"
  },
   
  "targets": [
    {
      "target": "BiotechnologyBuilding.CW.FP/TONS"
    }
  ]
}
"""
def test_nobarf(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value= [{"datapoints": []}],
    )
    
    result = run(event, None)
    assert "statusCode" in result
    assert "missing more than 10%" in result.get("body")


def test_handle400(mocker):
    r = Response()
    r.status_code = 400
    r._content = b'{"error":"No data"}'
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "no data" in result.get("body")


def test_barf(mocker):
    r = Response()
    r.status_code = 400
    r._content = b"qwerty"
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "qwerty" in result.get("body")




def test_CW_decrease(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(noanom_case)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body")
    
def test_CW_increase(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(anom_case)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "anomoly found" == result.get("body")
