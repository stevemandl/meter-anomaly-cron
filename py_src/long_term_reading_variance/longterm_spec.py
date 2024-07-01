from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json

actual_testcase = open('python_template/Testcases/actual_testcase.json')
# actual_test case from:
# Swagger JSON request body https://app.swaggerhub.com/apis/Cornell-BACSI/EMCS-portal/1.0.0
#. {
#   "range": {
#     "from": "2023-07-01T19:38:47.334Z",
#     "to": "2023-07-30T19:38:47.334Z"
#   },
#   "interval": "30s",
#   "intervalMs": 5500,
#   "maxDataPoints": 50,
#   "targets": [
#     {
#       "target": "DayHall.Elec.PowerScout3/kWsystem"
#     }
#   ]
# }
noanomaly_testcase = open('python_template/Testcases/noanomaly_testcase.json')
# noanomaly_testcase from:
# Swagger JSON request body https://app.swaggerhub.com/apis/Cornell-BACSI/EMCS-portal/1.0.0
# {
#   "panelId": "Q-1599986187842-0.164611811105138-0",
#   "range": {
#     "from": "2021-03-01T19:38:47.334Z",
#     "to": "2021-03-30T19:38:47.334Z"
#   },
#   "interval": "30s",
#   "intervalMs": 5500,
#   "maxDataPoints": 50,
#   "targets": [
#     {
#       "target": "StatlerHotel.Elec.PowerScout3/kWsystem"
#     }
#   ],
#   "group": "string",
#   "from": "2021-10-20T19:38:47.334Z",
#   "to": "2021-10-21T19:38:47.334Z"
# }

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



def test_actual(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
   
    data = json.load(actual_testcase)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value= data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "missing more than 10%" in result.get("body")


def test_noanomly(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(noanomaly_testcase)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body")
    
def test_onetime(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(noanomaly_testcase)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body")
